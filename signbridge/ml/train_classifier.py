"""
train_classifier.py

Trains an LSTM classifier on the landmark sequences from extract_landmarks.py,
using a SIGNER-BASED split (never a random frame/clip split, which leaks
information and inflates accuracy - the model must be tested on a signer it
has never seen during training).

Reports precision, recall, F1, a full confusion matrix, and per-class
performance - not just overall accuracy. Also reports confidence-threshold
rejection behavior, matching the backend's MIN_CONFIDENCE_THRESHOLD, so you
can see the real tradeoff between "signs accepted" and "signs correct" at
the threshold the live system will actually use.

Usage:
    pip install tensorflow scikit-learn numpy
    python train_classifier.py --data landmarks.npz --out sign_model.keras --confidence_threshold 0.70
"""

import argparse
import json
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras import layers, models


def signer_based_split(signer_ids, y, val_frac=0.15, test_frac=0.20, seed=42):
    """Splits by SIGNER, not by sample. All of one signer's clips go
    entirely into train, val, or test - never split across sets. This is
    what makes the reported accuracy mean 'generalizes to a new person'
    rather than 'memorized this person's hand'."""
    rng = np.random.RandomState(seed)
    unique_signers = sorted(set(signer_ids))
    rng.shuffle(unique_signers)

    n = len(unique_signers)
    n_test = max(1, int(round(n * test_frac))) if n >= 3 else 0
    n_val = max(1, int(round(n * val_frac))) if n - n_test >= 2 else 0

    test_signers = set(unique_signers[:n_test])
    val_signers = set(unique_signers[n_test:n_test + n_val])
    train_signers = set(unique_signers[n_test + n_val:])

    if not train_signers:
        # Too few signers to hold anything out - fall back to using
        # everyone for training and warn loudly. This is a real limitation,
        # not something to paper over.
        print("\n*** WARNING: too few distinct signers to hold any out for "
              "validation/test. Reported metrics below will be optimistic - "
              "they do NOT demonstrate generalization to a new signer. "
              "Collect more signers before trusting these numbers. ***\n")
        train_signers = set(unique_signers)
        val_signers = set()
        test_signers = set()

    def mask_for(signers):
        return np.array([s in signers for s in signer_ids])

    return mask_for(train_signers), mask_for(val_signers), mask_for(test_signers), {
        "train_signers": sorted(train_signers),
        "val_signers": sorted(val_signers),
        "test_signers": sorted(test_signers),
    }


def build_model(seq_len, num_features, num_classes):
    model = models.Sequential([
        layers.Input(shape=(seq_len, num_features)),
        layers.Masking(mask_value=0.0),
        layers.LSTM(64, return_sequences=True),
        layers.Dropout(0.3),
        layers.LSTM(32),
        layers.Dropout(0.3),
        layers.Dense(32, activation="relu"),
        layers.Dense(num_classes, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def rejection_report(y_true, probs, classes, threshold):
    """At the given confidence threshold: how many test predictions would be
    ACCEPTED (max prob >= threshold) vs REJECTED (shown as UNCERTAIN
    instead), and of the accepted ones, what fraction are actually correct.
    This is the number that matters for a system that must never force a
    wrong answer."""
    max_probs = probs.max(axis=1)
    pred_idx = probs.argmax(axis=1)
    accepted = max_probs >= threshold
    n_total = len(y_true)
    n_accepted = int(accepted.sum())
    n_rejected = n_total - n_accepted
    if n_accepted > 0:
        correct_among_accepted = int((pred_idx[accepted] == y_true[accepted]).sum())
        precision_at_threshold = correct_among_accepted / n_accepted
    else:
        correct_among_accepted = 0
        precision_at_threshold = float("nan")

    print(f"\n--- Confidence-threshold rejection report (threshold={threshold}) ---")
    print(f"  Total test samples:      {n_total}")
    print(f"  Accepted (would answer): {n_accepted} ({100 * n_accepted / max(n_total, 1):.1f}%)")
    print(f"  Rejected (UNCERTAIN):    {n_rejected} ({100 * n_rejected / max(n_total, 1):.1f}%)")
    print(f"  Correct among accepted:  {correct_among_accepted}/{n_accepted}"
          f" (precision-at-threshold = {precision_at_threshold:.3f})" if n_accepted else "  n/a")
    print("  This is the tradeoff that matters for the live system: raising the "
          "threshold rejects more signs but is safer per answer given.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default="sign_model.keras")
    parser.add_argument("--labels_out", default="labels.json")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--confidence_threshold", type=float, default=0.70,
                         help="Should match SIGNBRIDGE_MIN_CONFIDENCE in the backend")
    args = parser.parse_args()

    data = np.load(args.data, allow_pickle=True)
    X, y_raw, signer_ids = data["X"], data["y"], data["signer_ids"]

    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    num_classes = len(le.classes_)
    print(f"Loaded X={X.shape}, {num_classes} classes: {list(le.classes_)}")
    print(f"Distinct signers: {len(set(signer_ids))}")

    train_mask, val_mask, test_mask, split_info = signer_based_split(signer_ids, y)
    print(f"Split by signer -> train: {split_info['train_signers']}, "
          f"val: {split_info['val_signers']}, test: {split_info['test_signers']}")

    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = (X[val_mask], y[val_mask]) if val_mask.any() else (None, None)
    X_test, y_test = (X[test_mask], y[test_mask]) if test_mask.any() else (None, None)

    model = build_model(X.shape[1], X.shape[2], num_classes)
    model.summary()

    fit_kwargs = dict(epochs=args.epochs, batch_size=args.batch_size)
    if X_val is not None and len(X_val) > 0:
        fit_kwargs["validation_data"] = (X_val, y_val)
        fit_kwargs["callbacks"] = [tf.keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True)]
    else:
        print("No held-out validation signers available - training without early stopping.")

    model.fit(X_train, y_train, **fit_kwargs)

    if X_test is not None and len(X_test) > 0:
        loss, acc = model.evaluate(X_test, y_test)
        print(f"\nTest accuracy (held-out signers): {acc * 100:.2f}%")

        probs = model.predict(X_test)
        y_pred = np.argmax(probs, axis=1)

        print("\nClassification report (precision / recall / F1 per class):")
        print(classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0))
        print("Confusion matrix (rows=true, cols=predicted):")
        print(confusion_matrix(y_test, y_pred))

        rejection_report(y_test, probs, le.classes_, args.confidence_threshold)
    else:
        print("\n*** No held-out test signers - cannot report a meaningful test "
              "accuracy. Collect at least 3 signers per concept before trusting "
              "any accuracy number for this model. ***")

    model.save(args.out)
    with open(args.labels_out, "w", encoding="utf-8") as f:
        json.dump(list(le.classes_), f, ensure_ascii=False, indent=2)
    print(f"\nSaved model to {args.out} and label map to {args.labels_out}")


if __name__ == "__main__":
    main()
