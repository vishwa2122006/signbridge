"""
recognition.py — turns a stream of classifier outputs into accepted words.

Rules enforced here:
  1. Never force a prediction: below the confidence threshold -> UNCERTAIN.
  2. Never accept a single tick: the same word must win most of the last
     STABILITY_WINDOW ticks.
  3. A label with no vocabulary entry surfaces as UNKNOWN_SIGN, never
     snapped to the nearest known word.
  4. No hands in view (NO_HAND) and resting hands (IDLE, the model's
     "_none" class) are explicit states. They also mark the boundary between
     words: a word held steady is emitted once (new_word=True on the first
     acceptance only), the same word signed again after a pause is emitted again.
  5. With no trained model loaded every call returns NO_MODEL.
"""

import collections
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from app import config
from app.models.schemas import RecognitionCandidate, RecognitionStatus
from app.services.vocabulary import vocabulary

SESSION_TTL_SECONDS = 600
# Consecutive IDLE ticks (~250 ms each) that separate two signings of the same word.
IDLE_TICKS_FOR_BOUNDARY = 2


@dataclass
class _SessionState:
    ticks: collections.deque = field(default_factory=lambda: collections.deque(maxlen=config.STABILITY_WINDOW))
    last_seen: float = field(default_factory=time.time)
    last_word: Optional[str] = None
    idle_ticks: int = IDLE_TICKS_FOR_BOUNDARY


class RecognitionEngine:
    def __init__(self):
        self.model = None
        self.labels: List[str] = []
        self.model_metadata: dict = {}
        self._sessions: Dict[str, _SessionState] = {}

    def load_model(self, model, labels: List[str], metadata: Optional[dict] = None):
        """`model.predict(window) -> probabilities aligned with labels`."""
        self.model = model
        self.labels = list(labels)
        self.model_metadata = metadata or {}
        self._sessions.clear()

    def load_classifier(self, classifier, model_id: Optional[int] = None):
        meta = {**classifier.meta, "model_id": model_id} if model_id is not None else classifier.meta
        self.load_model(classifier, classifier.labels, meta)

    def unload(self):
        """No trained model: every prediction returns NO_MODEL."""
        self.load_model(None, [], {})

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    def _get_session(self, session_id: str) -> _SessionState:
        now = time.time()
        for sid in [s for s, st in self._sessions.items() if now - st.last_seen > SESSION_TTL_SECONDS]:
            del self._sessions[sid]
        session = self._sessions.setdefault(session_id, _SessionState())
        session.last_seen = now
        return session

    def reset_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    def _raw_predict(self, window) -> List[Tuple[str, float]]:
        probs = self.model.predict(window)
        return sorted(((label, float(p)) for label, p in zip(self.labels, probs)), key=lambda x: x[1], reverse=True)

    def best_match(self, clip) -> Optional[Tuple[str, float]]:
        """The model's best (label, confidence) for a whole recording, or None without a model."""
        if not self.model_loaded:
            return None
        predict = getattr(self.model, "predict_clip", self.model.predict)
        label, confidence = max(zip(self.labels, predict(clip)), key=lambda pair: pair[1])
        return label, float(confidence)

    @staticmethod
    def _candidates(ranked: List[Tuple[str, float]]) -> List[RecognitionCandidate]:
        out = []
        for label, conf in ranked[:3]:
            row = vocabulary.get_by_concept(label)
            out.append(RecognitionCandidate(sign_id=row["sign_id"] if row else label, concept=label, confidence=conf))
        return out

    def predict(self, session_id: str, hand_detected: bool, window) -> dict:
        session = self._get_session(session_id)

        if not hand_detected:
            session.ticks.clear()
            session.idle_ticks = IDLE_TICKS_FOR_BOUNDARY
            return self._result(RecognitionStatus.NO_HAND, session_id)

        if not self.model_loaded:
            return self._result(RecognitionStatus.NO_MODEL, session_id)

        ranked = self._raw_predict(window)
        candidates = self._candidates(ranked)
        top_label, top_conf = ranked[0]

        if top_label == config.NONE_LABEL:
            session.ticks.append(None)
            session.idle_ticks += 1
            return self._result(RecognitionStatus.IDLE, session_id, candidates=candidates)

        if top_conf < config.MIN_CONFIDENCE:
            session.ticks.append(None)  # low-confidence tick still counts against stability
            return self._result(RecognitionStatus.UNCERTAIN, session_id, candidates=candidates)

        session.ticks.append(top_label)
        if len(session.ticks) < config.STABILITY_WINDOW:
            return self._result(RecognitionStatus.UNSTABLE, session_id, candidates=candidates)

        non_null = [t for t in session.ticks if t is not None]
        label, count = collections.Counter(non_null).most_common(1)[0]
        if count / len(session.ticks) < config.STABILITY_RATIO:
            return self._result(RecognitionStatus.UNSTABLE, session_id, candidates=candidates)

        row = vocabulary.get_by_concept(label)
        if row is None:
            return self._result(RecognitionStatus.UNKNOWN_SIGN, session_id, candidates=candidates)

        new_word = label != session.last_word or session.idle_ticks >= IDLE_TICKS_FOR_BOUNDARY
        session.last_word = label
        session.idle_ticks = 0
        confidence = dict(ranked).get(label, top_conf)
        return self._result(RecognitionStatus.RECOGNIZED, session_id, row=row, confidence=confidence,
                            candidates=candidates, new_word=new_word)

    def _result(self, status: RecognitionStatus, session_id: str, row: Optional[dict] = None,
                confidence: Optional[float] = None,
                candidates: Optional[List[RecognitionCandidate]] = None,
                new_word: bool = False) -> dict:
        messages = {
            RecognitionStatus.NO_HAND: (
                "Show your hands to the camera.",
                "உங்கள் கைகளை கேமராவில் காட்டுங்கள்.",
            ),
            RecognitionStatus.NO_MODEL: (
                "No trained model yet. Trainers record signs; an admin reviews them and trains the model.",
                "இன்னும் பயிற்சி பெற்ற மாதிரி இல்லை. பயிற்சியாளர்கள் சைகைகளைப் பதிவு செய்கிறார்கள்; நிர்வாகி அவற்றைச் சரிபார்த்து மாதிரிக்குப் பயிற்சி அளிக்கிறார்.",
            ),
            RecognitionStatus.IDLE: (
                "Ready - sign a word.",
                "தயார் - ஒரு சைகையைக் காட்டுங்கள்.",
            ),
            RecognitionStatus.UNCERTAIN: (
                "Sign unclear - please repeat.",
                "சைகை தெளிவாக இல்லை - மீண்டும் காட்டவும்.",
            ),
            RecognitionStatus.UNSTABLE: (
                "Hold the sign steady...",
                "சைகையை நிலையாக வைக்கவும்...",
            ),
            RecognitionStatus.UNKNOWN_SIGN: (
                "This sign isn't in the vocabulary. Please repeat or use text.",
                "இந்த சைகை சொல்லகராதியில் இல்லை. மீண்டும் முயற்சிக்கவும் அல்லது உரையைப் பயன்படுத்தவும்.",
            ),
            RecognitionStatus.RECOGNIZED: (
                f"Detected: {row['english']}" if row else "Detected.",
                f"கண்டறியப்பட்டது: {row['tamil']}" if row else "கண்டறியப்பட்டது.",
            ),
        }
        message_en, message_ta = messages[status]
        return {
            "status": status,
            "session_id": session_id,
            "accepted_sign_id": row["sign_id"] if row else None,
            "accepted_concept": row["concept"] if row else None,
            "english": row["english"] if row else None,
            "tamil": row["tamil"] if row else None,
            "confidence": confidence,
            "top_candidates": candidates or [],
            "message_en": message_en,
            "message_ta": message_ta,
            "is_emergency": bool(row and vocabulary.is_emergency(row["concept"])),
            "new_word": new_word,
        }


engine = RecognitionEngine()
