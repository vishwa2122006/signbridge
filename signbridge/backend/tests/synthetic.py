"""Synthetic landmark clips for tests: simple geometric hands in the raw frame
format. NOT real sign data - only used to check the pipeline end to end."""

import numpy as np

NONE_LABEL = "_none"

# finger curl (thumb..pinky, 0 = straight, 1 = curled), wrist offset from the
# shoulder centre in shoulder widths, sideways wave amplitude, both hands?
SHAPES = {
    "hello": {"curl": [0, 0, 0, 0, 0], "offset": (0.6, -1.3), "wave": 0.25, "two_hands": False},
    "water": {"curl": [1, 0, 0, 1, 1], "offset": (0.1, -0.8), "wave": 0.0, "two_hands": False},
    "thumbs_up": {"curl": [0, 1, 1, 1, 1], "offset": (0.3, 0.2), "wave": 0.0, "two_hands": False},
    "pain": {"curl": [1, 0, 1, 1, 1], "offset": (0.5, 0.3), "wave": 0.0, "two_hands": True},
}


def hand_points(curl, wrist, size, angle, rng, noise=0.003):
    pts = np.zeros((21, 3))
    pts[0, :2] = wrist
    fan = np.radians([-45, -15, 0, 15, 30])
    for f in range(5):
        a = angle + fan[f]
        base = 1 + 4 * f
        pts[base, :2] = wrist + np.array([np.sin(a), -np.cos(a)]) * size * (0.5 if f else 0.3)
        bend = -1 if f == 0 else 1
        for j in range(1, 4):
            b = a + bend * curl[f] * np.radians(60) * j
            pts[base + j, :2] = pts[base + j - 1, :2] + np.array([np.sin(b), -np.cos(b)]) * size * 0.28
    pts[:, :2] += rng.normal(0, noise, (21, 2))
    pts[:, 2] = rng.normal(0, 0.005, 21)
    return pts


def make_clip(word, signer, rng, n_frames=45, fps=30.0):
    body = np.random.default_rng(1000 + signer)  # consistent body shape per signer
    width = 0.22 * (1.0 + body.normal(0, 0.08))
    centre = np.array([0.5, 0.62]) + body.normal(0, 0.03, 2)
    tilt = body.normal(0, 0.08)
    pose = np.array([
        [centre[0], centre[1] - 0.9 * width, 0],                    # nose
        [centre[0] + width / 2, centre[1], 0],                      # left shoulder
        [centre[0] - width / 2, centre[1], 0],                      # right shoulder
        [centre[0] + 0.7 * width, centre[1] + 0.8 * width, 0],      # left elbow
        [centre[0] - 0.7 * width, centre[1] + 0.8 * width, 0],      # right elbow
        [centre[0] + 0.6 * width, centre[1] + 1.4 * width, 0],      # left wrist
        [centre[0] - 0.6 * width, centre[1] + 1.4 * width, 0],      # right wrist
    ])
    shape = SHAPES.get(word)
    resting_hand_visible = rng.random() < 0.5
    t0 = float(rng.uniform(0, 1e5))

    frames = []
    for i in range(n_frames):
        frame = {
            "t": t0 + i * 1000.0 / fps,
            "left": None,
            "right": None,
            "pose": (pose + rng.normal(0, 0.002, pose.shape)).tolist(),
        }
        if shape is None:
            if resting_hand_visible:
                wrist = centre + np.array([-0.5, 1.6]) * width
                frame["right"] = hand_points([0.5] * 5, wrist, 0.35 * width, np.pi, rng).tolist()
        else:
            wave = shape["wave"] * np.sin(2 * np.pi * 2 * i / n_frames)
            dx, dy = shape["offset"][0] + wave, shape["offset"][1]
            wrist = centre + np.array([-dx, dy]) * width
            frame["right"] = hand_points(shape["curl"], wrist, 0.35 * width, tilt + rng.normal(0, 0.02), rng).tolist()
            if shape["two_hands"]:
                wrist = centre + np.array([dx, dy]) * width
                frame["left"] = hand_points(shape["curl"], wrist, 0.35 * width, -tilt, rng).tolist()
        frames.append(frame)
    return frames
