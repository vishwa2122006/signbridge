"""Recognition engine: confidence threshold, temporal stability, NO_HAND,
NO_MODEL, IDLE, and emitting each signed word exactly once."""

from app import config
from app.models.schemas import RecognitionStatus
from app.services.recognition import IDLE_TICKS_FOR_BOUNDARY, RecognitionEngine

WINDOW = {"frames": [], "aspect": 4 / 3}


class FakeModel:
    """Returns a scripted (label, confidence) per call as a full probability
    vector aligned to `labels`."""

    def __init__(self, script, labels):
        self.script = list(script)
        self.labels = list(labels)
        self.calls = 0

    def predict(self, window):
        label, conf = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        other = (1.0 - conf) / (len(self.labels) - 1)
        return [conf if l == label else other for l in self.labels]


def make_engine(script, labels=("help", "OTHER")):
    engine = RecognitionEngine()
    engine.load_model(FakeModel(script, labels), list(labels))
    return engine


def run(engine, ticks, session="s1"):
    return [engine.predict(session, hand_detected=True, window=WINDOW) for _ in range(ticks)]


def test_no_model_is_honest_default():
    result = RecognitionEngine().predict("s1", hand_detected=True, window=WINDOW)
    assert result["status"] == RecognitionStatus.NO_MODEL
    assert result["accepted_sign_id"] is None


def test_no_hand_detected():
    engine = make_engine([("help", 0.95)] * 10)
    assert engine.predict("s1", hand_detected=False, window=WINDOW)["status"] == RecognitionStatus.NO_HAND


def test_low_confidence_is_rejected_not_guessed():
    result = run(make_engine([("help", 0.40)] * 10), 1)[-1]
    assert result["status"] == RecognitionStatus.UNCERTAIN
    assert result["accepted_sign_id"] is None


def test_single_tick_is_not_accepted_even_with_high_confidence():
    result = run(make_engine([("help", 0.95)]), 1)[-1]
    assert result["status"] == RecognitionStatus.UNSTABLE
    assert result["accepted_sign_id"] is None


def test_stable_consistent_predictions_are_accepted():
    result = run(make_engine([("help", 0.95)] * config.STABILITY_WINDOW), config.STABILITY_WINDOW)[-1]
    assert result["status"] == RecognitionStatus.RECOGNIZED
    assert result["accepted_concept"] == "help"
    assert result["english"] == "Help" and result["tamil"] == "உதவி"
    assert result["is_emergency"] is True


def test_flickering_predictions_are_rejected():
    script = [("help", 0.9), ("pain", 0.9), ("water", 0.9), ("help", 0.9), ("doctor", 0.9)]
    engine = make_engine(script, labels=["help", "pain", "water", "doctor", "OTHER"])
    result = run(engine, len(script))[-1]
    assert result["status"] != RecognitionStatus.RECOGNIZED
    assert result["accepted_sign_id"] is None


def test_unknown_class_never_snaps_to_nearest_known_word():
    engine = make_engine([("totally_unmapped_label", 0.95)] * 10, labels=["totally_unmapped_label", "OTHER"])
    result = run(engine, config.STABILITY_WINDOW)[-1]
    assert result["status"] == RecognitionStatus.UNKNOWN_SIGN
    assert result["accepted_sign_id"] is None


def test_session_reset_clears_stability_buffer():
    engine = make_engine([("help", 0.95)] * 20)
    run(engine, config.STABILITY_WINDOW)
    engine.reset_session("s1")
    assert run(engine, 1)[-1]["status"] == RecognitionStatus.UNSTABLE


def test_idle_class_reports_idle():
    engine = make_engine([(config.NONE_LABEL, 0.9)] * 5, labels=[config.NONE_LABEL, "help"])
    result = run(engine, 3)[-1]
    assert result["status"] == RecognitionStatus.IDLE
    assert result["accepted_sign_id"] is None


def test_held_sign_is_emitted_once():
    engine = make_engine([("help", 0.95)] * 20)
    results = run(engine, config.STABILITY_WINDOW + 6)
    assert sum(r["new_word"] for r in results) == 1


def test_same_sign_after_idle_pause_is_emitted_again():
    window = config.STABILITY_WINDOW
    script = ([("help", 0.95)] * window + [(config.NONE_LABEL, 0.9)] * IDLE_TICKS_FOR_BOUNDARY
              + [("help", 0.95)] * (window + 2))
    engine = make_engine(script, labels=[config.NONE_LABEL, "help"])
    results = run(engine, len(script))
    assert sum(r["new_word"] for r in results) == 2


def test_switching_directly_to_another_word_emits_it():
    window = config.STABILITY_WINDOW
    script = [("help", 0.95)] * window + [("water", 0.95)] * (window + 1)
    engine = make_engine(script, labels=["help", "water"])
    emitted = [r["accepted_concept"] for r in run(engine, len(script)) if r["new_word"]]
    assert emitted == ["help", "water"]
