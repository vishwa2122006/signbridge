"""Tests for the safety-critical recognition engine: confidence threshold,
temporal stability, NO_HAND, and the honest NO_MODEL default."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.recognition import RecognitionEngine, MIN_CONFIDENCE_THRESHOLD, STABILITY_WINDOW
from app.models.schemas import RecognitionStatus


class FakeModel:
    """Deterministic fake model for testing the engine logic in isolation
    (not for demoing real recognition - see DEMO_MODE notes in the README).
    Builds a full probability vector aligned to `labels`, so the intended
    label actually ends up as the top prediction on each call."""
    def __init__(self, script, labels):
        # script: list of (label, confidence) to return on successive calls
        self.script = list(script)
        self.labels = list(labels)
        self.calls = 0

    def predict(self, window_features):
        label, conf = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        n_others = len(self.labels) - 1
        other_conf = (1.0 - conf) / n_others if n_others > 0 else 0.0
        return [conf if l == label else other_conf for l in self.labels]


def make_engine_with_script(script, labels=("help", "OTHER")):
    engine = RecognitionEngine()
    engine.load_model(FakeModel(script, labels), list(labels))
    return engine


def test_no_model_is_honest_default():
    engine = RecognitionEngine()  # nothing loaded
    result = engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    assert result["status"] == RecognitionStatus.NO_MODEL
    assert result["accepted_sign_id"] is None


def test_no_hand_detected():
    engine = make_engine_with_script([("help", 0.95)] * 10)
    result = engine.predict("s1", hand_detected=False, window_features=[[0.0] * 126])
    assert result["status"] == RecognitionStatus.NO_HAND


def test_low_confidence_is_rejected_not_guessed():
    engine = make_engine_with_script([("help", 0.40)] * 10)
    result = engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    assert result["status"] == RecognitionStatus.UNCERTAIN
    assert result["accepted_sign_id"] is None
    assert result["confidence"] != 0.40 or result["accepted_sign_id"] is None


def test_single_tick_is_not_accepted_even_with_high_confidence():
    """A single high-confidence frame must NOT be enough - stability window required."""
    engine = make_engine_with_script([("help", 0.95)])
    result = engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    assert result["status"] in (RecognitionStatus.UNSTABLE,)
    assert result["accepted_sign_id"] is None


def test_stable_consistent_predictions_are_accepted():
    """HELP HELP HELP HELP HELP -> accept (matches the spec's worked example)."""
    engine = make_engine_with_script([("help", 0.95)] * STABILITY_WINDOW, labels=("help", "OTHER"))
    result = None
    for _ in range(STABILITY_WINDOW):
        result = engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    assert result["status"] == RecognitionStatus.RECOGNIZED
    assert result["accepted_concept"] == "help"


def test_flickering_predictions_are_rejected():
    """HELP PAIN WATER HELP DOCTOR -> reject (matches the spec's worked example)."""
    script = [("help", 0.9), ("pain", 0.9), ("water", 0.9), ("help", 0.9), ("doctor", 0.9)]
    labels = ["help", "pain", "water", "doctor", "OTHER"]
    engine = RecognitionEngine()
    engine.load_model(FakeModel(script, labels), labels)
    result = None
    for _ in range(len(script)):
        result = engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    assert result["status"] != RecognitionStatus.RECOGNIZED
    assert result["accepted_sign_id"] is None


def test_unknown_class_never_snaps_to_nearest_known_word():
    """A model predicting a label with no vocabulary entry must surface as
    UNKNOWN_SIGN, never silently mapped to the closest known concept."""
    script = [("totally_unmapped_label", 0.95)] * STABILITY_WINDOW
    labels = ["totally_unmapped_label", "OTHER"]
    engine = RecognitionEngine()
    engine.load_model(FakeModel(script, labels), labels)
    result = None
    for _ in range(STABILITY_WINDOW):
        result = engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    assert result["status"] == RecognitionStatus.UNKNOWN_SIGN
    assert result["accepted_sign_id"] is None


def test_session_reset_clears_stability_buffer():
    engine = make_engine_with_script([("help", 0.95)] * 20, labels=("help", "OTHER"))
    for _ in range(STABILITY_WINDOW):
        engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    engine.reset_session("s1")
    result = engine.predict("s1", hand_detected=True, window_features=[[0.0] * 126])
    assert result["status"] == RecognitionStatus.UNSTABLE
