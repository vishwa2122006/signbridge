"""
features.py — turns raw MediaPipe landmark frames into a fixed-length vector.

This is the ONLY place feature engineering happens: live prediction, in-app
training and the offline video importer all call it, so the model always sees
identically prepared input.

Raw frame format (produced by frontend/src/mediapipe.js and ml/import_videos.py):

    {"t": milliseconds,
     "left":  [[x, y, z] * 21] | None,
     "right": [[x, y, z] * 21] | None,
     "pose":  [[x, y, z] * 7]  | None}

x/y are normalized image coordinates (0..1) of the *unmirrored* camera image.
Pose points, in order: nose, left shoulder, right shoulder, left elbow,
right elbow, left wrist, right wrist.
"""

from typing import List, Optional

import numpy as np

FEATURE_VERSION = 1
NUM_HAND_POINTS = 21
NUM_POSE_POINTS = 7
TIME_STEPS = 16
DEFAULT_ASPECT = 4 / 3

# Signs can be recorded from 1.5 to 6 seconds long. Live recognition scores each
# word over about as long as its recordings last: their median length, rounded
# to WINDOW_STEP_MS (see classifier.py).
DEFAULT_WINDOW_MS = 1500
WINDOW_STEP_MS = 500
MIN_WINDOW_MS = 1000

# Per hand: presence flag + 21 wrist-relative points + (x, y, size) relative to the body.
PER_HAND = 1 + NUM_HAND_POINTS * 3 + 3
PER_FRAME = 2 * PER_HAND
MOTION_FEATURES = 2 * 5
VECTOR_SIZE = TIME_STEPS * PER_FRAME + MOTION_FEATURES

# MediaPipe regularly loses a hand for a frame or two mid-sign; carry it forward.
MAX_GAP_FILL = 3

_HAND_KEYS = ("left", "right")
_POSE_MIRROR_ORDER = [0, 2, 1, 4, 3, 6, 5]


def _points(value, n: int) -> Optional[np.ndarray]:
    if value is None:
        return None
    arr = np.asarray(value, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[0] != n or arr.shape[1] < 3:
        return None
    return arr[:, :3]


def _to_arrays(frames: List[dict]):
    n = len(frames)
    hands = np.zeros((n, 2, NUM_HAND_POINTS, 3), dtype=np.float32)
    present = np.zeros((n, 2), dtype=bool)
    pose = np.zeros((n, NUM_POSE_POINTS, 3), dtype=np.float32)
    pose_present = np.zeros(n, dtype=bool)
    t = np.zeros(n, dtype=np.float64)
    for i, frame in enumerate(frames):
        ts = frame.get("t")
        t[i] = float(ts) if ts is not None else i * 33.0
        for h, key in enumerate(_HAND_KEYS):
            pts = _points(frame.get(key), NUM_HAND_POINTS)
            if pts is not None:
                hands[i, h] = pts
                present[i, h] = True
        pts = _points(frame.get("pose"), NUM_POSE_POINTS)
        if pts is not None:
            pose[i] = pts
            pose_present[i] = True
    order = np.argsort(t, kind="stable")
    return hands[order], present[order], pose[order], pose_present[order], t[order]


def _fill_gaps(values: np.ndarray, present: np.ndarray, max_gap: int):
    """In place: copies the last seen value into up to `max_gap` following missing frames."""
    seen = present.copy()
    last, gap = None, 0
    for i in range(len(seen)):
        if seen[i]:
            last, gap = i, 0
        elif last is not None and gap < max_gap:
            gap += 1
            values[i] = values[last]
            present[i] = True


def _sample_indices(t: np.ndarray, steps: int) -> np.ndarray:
    """Nearest frame to `steps` evenly spaced timestamps, so clips recorded at
    different frame rates produce the same number of steps over the same time."""
    n = len(t)
    if n == 1:
        return np.zeros(steps, dtype=int)
    if t[-1] - t[0] <= 0:
        return np.linspace(0, n - 1, steps).round().astype(int)
    targets = np.linspace(t[0], t[-1], steps)
    idx = np.clip(np.searchsorted(t, targets), 1, n - 1)
    left_closer = (targets - t[idx - 1]) <= (t[idx] - targets)
    return np.where(left_closer, idx - 1, idx)


def frame_matrix(frames: List[dict], aspect: float = DEFAULT_ASPECT, steps: int = TIME_STEPS) -> np.ndarray:
    """(steps, PER_FRAME) matrix of normalized per-frame features."""
    out = np.zeros((steps, PER_FRAME), dtype=np.float32)
    if not frames:
        return out

    hands, present, pose, pose_present, t = _to_arrays(frames)
    for h in range(2):
        _fill_gaps(hands[:, h], present[:, h], MAX_GAP_FILL)
    _fill_gaps(pose, pose_present, len(frames))

    idx = _sample_indices(t, steps)
    hands, present, pose, pose_present = hands[idx], present[idx], pose[idx], pose_present[idx]

    # Undo the non-square frame so angles and distances are true to life.
    hands[..., 0] *= aspect
    pose[..., 0] *= aspect

    for s in range(steps):
        center, width = np.array([0.5 * aspect, 0.5, 0.0], dtype=np.float32), 0.35
        if pose_present[s]:
            shoulder_width = float(np.linalg.norm(pose[s, 1, :2] - pose[s, 2, :2]))
            if shoulder_width > 1e-3:
                center, width = (pose[s, 1] + pose[s, 2]) / 2, shoulder_width

        for h in range(2):
            if not present[s, h]:
                continue
            pts = hands[s, h]
            wrist = pts[0]
            size = max(float(np.linalg.norm(pts[9, :2] - wrist[:2])), 1e-4)  # wrist -> middle knuckle
            base = h * PER_HAND
            out[s, base] = 1.0
            out[s, base + 1:base + 64] = ((pts - wrist) / size).reshape(-1)
            out[s, base + 64] = (wrist[0] - center[0]) / width
            out[s, base + 65] = (wrist[1] - center[1]) / width
            out[s, base + 66] = size / width  # rough distance-to-camera cue
    return out


def clip_vector(frames: List[dict], aspect: float = DEFAULT_ASPECT) -> np.ndarray:
    """Fixed-length vector for one clip / live window: the flattened frame
    matrix plus per-hand motion statistics."""
    matrix = frame_matrix(frames, aspect)
    motion = []
    for h in range(2):
        base = h * PER_HAND
        pres = matrix[:, base]
        pos = matrix[:, base + 64:base + 66]
        both = (pres[1:] * pres[:-1])[:, None]
        delta = np.diff(pos, axis=0) * both
        motion.extend([np.abs(delta).mean(axis=0), delta.std(axis=0), [pres.mean()]])
    return np.concatenate([matrix.reshape(-1)] + [np.asarray(m, dtype=np.float32).ravel() for m in motion])


def clip_duration_ms(frames: List[dict]) -> int:
    """Time from the first to the last frame."""
    times = [f["t"] for f in frames if f.get("t") is not None]
    return int(round(max(times) - min(times))) if len(times) >= 2 else 0


def window_ms(durations_ms: List[float]) -> int:
    """The live window for a word: the median length of its recordings, rounded to WINDOW_STEP_MS."""
    if len(durations_ms) == 0:
        return DEFAULT_WINDOW_MS
    median = float(np.median(durations_ms))
    return int(max(MIN_WINDOW_MS, round(median / WINDOW_STEP_MS) * WINDOW_STEP_MS))


def has_hands(frames: List[dict]) -> bool:
    return any(f.get("left") is not None or f.get("right") is not None for f in frames)


def _flip(points):
    if points is None:
        return None
    return [[1.0 - p[0], p[1], p[2]] for p in points]


def mirror(frames: List[dict]) -> List[dict]:
    """Horizontally mirrored copy (left and right swapped). Used as training
    augmentation so a sign recorded right-handed is also learned left-handed."""
    out = []
    for frame in frames:
        pose = _flip(frame.get("pose"))
        if pose is not None and len(pose) == NUM_POSE_POINTS:
            pose = [pose[i] for i in _POSE_MIRROR_ORDER]
        out.append({
            "t": frame.get("t"),
            "left": _flip(frame.get("right")),
            "right": _flip(frame.get("left")),
            "pose": pose,
        })
    return out


def jitter(frames: List[dict], rng: np.random.Generator) -> List[dict]:
    """Label-preserving random distortion for training augmentation: shifted
    window start/end (live windows never line up exactly with a sign), hand
    placement, small wrist rotation and landmark noise."""
    n = len(frames)
    if n >= 8:
        max_crop = max(1, int(n * 0.15))
        start = int(rng.integers(0, max_crop + 1))
        end = n - int(rng.integers(0, max_crop + 1))
        frames = frames[start:max(end, start + 5)]

    angle = rng.normal(0.0, np.radians(8))
    cos, sin = np.cos(angle), np.sin(angle)
    shifts = {key: rng.normal(0.0, 0.02, size=2) for key in _HAND_KEYS}

    out = []
    for frame in frames:
        jittered = {"t": frame.get("t"), "pose": frame.get("pose")}
        for key in _HAND_KEYS:
            pts = _points(frame.get(key), NUM_HAND_POINTS)
            if pts is None:
                jittered[key] = None
                continue
            pts = pts.copy()
            wrist = pts[0, :2].copy()
            rel = pts[:, :2] - wrist
            pts[:, 0] = wrist[0] + rel[:, 0] * cos - rel[:, 1] * sin + shifts[key][0]
            pts[:, 1] = wrist[1] + rel[:, 0] * sin + rel[:, 1] * cos + shifts[key][1]
            pts += rng.normal(0.0, 0.002, size=pts.shape)
            jittered[key] = pts.tolist()
        out.append(jittered)
    return out
