"""Loads the trained model from disk and exposes the interface the
RecognitionEngine expects: predict(window) -> probabilities aligned to labels.

Words can be recorded at different lengths (1.5 to 6 seconds). The live
window covers the longest word, and each word is scored on the end of that
window cut to its own length, so a quick sign isn't diluted by seconds of
other movement and a slow sign is seen whole."""

import json
import logging
import os
from typing import Dict, List, Optional

import joblib
import numpy as np

from app import config
from app.ml import features

MODEL_FILE = "model.joblib"
META_FILE = "model_meta.json"

# A word is only scored once the live window covers this share of its length
# (the shortest words are always scored).
MIN_WINDOW_FILL = 0.8

log = logging.getLogger(__name__)


class SignClassifier:
    def __init__(self, estimator, labels: List[str], meta: Optional[dict] = None,
                 window_ms: Optional[Dict[str, int]] = None):
        self.estimator = estimator
        self.labels = list(labels)
        self.meta = meta or {}
        groups: Dict[int, List[int]] = {}
        for i, label in enumerate(self.labels):
            groups.setdefault(int((window_ms or {}).get(label, features.DEFAULT_WINDOW_MS)), []).append(i)
        self._groups = [(ms, np.array(groups[ms])) for ms in sorted(groups)]  # shortest first

    @property
    def max_window_ms(self) -> int:
        return self._groups[-1][0] if self._groups else features.DEFAULT_WINDOW_MS

    @classmethod
    def load(cls, model_dir: Optional[str] = None) -> Optional["SignClassifier"]:
        model_dir = model_dir or config.model_dir()
        path = os.path.join(model_dir, MODEL_FILE)
        if not os.path.exists(path):
            return None
        bundle = joblib.load(path)
        if bundle.get("feature_version") != features.FEATURE_VERSION:
            log.warning("Ignoring %s: trained with feature version %s, current is %s - retrain.",
                        path, bundle.get("feature_version"), features.FEATURE_VERSION)
            return None
        meta = {}
        meta_path = os.path.join(model_dir, META_FILE)
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
        return cls(bundle["estimator"], bundle["labels"], meta, bundle.get("window_ms"))

    def predict(self, window: dict) -> np.ndarray:
        """window = {"frames": [raw frame, ...], "aspect": width / height}: the last few seconds of camera frames."""
        frames = window["frames"]
        aspect = window.get("aspect") or features.DEFAULT_ASPECT
        probs = np.zeros(len(self.labels))
        if not frames:
            return probs
        times = [f.get("t") or 0.0 for f in frames]
        end, seen = times[-1], times[-1] - times[0]
        for i, (ms, indices) in enumerate(self._groups):
            if i > 0 and seen < ms * MIN_WINDOW_FILL:
                continue  # the camera hasn't seen enough of this word's length yet
            crop = [frame for frame, t in zip(frames, times) if t >= end - ms]
            scores = self.estimator.predict_proba(features.clip_vector(crop, aspect)[None, :])[0]
            probs[indices] = scores[indices]
        return probs
