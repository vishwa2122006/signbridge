"""
extract_landmarks.py

Extracts MediaPipe hand-landmark sequences from a video dataset organized as:

    dataset/raw/
        sign_concept_1/
            signer_001/
                video_001.mp4
            signer_002/
                video_001.mp4
        sign_concept_2/
            ...

Folder name at the top level = concept slug (must match `concept` in
backend/app/data/sign_metadata.csv). The signer subfolder is REQUIRED, not
optional - it is what makes a signer-based train/test split possible later,
which is the only way to honestly test whether the model generalizes to a
person it has never seen (see train_classifier.py).

Produces landmarks.npz with:
    X          : (num_samples, seq_len, num_features)
    y          : (num_samples,)          -- concept slug per sample
    signer_ids : (num_samples,)          -- signer folder name per sample

Usage:
    pip install mediapipe opencv-python numpy
    python extract_landmarks.py --data_dir dataset/raw --out landmarks.npz --seq_len 30
"""

import os
import argparse
import numpy as np
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands

NUM_LANDMARKS = 21
COORDS = 3
MAX_HANDS = 2
NUM_FEATURES = NUM_LANDMARKS * COORDS * MAX_HANDS


def extract_frame_features(results):
    features = np.zeros(NUM_FEATURES, dtype=np.float32)
    if results.multi_hand_landmarks:
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks[:MAX_HANDS]):
            base = hand_idx * NUM_LANDMARKS * COORDS
            for i, lm in enumerate(hand_landmarks.landmark):
                offset = base + i * COORDS
                features[offset] = lm.x
                features[offset + 1] = lm.y
                features[offset + 2] = lm.z
    return features


def sample_indices(total_frames, seq_len):
    if total_frames <= 0:
        return np.zeros(seq_len, dtype=int)
    if total_frames >= seq_len:
        return np.linspace(0, total_frames - 1, seq_len).astype(int)
    idx = list(range(total_frames)) + [total_frames - 1] * (seq_len - total_frames)
    return np.array(idx)


def process_video(video_path, hands, seq_len):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    wanted = set(sample_indices(total_frames, seq_len).tolist())

    frame_features = {}
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx in wanted:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            frame_features[frame_idx] = extract_frame_features(results)
        frame_idx += 1
    cap.release()

    ordered = sample_indices(total_frames, seq_len)
    seq = np.array(
        [frame_features.get(i, np.zeros(NUM_FEATURES, dtype=np.float32)) for i in ordered],
        dtype=np.float32,
    )
    if len(seq) < seq_len:
        pad = np.zeros((seq_len - len(seq), NUM_FEATURES), dtype=np.float32)
        seq = np.vstack([seq, pad]) if len(seq) else pad
    return seq[:seq_len]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True,
                         help="Path to dataset/raw (one subfolder per concept, each containing signer subfolders)")
    parser.add_argument("--out", default="landmarks.npz")
    parser.add_argument("--seq_len", type=int, default=30)
    args = parser.parse_args()

    X, y, signer_ids = [], [], []

    with mp_hands.Hands(
        static_image_mode=False, max_num_hands=MAX_HANDS,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
    ) as hands:
        concepts = sorted(d for d in os.listdir(args.data_dir) if os.path.isdir(os.path.join(args.data_dir, d)))
        print(f"Found {len(concepts)} concept folders: {concepts}")

        for concept in concepts:
            concept_dir = os.path.join(args.data_dir, concept)
            signer_dirs = sorted(d for d in os.listdir(concept_dir) if os.path.isdir(os.path.join(concept_dir, d)))
            if not signer_dirs:
                print(f"  WARNING: {concept} has no signer subfolders - skipping. "
                      f"Expected dataset/raw/{concept}/signer_XXX/video.mp4")
                continue
            for signer in signer_dirs:
                signer_dir = os.path.join(concept_dir, signer)
                videos = [f for f in os.listdir(signer_dir) if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
                print(f"  {concept}/{signer}: {len(videos)} videos")
                for vid in videos:
                    path = os.path.join(signer_dir, vid)
                    seq = process_video(path, hands, args.seq_len)
                    X.append(seq)
                    y.append(concept)
                    signer_ids.append(signer)

    if not X:
        print("\nNo videos found. Populate dataset/raw/<concept>/<signer_id>/*.mp4 first - "
              "see dataset/raw/README.md.")
        return

    X = np.array(X, dtype=np.float32)
    y = np.array(y)
    signer_ids = np.array(signer_ids)

    unique_signers_per_concept = {c: len(set(signer_ids[y == c])) for c in set(y)}
    low_signer_concepts = [c for c, n in unique_signers_per_concept.items() if n < 2]
    if low_signer_concepts:
        print(f"\nWARNING: these concepts have fewer than 2 distinct signers, so a "
              f"signer-held-out split isn't meaningful for them yet: {low_signer_concepts}")

    print(f"\nExtracted dataset shape: X={X.shape}, y={y.shape}, signers={len(set(signer_ids))} unique")
    np.savez_compressed(args.out, X=X, y=y, signer_ids=signer_ids)
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
