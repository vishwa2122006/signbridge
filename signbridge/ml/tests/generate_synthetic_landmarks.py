"""
generate_synthetic_landmarks.py — TEST FIXTURE ONLY.

Generates a fake landmarks.npz with clearly separable per-class patterns
and multiple synthetic signers, purely so train_classifier.py's CODE PATH
(signer-based split, training loop, metrics reporting, model export) can be
exercised and verified without real video data.

This produces NO real sign data and must never be used to claim a working
Tamil Sign Language model. It only proves the training pipeline runs
correctly end-to-end and computes its metrics correctly.
"""

import numpy as np

SEQ_LEN = 30
NUM_FEATURES = 126
CONCEPTS = ["help", "pain", "water", "doctor", "yes"]
SIGNERS_PER_CONCEPT = 5
CLIPS_PER_SIGNER = 4


def main(out_path="synthetic_landmarks.npz", seed=0):
    rng = np.random.RandomState(seed)
    X, y, signer_ids = [], [], []

    for ci, concept in enumerate(CONCEPTS):
        # Give each concept a distinct base pattern so the classifier has a
        # real (if trivial) signal to learn - this is a code-correctness
        # fixture, not an attempt to simulate real hand motion.
        base_pattern = np.sin(np.linspace(0, (ci + 1) * np.pi, SEQ_LEN))[:, None] * (ci + 1) * 0.1

        for signer_idx in range(SIGNERS_PER_CONCEPT):
            signer_id = f"synth_signer_{signer_idx:02d}"
            signer_noise_bias = rng.normal(0, 0.02, size=(1, NUM_FEATURES))
            for _clip in range(CLIPS_PER_SIGNER):
                seq = base_pattern @ np.ones((1, NUM_FEATURES)) + signer_noise_bias
                seq = seq + rng.normal(0, 0.05, size=(SEQ_LEN, NUM_FEATURES))
                X.append(seq.astype(np.float32))
                y.append(concept)
                signer_ids.append(signer_id)

    X = np.array(X, dtype=np.float32)
    y = np.array(y)
    signer_ids = np.array(signer_ids)
    np.savez_compressed(out_path, X=X, y=y, signer_ids=signer_ids)
    print(f"Wrote synthetic fixture: X={X.shape}, {len(CONCEPTS)} concepts, "
          f"{SIGNERS_PER_CONCEPT} signers/concept -> {out_path}")


if __name__ == "__main__":
    main()
