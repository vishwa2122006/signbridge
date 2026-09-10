"""
recognition.py — the safety-critical core of SignBridge.

Design rules enforced here (from the project spec, non-negotiable):
  1. Never force a prediction. Low confidence -> reject, don't guess.
  2. Never accept a single-frame/single-tick prediction. Require temporal
     stability across a rolling window of recent ticks.
  3. Unknown gestures must surface as UNKNOWN, never snapped to the
     nearest known class.
  4. No hand detected is its own explicit state, not silence.
  5. If no trained/validated model is loaded, the honest default is
     NO_MODEL on every call - the system must not pretend to recognize
     signs it was never actually trained to recognize.

This module intentionally ships WITHOUT a trained model file. Wire in a
real one (see ml/train_classifier.py) only once it was trained on data
that is at least Category B in DATASET_SOURCES.md - never on invented or
relabeled data.
"""

import collections
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from app.models.schemas import RecognitionStatus, RecognitionCandidate
from app.services.vocabulary import vocabulary

MIN_CONFIDENCE_THRESHOLD = float(os.environ.get("SIGNBRIDGE_MIN_CONFIDENCE", "0.70"))
STABILITY_WINDOW = int(os.environ.get("SIGNBRIDGE_STABILITY_WINDOW", "5"))   # last N ticks
STABILITY_RATIO = float(os.environ.get("SIGNBRIDGE_STABILITY_RATIO", "0.80"))  # 80% must agree
SESSION_TTL_SECONDS = 600


@dataclass
class _SessionState:
    ticks: collections.deque = field(default_factory=lambda: collections.deque(maxlen=STABILITY_WINDOW))
    last_seen: float = field(default_factory=time.time)
    last_confirmed_sign_id: Optional[str] = None


class RecognitionEngine:
    """Wraps an optional trained model. With no model loaded, every call
    honestly reports NO_MODEL instead of fabricating a result."""

    def __init__(self):
        self.model = None          # set by load_model() once a real model exists
        self.model_metadata = {}   # e.g. {"trained_on": "...", "signer_split": "...", "test_f1": ...}
        self._sessions: Dict[str, _SessionState] = {}

    def load_model(self, model, labels: List[str], metadata: Optional[dict] = None):
        """Attach a real trained model. `model.predict(window) -> np.ndarray of
        class probabilities` is the expected interface (matches the Keras
        model produced by ml/train_classifier.py)."""
        self.model = model
        self.labels = labels
        self.model_metadata = metadata or {}

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    def _get_session(self, session_id: str) -> _SessionState:
        self._gc_sessions()
        if session_id not in self._sessions:
            self._sessions[session_id] = _SessionState()
        st = self._sessions[session_id]
        st.last_seen = time.time()
        return st

    def _gc_sessions(self):
        now = time.time()
        stale = [sid for sid, st in self._sessions.items() if now - st.last_seen > SESSION_TTL_SECONDS]
        for sid in stale:
            del self._sessions[sid]

    def reset_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    def _raw_predict(self, window_features) -> Tuple[Optional[str], float, List[Tuple[str, float]]]:
        """Runs the actual model. Returns (top_label_or_None, top_confidence, all_candidates)."""
        if not self.model_loaded:
            return None, 0.0, []
        probs = self.model.predict(window_features)  # expected: 1D array aligned with self.labels
        ranked = sorted(zip(self.labels, probs), key=lambda x: x[1], reverse=True)
        top_label, top_conf = ranked[0]
        return top_label, float(top_conf), [(l, float(c)) for l, c in ranked[:3]]

    def predict(self, session_id: str, hand_detected: bool, window_features) -> dict:
        """Main entry point. Returns a plain dict the router turns into a
        PredictResponse. Every branch is explicit - nothing falls through to
        a silent guess."""
        session = self._get_session(session_id)

        if not hand_detected:
            session.ticks.clear()
            return self._result(RecognitionStatus.NO_HAND, session_id)

        if not self.model_loaded:
            # Honest default: we have landmark data flowing correctly (proving
            # the pipeline works end-to-end) but no validated model to classify
            # it with yet. This is expected in the delivered prototype until a
            # real model is trained on Category A/B data and wired in.
            return self._result(RecognitionStatus.NO_MODEL, session_id)

        top_label, top_conf, candidates = self._raw_predict(window_features)

        if top_label is None or top_conf < MIN_CONFIDENCE_THRESHOLD:
            session.ticks.append(None)  # low-confidence tick still counts against stability
            return self._result(
                RecognitionStatus.UNCERTAIN, session_id,
                candidates=[RecognitionCandidate(sign_id=l, concept=l, confidence=c) for l, c in candidates],
            )

        session.ticks.append(top_label)

        if len(session.ticks) < STABILITY_WINDOW:
            return self._result(
                RecognitionStatus.UNSTABLE, session_id,
                candidates=[RecognitionCandidate(sign_id=l, concept=l, confidence=c) for l, c in candidates],
            )

        non_null = [t for t in session.ticks if t is not None]
        if not non_null:
            return self._result(RecognitionStatus.UNCERTAIN, session_id)

        most_common_label, most_common_count = collections.Counter(non_null).most_common(1)[0]
        agreement_ratio = most_common_count / len(session.ticks)

        if agreement_ratio < STABILITY_RATIO:
            return self._result(
                RecognitionStatus.UNSTABLE, session_id,
                candidates=[RecognitionCandidate(sign_id=l, concept=l, confidence=c) for l, c in candidates],
            )

        row = vocabulary.get_by_concept(most_common_label) or vocabulary.get(most_common_label)
        if row is None:
            # The model predicted a class we have no vocabulary entry for at
            # all - treat as unknown rather than exposing a raw label.
            return self._result(RecognitionStatus.UNKNOWN_SIGN, session_id)

        session.last_confirmed_sign_id = row["sign_id"]
        return self._result(
            RecognitionStatus.RECOGNIZED, session_id,
            row=row, confidence=top_conf,
            candidates=[RecognitionCandidate(sign_id=l, concept=l, confidence=c) for l, c in candidates],
        )

    def _result(self, status: RecognitionStatus, session_id: str, row: Optional[dict] = None,
                confidence: Optional[float] = None,
                candidates: Optional[List[RecognitionCandidate]] = None) -> dict:
        messages = {
            RecognitionStatus.NO_HAND: (
                "Position your hands inside the camera area.",
                "உங்கள் கைகளை கேமரா பகுதிக்குள் வையுங்கள்.",
            ),
            RecognitionStatus.NO_MODEL: (
                "No validated sign-recognition model is loaded yet. "
                "The camera and landmark pipeline are working - train and "
                "load a model to enable recognition.",
                "இன்னும் சரிபார்க்கப்பட்ட அடையாள மொழி மாதிரி இல்லை. "
                "கேமரா இயங்குகிறது.",
            ),
            RecognitionStatus.UNCERTAIN: (
                "Sign unclear - please repeat.",
                "அடையாளம் தெளிவாக இல்லை - மீண்டும் காட்டவும்.",
            ),
            RecognitionStatus.UNSTABLE: (
                "Hold the sign steady...",
                "அடையாளத்தை நிலையாக வைக்கவும்...",
            ),
            RecognitionStatus.UNKNOWN_SIGN: (
                "I don't recognize this sign yet. Please repeat or use text input.",
                "இந்த அடையாளம் எனக்குத் தெரியாது. மீண்டும் முயற்சிக்கவும் அல்லது "
                "உரையை பயன்படுத்தவும்.",
            ),
            RecognitionStatus.RECOGNIZED: (
                f"Detected: {row['english']}" if row else "Detected.",
                f"கண்டறியப்பட்டது: {row['tamil']}" if row else "கண்டறியப்பட்டது.",
            ),
        }
        msg_en, msg_ta = messages[status]

        return {
            "status": status,
            "session_id": session_id,
            "simulated": False,
            "accepted_sign_id": row["sign_id"] if row else None,
            "accepted_concept": row["concept"] if row else None,
            "english": row["english"] if row else None,
            "tamil": row["tamil"] if row else None,
            "confidence": confidence,
            "top_candidates": candidates or [],
            "message_en": msg_en,
            "message_ta": msg_ta,
            "is_emergency": bool(row and vocabulary.is_emergency(row["concept"])),
        }


engine = RecognitionEngine()
