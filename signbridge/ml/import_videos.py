"""
import_videos.py — turns sign videos (e.g. a public dataset) into training
samples, in exactly the format the Teach Signs page records.

Runs the same MediaPipe hand + pose models the browser uses over every
video, keeps only landmark coordinates, and saves one sample per video to the
database, already approved (running this script counts as an admin's review).
Afterwards train from the app (Review -> Train model) or with
`python ml/train.py`, then restart the backend.

Folder layouts:
    default:  <data_dir>/<concept>/<signer>/<video>.mp4
    --flat:   <data_dir>/<concept>/<video>.mp4        (signer name from --signer)

Folder names must be vocabulary concept slugs (see the Vocabulary page; use
`_none` for idle clips), or be mapped with --map: a CSV with columns
folder,concept,english,tamil,category. A mapped concept that isn't in the
vocabulary yet is added as a custom word using the given English and Tamil.

Usage (from the signbridge/ folder, with the backend venv active):
    pip install -r ml/requirements.txt
    python ml/import_videos.py --data_dir dataset/raw
    python ml/import_videos.py --data_dir ~/Downloads/tsl --flat --signer kaggle --map tsl_map.csv
"""

import argparse
import csv
import os
import sys
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

import cv2  # noqa: E402
import mediapipe as mp  # noqa: E402
from mediapipe.tasks.python import BaseOptions, vision  # noqa: E402

from app import config  # noqa: E402
from app.ml.features import has_hands  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.db import init_db, session_scope  # noqa: E402
from app.errors import ApiError  # noqa: E402
from app.models.tables import APPROVED, Word  # noqa: E402
from app.services import sample_store  # noqa: E402
from app.services.vocabulary import add_word, slugify, vocabulary  # noqa: E402

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_URLS = {
    "hand": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
    "pose": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
}
POSE_INDICES = [0, 11, 12, 13, 14, 15, 16]  # must match frontend/src/mediapipe.js
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm")
MAX_FPS = 30
MIN_HAND_FRAMES = 5


def ensure_models() -> dict:
    os.makedirs(MODELS_DIR, exist_ok=True)
    paths = {}
    for name, url in MODEL_URLS.items():
        path = os.path.join(MODELS_DIR, os.path.basename(url))
        if not os.path.exists(path):
            print(f"Downloading {os.path.basename(url)} ...")
            urllib.request.urlretrieve(url, path + ".part")
            os.replace(path + ".part", path)
        paths[name] = path
    return paths


def to_points(landmarks):
    return [[round(float(p.x), 4), round(float(p.y), 4), round(float(p.z), 4)] for p in landmarks]


def assign_hands(hand_landmarks, handedness) -> dict:
    """Same rule as assignHands() in frontend/src/mediapipe.js."""
    hands = []
    for i, landmarks in enumerate(hand_landmarks[:2]):
        is_left = i < len(handedness) and handedness[i] and handedness[i][0].category_name == "Left"
        hands.append([landmarks, "Left" if is_left else "Right"])
    if len(hands) == 2 and hands[0][1] == hands[1][1]:
        right = 0 if hands[0][0][0].x >= hands[1][0][0].x else 1
        hands[right][1], hands[1 - right][1] = "Right", "Left"
    slots = {"left": None, "right": None}
    for landmarks, label in hands:
        slots["left" if label == "Left" else "right"] = to_points(landmarks)
    return slots


class Extractor:
    def __init__(self, models: dict):
        self.hands = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=models["hand"]),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
        ))
        self.pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=models["pose"]),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
        ))
        self.clock = 0  # VIDEO mode needs increasing timestamps across all videos

    def frames(self, path: str):
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise IOError("cannot open video")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, round(fps / MAX_FPS))
        frames, aspect, index, last_ms = [], None, -1, -1.0
        try:
            while True:
                ok, bgr = cap.read()
                if not ok:
                    break
                index += 1
                if index % step:
                    continue
                ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                if ms <= last_ms:  # some containers don't report positions
                    ms = last_ms + 1000.0 / fps * step
                last_ms = ms
                if aspect is None:
                    height, width = bgr.shape[:2]
                    aspect = width / height

                ts = max(self.clock, int(ms) + self.clock)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
                hand_result = self.hands.detect_for_video(image, ts)
                pose_result = self.pose.detect_for_video(image, ts)
                pose = None
                if pose_result.pose_landmarks:
                    pose = to_points([pose_result.pose_landmarks[0][i] for i in POSE_INDICES])
                frames.append({"t": round(ms, 1), **assign_hands(hand_result.hand_landmarks, hand_result.handedness),
                               "pose": pose})
        finally:
            cap.release()
        self.clock += int(last_ms) + 1000
        return frames, aspect or 4 / 3


def trim(frames):
    """Drops the frames before the first and after the last detected hand."""
    with_hands = [i for i, f in enumerate(frames) if f["left"] is not None or f["right"] is not None]
    return frames[with_hands[0]:with_hands[-1] + 1] if with_hands else []


def load_map(path):
    with open(path, encoding="utf-8", newline="") as f:
        return {row["folder"]: row for row in csv.DictReader(f)}


def resolve_concept(folder, mapping):
    entry = (mapping or {}).get(folder)
    concept = (entry.get("concept") or "").strip() if entry else folder
    if concept == config.NONE_LABEL or vocabulary.get_by_concept(concept):
        return concept
    if entry and entry.get("english") and entry.get("tamil"):
        try:
            with session_scope() as db:
                word = add_word(db, entry["english"], entry["tamil"], entry.get("category") or "CUSTOM")
                print(f"  + added custom word '{word.concept}' ({word.english} / {word.tamil})")
            vocabulary.reload()
            return word.concept
        except ApiError:  # already in the vocabulary, or proposed and waiting for review
            existing = slugify(entry["english"])
            return existing if vocabulary.get_by_concept(existing) else None
    return None


def iter_videos(data_dir, flat, signer):
    for folder in sorted(os.listdir(data_dir)):
        folder_path = os.path.join(data_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        if flat:
            for name in sorted(os.listdir(folder_path)):
                if name.lower().endswith(VIDEO_EXTENSIONS):
                    yield folder, signer, os.path.join(folder_path, name)
            continue
        for signer_dir in sorted(os.listdir(folder_path)):
            signer_path = os.path.join(folder_path, signer_dir)
            if not os.path.isdir(signer_path):
                if signer_dir.lower().endswith(VIDEO_EXTENSIONS):
                    print(f"  ! {folder}/{signer_dir}: videos must be inside a signer folder (or use --flat)")
                continue
            for name in sorted(os.listdir(signer_path)):
                if name.lower().endswith(VIDEO_EXTENSIONS):
                    yield folder, signer_dir, os.path.join(signer_path, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data_dir", required=True)
    parser.add_argument("--flat", action="store_true", help="videos directly inside each concept folder")
    parser.add_argument("--signer", default="dataset", help="signer name for --flat layouts")
    parser.add_argument("--map", help="CSV mapping dataset folders to concepts")
    parser.add_argument("--source", help="label stored with each sample (default: import:<data_dir name>)")
    args = parser.parse_args()
    init_db()

    data_dir = os.path.abspath(os.path.expanduser(args.data_dir))
    source = args.source or f"import:{os.path.basename(data_dir)}"
    mapping = load_map(args.map) if args.map else None
    extractor = Extractor(ensure_models())

    resolved, imported, skipped, unknown = {}, Counter(), Counter(), []
    for folder, signer, path in iter_videos(data_dir, args.flat, args.signer):
        if folder not in resolved:
            resolved[folder] = resolve_concept(folder, mapping)
            if resolved[folder] is None:
                unknown.append(folder)
        concept = resolved[folder]
        if concept is None:
            continue

        try:
            frames, aspect = extractor.frames(path)
        except Exception as e:  # a single broken file shouldn't stop a large import
            print(f"  ! {path}: {e}")
            skipped[concept] += 1
            continue
        frames = trim(frames)
        hand_frames = sum(1 for f in frames if f["left"] is not None or f["right"] is not None)
        if concept != config.NONE_LABEL and (not has_hands(frames) or hand_frames < MIN_HAND_FRAMES):
            print(f"  ! {os.path.relpath(path, data_dir)}: no hands detected - skipped")
            skipped[concept] += 1
            continue

        with session_scope() as db:
            word = None if concept == config.NONE_LABEL else db.scalar(select(Word).where(Word.concept == concept))
            sample_store.save_sample(db, word, frames, aspect, status=APPROVED, signer_id=signer,
                                     source=f"{source}:{os.path.relpath(path, data_dir)}")
        imported[concept] += 1
        print(f"  {concept:<22} {signer:<16} {len(frames):>4} frames  {os.path.basename(path)}")

    print(f"\nImported {sum(imported.values())} approved samples for {len(imported)} words into the database")
    for concept, n in sorted(imported.items()):
        print(f"  {concept:<22} {n}")
    if skipped:
        print(f"Skipped {sum(skipped.values())} videos (unreadable or no hands).")
    if unknown:
        print(f"Unknown folders (not in the vocabulary and not mapped): {', '.join(unknown)}\n"
              "  -> add them on the Teach Signs page, or map them with --map.")
    if imported:
        print("\nNext: train with `python ml/train.py` (or Train model on the Review page), then restart the backend.")


if __name__ == "__main__":
    main()
