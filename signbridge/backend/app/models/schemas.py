"""Pydantic request/response models for the SignBridge API."""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

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
    window: List[RawFrame] = Field(..., max_length=600, description="The last few seconds of frames (the model's max_window_ms)")
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
    """The signer is the logged-in trainer or admin."""
    concept: str = Field(..., max_length=60)
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


class TextToSignsRequest(BaseModel):
    text: str = Field(..., max_length=500)


class SignUpdate(BaseModel):
    english: Optional[str] = Field(None, min_length=1, max_length=60)
    tamil: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = Field(None, min_length=1, max_length=40)
    is_emergency: Optional[bool] = None


class SubmitRequest(BaseModel):
    concept: Optional[str] = Field(None, max_length=60, description="Only this word's drafts; all drafts if omitted")


class ReviewSamplesRequest(BaseModel):
    approve: List[int] = Field(default_factory=list, max_length=5000)
    reject: List[int] = Field(default_factory=list, max_length=5000)
    note: Optional[str] = Field(None, max_length=500, description="Sent to the trainers of rejected recordings")

    @model_validator(mode="after")
    def _decisions(self):
        if not self.approve and not self.reject:
            raise ValueError("Nothing to review.")
        if set(self.approve) & set(self.reject):
            raise ValueError("A recording can't be both approved and rejected.")
        return self


class ReviewWordRequest(BaseModel):
    action: Literal["approve", "reject"]
    note: Optional[str] = Field(None, max_length=500)


# ---- accounts ----

Background = Literal["deaf", "hard_of_hearing", "interpreter", "teacher", "family", "student", "other"]
SigningLevel = Literal["native", "fluent", "intermediate", "beginner"]
SignLanguage = Literal["tamil", "indian", "both", "other"]


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    password: str = Field(..., min_length=6, max_length=72)
    city: str = Field(..., min_length=2, max_length=80)
    organization: Optional[str] = Field(None, max_length=120)
    background: Background
    signing_level: SigningLevel
    sign_language: SignLanguage
    about: Optional[str] = Field(None, max_length=500)
    consent: bool = Field(..., description="Agrees to their recordings (hand and body points) training the model")

    @field_validator("name", "city", "organization", "about", mode="before")
    @classmethod
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("organization", "about")
    @classmethod
    def _blank_is_none(cls, v):
        return v or None

    @field_validator("phone")
    @classmethod
    def _phone(cls, v):
        compact = re.sub(r"[\s()-]", "", v)
        if not re.fullmatch(r"\+?\d{10,15}", compact):
            raise ValueError("Enter a valid phone number (10 to 15 digits).")
        return compact

    @field_validator("consent")
    @classmethod
    def _consent(cls, v):
        if not v:
            raise ValueError("Please agree to your recordings being used to train the model.")
        return v


class EmailRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class CodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., pattern=r"^\s*\d{4,10}\s*$")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=72)
    new_password: str = Field(..., min_length=6, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    city: Optional[str] = None
    organization: Optional[str] = None
    background: Optional[str] = None
    signing_level: Optional[str] = None
    sign_language: Optional[str] = None
    about: Optional[str] = None
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class UserUpdate(BaseModel):
    is_active: bool
