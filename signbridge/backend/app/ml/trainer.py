"""
trainer.py — trains the sign classifier from approved landmark recordings.

Small-data friendly by design: tens of clips per word recorded in the app is
the expected input, so this uses scikit-learn on engineered features
(features.py) instead of a deep sequence model, and trains on CPU in seconds.

Evaluation is explicit about what it measures: with 3+ signers,
cross-validation holds out whole signers ("does it work for a new person?");
otherwise it falls back to a stratified split and warns that the number is
optimistic for new signers.
"""

import json
import os
import time
from collections import Counter
from typing import List, Optional

import joblib
import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from app import config
from app.ml import features
from app.ml.classifier import META_FILE, MODEL_FILE
from app.services import sample_store

MIN_SAMPLES_PER_WORD = 5
MAX_CV_SPLITS = 4
JITTER_COPIES = 2
SVM_MAX_ROWS = 5000  # probability-calibrated SVC gets slow beyond this
PCA_COMPONENTS = 64


class NotEnoughDataError(ValueError):
    def __init__(self, message: str, counts: dict):
        super().__init__(message)
        self.counts = counts


def _candidates(n_rows: int) -> dict:
    # PCA first: on the raw ~2k features logistic regression takes ~20x longer for the same accuracy.
    pca_components = max(1, min(PCA_COMPONENTS, n_rows - 1))
    models = {
        "logistic_regression": make_pipeline(
            StandardScaler(), PCA(n_components=pca_components, random_state=0), LogisticRegression(C=1.0, max_iter=2000)
        ),
        "extra_trees": ExtraTreesClassifier(n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=0),
    }
    if n_rows <= SVM_MAX_ROWS:
        models["svm"] = make_pipeline(
            StandardScaler(),
            SVC(C=10.0, gamma="scale", probability=True, class_weight="balanced", random_state=0),
        )
    return models


def _build_rows(samples: List[dict], seed: int = 0):
    """Feature rows for every sample plus its augmentations. `origin` maps each
    row back to its sample so cross-validation never trains on an augmented
    copy of a test clip; `is_original` marks the unaugmented rows."""
    rng = np.random.default_rng(seed)
    X, y, origin, is_original = [], [], [], []
    for i, sample in enumerate(samples):
        aspect = sample.get("aspect") or features.DEFAULT_ASPECT
        frames = sample["frames"]
        mirrored = features.mirror(frames)
        variants = [frames, mirrored] + [
            features.jitter(frames if k % 2 == 0 else mirrored, rng) for k in range(JITTER_COPIES)
        ]
        for v, variant in enumerate(variants):
            X.append(features.clip_vector(variant, aspect))
            y.append(sample["concept"])
            origin.append(i)
            is_original.append(v == 0)
    return np.stack(X), np.array(y), np.array(origin), np.array(is_original)


def _splits(labels: np.ndarray, signers: np.ndarray):
    unique_signers = set(signers.tolist())
    if len(unique_signers) >= 3:
        splitter = GroupKFold(n_splits=min(MAX_CV_SPLITS, len(unique_signers)))
        return "signer-held-out", list(splitter.split(np.zeros(len(labels)), labels, signers))
    min_count = min(Counter(labels.tolist()).values())
    if min_count >= 2:
        splitter = StratifiedKFold(n_splits=min(MAX_CV_SPLITS, min_count), shuffle=True, random_state=0)
        return "stratified", list(splitter.split(np.zeros(len(labels)), labels))
    return None, []


def _cross_validate(name, X, y, origin, is_original, n_samples, splits):
    """Out-of-fold predictions for every original sample."""
    predicted = np.empty(n_samples, dtype=object)
    confidence = np.zeros(n_samples)
    evaluated = np.zeros(n_samples, dtype=bool)
    for train_idx, test_idx in splits:
        train_rows = np.isin(origin, train_idx)
        test_rows = np.isin(origin, test_idx) & is_original
        if len(set(y[train_rows].tolist())) < 2 or not test_rows.any():
            continue
        estimator = _candidates(int(train_rows.sum()))[name].fit(X[train_rows], y[train_rows])
        probs = estimator.predict_proba(X[test_rows])
        rows = origin[test_rows]
        predicted[rows] = estimator.classes_[probs.argmax(axis=1)]
        confidence[rows] = probs.max(axis=1)
        evaluated[rows] = True
    return predicted, confidence, evaluated


def train_and_save(samples: Optional[List[dict]] = None, model_dir: Optional[str] = None) -> dict:
    """Trains on `samples` (default: every approved recording in the database) and saves the model."""
    model_dir = model_dir or config.model_dir()
    started = time.time()

    all_samples = sample_store.training_samples() if samples is None else samples
    counts = Counter(s["concept"] for s in all_samples)
    usable = {c for c, n in counts.items() if n >= MIN_SAMPLES_PER_WORD}
    skipped = sorted(c for c in counts if c not in usable)
    if not (usable - {config.NONE_LABEL}) or len(usable) < 2:
        current = ", ".join(f"{concept} {n}" for concept, n in sorted(counts.items())) or "none approved yet"
        raise NotEnoughDataError(
            f"Not enough approved recordings to train yet: approve at least {MIN_SAMPLES_PER_WORD} recordings "
            f"for each of at least 2 signs (Idle counts as one). Current: {current}.",
            dict(counts),
        )

    samples = [s for s in all_samples if s["concept"] in usable]
    sample_labels = np.array([s["concept"] for s in samples])
    sample_signers = np.array([s.get("signer_id", "unknown") for s in samples])
    X, y, origin, is_original = _build_rows(samples)

    cv_method, splits = _splits(sample_labels, sample_signers)
    candidate_accuracy, best_name, best_oof = {}, "logistic_regression", None
    for name in _candidates(len(X)):
        if not splits:
            break
        predicted, confidence, evaluated = _cross_validate(name, X, y, origin, is_original, len(samples), splits)
        if not evaluated.any():
            continue
        accuracy = float((predicted[evaluated] == sample_labels[evaluated]).mean())
        candidate_accuracy[name] = round(accuracy, 4)
        if best_oof is None or accuracy > candidate_accuracy[best_name]:
            best_name, best_oof = name, (predicted, confidence, evaluated)

    estimator = _candidates(len(X))[best_name].fit(X, y)

    labels = sorted(usable)
    # `warnings` is readable text for the CLI; `warning_codes` lets the app show them in Tamil or English.
    warnings, warning_codes = [], []
    per_word, accepted_rate, precision_at_threshold, cv_accuracy = [], None, None, None
    if best_oof is not None:
        predicted, confidence, evaluated = best_oof
        truth, preds = sample_labels[evaluated], predicted[evaluated].astype(str)
        cv_accuracy = candidate_accuracy[best_name]
        report = classification_report(truth, preds, labels=labels, output_dict=True, zero_division=0)
        per_word = [
            {
                "concept": c,
                "precision": round(report[c]["precision"], 3),
                "recall": round(report[c]["recall"], 3),
                "f1": round(report[c]["f1-score"], 3),
                "samples": int(counts[c]),
            }
            for c in labels
        ]
        accepted = confidence[evaluated] >= config.MIN_CONFIDENCE
        accepted_rate = round(float(accepted.mean()), 3)
        if accepted.any():
            precision_at_threshold = round(float((truth[accepted] == preds[accepted]).mean()), 3)
    else:
        warnings.append("Not enough samples to cross-validate, so accuracy could not be measured.")
        warning_codes.append({"code": "no_cv"})

    num_signers = len(set(sample_signers.tolist()))
    if cv_method == "stratified":
        warnings.append(
            f"Only {num_signers} signer(s): accuracy was measured on the same people the model was "
            "trained on and will be lower for new signers. Record 3+ signers for an honest number."
        )
        warning_codes.append({"code": "few_signers", "signers": num_signers})
    if config.NONE_LABEL not in usable:
        warnings.append(
            "No idle ('no sign') samples: record some so the translator stays quiet while your hands rest."
        )
        warning_codes.append({"code": "no_idle"})
    if skipped:
        warnings.append(f"Skipped (fewer than {MIN_SAMPLES_PER_WORD} samples): {', '.join(skipped)}.")
        warning_codes.append({"code": "skipped", "words": skipped, "min_samples": MIN_SAMPLES_PER_WORD})

    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, MODEL_FILE)
    joblib.dump(
        {"estimator": estimator, "labels": list(estimator.classes_),
         "feature_version": features.FEATURE_VERSION, "time_steps": features.TIME_STEPS},
        model_path + ".tmp",
    )
    os.replace(model_path + ".tmp", model_path)

    meta = {
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "training_seconds": round(time.time() - started, 1),
        "model_type": best_name,
        "labels": labels,
        "words": [c for c in labels if c != config.NONE_LABEL],
        "has_idle_class": config.NONE_LABEL in usable,
        "num_samples": len(samples),
        "num_signers": num_signers,
        "cv_method": cv_method,
        "cv_accuracy": cv_accuracy,
        "candidate_accuracy": candidate_accuracy,
        "per_word": per_word,
        "confidence_threshold": config.MIN_CONFIDENCE,
        "accepted_rate": accepted_rate,
        "precision_at_threshold": precision_at_threshold,
        "skipped_words": skipped,
        "warnings": warnings,
        "warning_codes": warning_codes,
    }
    with open(os.path.join(model_dir, META_FILE), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta
