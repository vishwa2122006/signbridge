"""Loads the trained model from disk and exposes the interface the
RecognitionEngine expects: predict(window) -> probabilities aligned to labels."""

import json
import logging
import os
from typing import List, Optional

import joblib
import numpy as np

from app import config
from app.ml import features

MODEL_FILE = "model.joblib"
META_FILE = "model_meta.json"

log = logging.getLogger(__name__)


class SignClassifier:
    def __init__(self, estimator, labels: List[str], meta: Optional[dict] = None):
        self.estimator = estimator
        self.labels = list(labels)
        self.meta = meta or {}

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
        return cls(bundle["estimator"], bundle["labels"], meta)

    def predict(self, window: dict) -> np.ndarray:
        """window = {"frames": [raw frame, ...], "aspect": width / height}"""
        vector = features.clip_vector(window["frames"], window.get("aspect") or features.DEFAULT_ASPECT)
        return self.estimator.predict_proba(vector[None, :])[0]
