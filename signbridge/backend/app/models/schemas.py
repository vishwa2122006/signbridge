"""Pydantic request/response models for the SignBridge API."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.ml.features import DEFAULT_ASPECT, NUM_HAND_POINTS, NUM_POSE_POINTS


class RecognitionStatus(str, Enum):
    NO_HAND = "NO_HAND"            # no hands in the camera window
    NO_MODEL = "NO_MODEL"          # nothing trained yet
    IDLE = "IDLE"                  # hands visible but resting (model's "_none" class)
    UNCERTAIN = "UNCERTAIN"        # below confidence threshold
    UNSTABLE = "UNSTABLE"          # confident, but not stable across recent ticks yet
    UNKNOWN_SIGN = "UNKNOWN_SIGN"  # model label with no vocabulary entry
    RECOGNIZED = "RECOGNIZED"      # confident + stable + in the vocabulary


def _check_points(value, n: int, what: str):
    if value is not None and (len(value) != n or any(len(p) < 3 for p in value)):
        raise ValueError(f"{what} must have {n} [x, y, z] points")
    return value


class RawFrame(BaseModel):
    """One camera frame of landmarks, as produced by frontend/src/mediapipe.js.
    See app/ml/features.py for the exact meaning of each field."""
    t: float = 0.0
    left: Optional[List[List[float]]] = None
    right: Optional[List[List[float]]] = None
    pose: Optional[List[List[float]]] = None

    @field_validator("left", "right")
    @classmethod
    def _hand(cls, v):
        return _check_points(v, NUM_HAND_POINTS, "a hand")

    @field_validator("pose")
    @classmethod
    def _pose(cls, v):
        return _check_points(v, NUM_POSE_POINTS, "pose")


class PredictRequest(BaseModel):
    session_id: str = Field(..., max_length=100)
    window: List[RawFrame] = Field(..., max_length=300, description="The last ~1.5 s of frames")
    aspect: float = Field(DEFAULT_ASPECT, gt=0.2, lt=5.0, description="Video width / height")


class RecognitionCandidate(BaseModel):
    sign_id: str
    concept: str
    confidence: float


class PredictResponse(BaseModel):
    status: RecognitionStatus
    session_id: str
    accepted_sign_id: Optional[str] = None
    accepted_concept: Optional[str] = None
    english: Optional[str] = None
    tamil: Optional[str] = None
    confidence: Optional[float] = None
    top_candidates: List[RecognitionCandidate] = Field(default_factory=list)
    message_en: str
    message_ta: str
    is_emergency: bool = False
    new_word: bool = False


class SampleCreate(BaseModel):
    concept: str = Field(..., max_length=60)
    signer_id: str = Field(..., min_length=1, max_length=40)
    frames: List[RawFrame] = Field(..., min_length=5, max_length=600)
    aspect: float = Field(DEFAULT_ASPECT, gt=0.2, lt=5.0)
    source: str = Field("webcam", max_length=200)


class SignCreate(BaseModel):
    english: str = Field(..., min_length=1, max_length=60)
    tamil: str = Field(..., min_length=1, max_length=120)
    category: str = Field("CUSTOM", max_length=40)
    is_emergency: bool = False


class TranslateRequest(BaseModel):
    words: List[str] = Field(..., max_length=50)
