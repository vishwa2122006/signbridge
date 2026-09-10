"""Pydantic request/response models for the SignBridge API."""

from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RecognitionStatus(str, Enum):
    NO_HAND = "NO_HAND"                # no hand detected in frame(s)
    NO_MODEL = "NO_MODEL"              # no trained/validated model loaded - honest default
    UNCERTAIN = "UNCERTAIN"            # below confidence threshold
    UNSTABLE = "UNSTABLE"              # confidence ok but predictions not temporally stable yet
    UNKNOWN_SIGN = "UNKNOWN_SIGN"      # model actively predicts "not a known class"
    RECOGNIZED = "RECOGNIZED"          # accepted: confident + validated-source + temporally stable


class LandmarkFrame(BaseModel):
    """One frame's worth of hand landmarks, as extracted client-side by MediaPipe."""
    hand_detected: bool
    num_hands: int = 0
    # Flat feature vector: up to 2 hands x 21 landmarks x (x,y,z) = up to 126 floats.
    # Missing hands / frames are zero-filled by the client, matching the training pipeline.
    features: List[float] = Field(default_factory=list)


class PredictRequest(BaseModel):
    session_id: str = Field(..., description="Stable per-user/per-tab session id for temporal smoothing")
    window: List[LandmarkFrame] = Field(..., description="A short sequence of recent frames (e.g. ~1 second)")
    language: str = Field(default="both", pattern="^(ta|en|both)$")


class SimulatePredictRequest(BaseModel):
    """DEMO-ONLY endpoint: lets the UI walk through the full downstream pipeline
    (confidence display, bilingual output, templates, emergency mode, conversation
    log) using a manually chosen concept instead of a real camera + model. The
    response is always clearly labeled simulated=True so it can never be
    mistaken for a real recognition result."""
    session_id: str
    sign_id: str


class RecognitionCandidate(BaseModel):
    sign_id: str
    concept: str
    confidence: float


class PredictResponse(BaseModel):
    status: RecognitionStatus
    session_id: str
    simulated: bool = False
    accepted_sign_id: Optional[str] = None
    accepted_concept: Optional[str] = None
    english: Optional[str] = None
    tamil: Optional[str] = None
    confidence: Optional[float] = None
    top_candidates: List[RecognitionCandidate] = Field(default_factory=list)
    message_en: str
    message_ta: str
    is_emergency: bool = False
    disclaimer: str = (
        "Communication assistance only. This system does not provide medical "
        "diagnosis or medical advice."
    )


class SignMetadataOut(BaseModel):
    sign_id: str
    concept: str
    english: str
    tamil: str
    sign_language: str
    source: str
    validation_status: str
    healthcare_category: str
    static_or_dynamic: str
    priority_demo_candidate: str
    notes: str


class FeedbackRequest(BaseModel):
    validator_id: str
    sign_id: str
    prediction: str
    decision: str = Field(..., pattern="^(correct|incorrect|different_sign|unsure)$")
    comment: Optional[str] = None


class DatasetSampleRegisterRequest(BaseModel):
    sign_id: str
    signer_id: str
    source: str = "community_collected"
    frame_count: Optional[int] = None
    fps: Optional[int] = None
    consent_confirmed: bool = Field(
        ..., description="Must be true - the UI must not allow submission without explicit consent"
    )


class TemplateRequest(BaseModel):
    concept_slugs: List[str]
    language: str = Field(default="both", pattern="^(ta|en|both)$")
