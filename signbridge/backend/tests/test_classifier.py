"""Words recorded at different lengths: each is scored on the end of the live
window cut to its own length."""

import numpy as np

from app.ml import classifier as classifier_module
from app.ml import features
from app.ml.classifier import SignClassifier

FRAME_MS = 33.0


class ScriptedEstimator:
    """Returns the next scripted probability row for each call."""

    def __init__(self, rows):
        self.rows = list(rows)

    def predict_proba(self, X):
        return np.array([self.rows.pop(0)])


def window(seconds):
    return {"frames": [{"t": 1000 + i * FRAME_MS} for i in range(int(seconds * 1000 / FRAME_MS))], "aspect": 4 / 3}


def test_each_word_is_scored_on_its_own_length(monkeypatch):
    crops = []
    monkeypatch.setattr(features, "clip_vector", lambda frames, aspect: crops.append(frames) or np.zeros(3))
    # labels: long (3 s), short (1.5 s); scored shortest first
    model = SignClassifier(ScriptedEstimator([[0.1, 0.9], [0.8, 0.2]]), ["long", "short"],
                           window_ms={"long": 3000, "short": 1500})
    assert model.max_window_ms == 3000

    probs = model.predict(window(3.2))
    assert [round((c[-1]["t"] - c[0]["t"]) / 100) for c in crops] == [15, 30]  # 1.5 s crop, then 3 s crop
    assert probs.tolist() == [0.8, 0.9]  # "long" from the 3 s crop, "short" from the 1.5 s crop


def test_long_words_wait_until_enough_has_been_seen(monkeypatch):
    monkeypatch.setattr(features, "clip_vector", lambda frames, aspect: np.zeros(3))
    model = SignClassifier(ScriptedEstimator([[0.3, 0.7]]), ["long", "short"], window_ms={"long": 5000, "short": 1500})
    assert model.predict(window(2)).tolist() == [0.0, 0.7]


def test_models_without_lengths_use_one_window():
    assert classifier_module.MIN_WINDOW_FILL < 1
    model = SignClassifier(ScriptedEstimator([[0.4, 0.6]]), ["a", "b"])
    assert model.max_window_ms == features.DEFAULT_WINDOW_MS


def test_window_is_the_rounded_median_recording_length():
    assert features.window_ms([1470, 1480, 1510]) == 1500
    assert features.window_ms([2900, 3100, 3050, 6000]) == 3000
    assert features.window_ms([400, 500]) == features.MIN_WINDOW_MS
    assert features.window_ms([]) == features.DEFAULT_WINDOW_MS
    assert features.clip_duration_ms([{"t": 10}, {"t": 5010}]) == 5000
