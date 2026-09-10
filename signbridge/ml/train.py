"""
train.py — trains the sign classifier from the command line.

Same as Review -> Train model in the app: uses every approved recording in
the database and writes dataset/models/. A running backend loads the
new model on restart (the in-app Train button hot-swaps it instead).

Usage (from the signbridge/ folder, with the backend venv active):
    python ml/train.py
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from app import config  # noqa: E402
from app.ml import trainer  # noqa: E402


def pct(value):
    return "n/a" if value is None else f"{value:.1%}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model_dir", default=None, help=f"default: {config.model_dir()}")
    args = parser.parse_args()

    try:
        meta = trainer.train_and_save(model_dir=args.model_dir)
    except trainer.NotEnoughDataError as e:
        sys.exit(f"Not enough data: {e}")

    print(f"Model: {meta['model_type']}  ({meta['num_samples']} samples, {meta['num_signers']} signers, "
          f"{meta['training_seconds']} s)")
    print(f"Accuracy ({meta['cv_method']} cross-validation): {pct(meta['cv_accuracy'])}")
    for name, accuracy in meta["candidate_accuracy"].items():
        print(f"  {name:<22} {pct(accuracy)}")
    print(f"At confidence >= {meta['confidence_threshold']}: answers {pct(meta['accepted_rate'])} of signs, "
          f"{pct(meta['precision_at_threshold'])} of those correct")

    if meta["per_word"]:
        print(f"\n{'word':<24}{'precision':>10}{'recall':>8}{'f1':>7}{'samples':>9}")
        for w in meta["per_word"]:
            print(f"{w['concept']:<24}{w['precision']:>10.2f}{w['recall']:>8.2f}{w['f1']:>7.2f}{w['samples']:>9}")
    for warning in meta["warnings"]:
        print(f"\nWARNING: {warning}")
    print(f"\nSaved to {args.model_dir or config.model_dir()}")


if __name__ == "__main__":
    main()
