"""Database tables. All timestamps are timezone-aware UTC."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

# roles
ADMIN = "admin"
TRAINER = "trainer"

# review statuses (words use the last three)
DRAFT = "draft"
PENDING = "pending"
APPROVED = "approved"
REJECTED = "rejected"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _time(nullable: bool = True, **kwargs):
    return mapped_column(DateTime(timezone=True), nullable=nullable, **kwargs)


class User(Base):
    """An admin or a trainer. The public uses the app without an account."""

    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin', 'trainer')", name="ck_users_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(254), unique=True)  # always lower-case
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    city: Mapped[Optional[str]] = mapped_column(String(80))
    organization: Mapped[Optional[str]] = mapped_column(String(120))
    background: Mapped[Optional[str]] = mapped_column(String(30))  # schemas.Background
    signing_level: Mapped[Optional[str]] = mapped_column(String(20))  # schemas.SigningLevel
    sign_language: Mapped[Optional[str]] = mapped_column(String(20))  # schemas.SignLanguage
    about: Mapped[Optional[str]] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(10), default=TRAINER)
    password_hash: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    consent_at: Mapped[Optional[datetime]] = _time()
    email_verified_at: Mapped[Optional[datetime]] = _time()
    last_login_at: Mapped[Optional[datetime]] = _time()
    created_at: Mapped[datetime] = _time(nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = _time(nullable=False, default=utcnow, onupdate=utcnow)

    @property
    def is_admin(self) -> bool:
        return self.role == ADMIN

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def signer_id(self) -> str:
        """Groups a person's recordings, so cross-validation can test on people the model hasn't seen."""
        return f"user-{self.id}"


class OtpCode(Base):
    """A one-time code emailed for registration or login. Only a hash is stored."""

    __tablename__ = "otp_codes"
    __table_args__ = (Index("ix_otp_codes_email_purpose", "email", "purpose"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254))
    purpose: Mapped[str] = mapped_column(String(20))  # register | login
    code_hash: Mapped[str] = mapped_column(String(64))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = _time(nullable=False)
    consumed_at: Mapped[Optional[datetime]] = _time()
    created_at: Mapped[datetime] = _time(nullable=False, default=utcnow)


class Word(Base):
    """A vocabulary word. Only approved words are shown to the public, recognized and trained;
    a word proposed by a trainer is pending until an admin reviews it."""

    __tablename__ = "words"
    __table_args__ = (CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_words_status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    sign_id: Mapped[str] = mapped_column(String(12), unique=True)
    concept: Mapped[str] = mapped_column(String(60), unique=True)
    english: Mapped[str] = mapped_column(String(60))
    tamil: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40), default="CUSTOM")
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(20), default="custom")  # builtin | custom
    status: Mapped[str] = mapped_column(String(10), default=APPROVED)
    proposed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[Optional[datetime]] = _time()
    review_note: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = _time(nullable=False, default=utcnow)

    proposed_by: Mapped[Optional[User]] = relationship(foreign_keys=[proposed_by_id])
    reviewed_by: Mapped[Optional[User]] = relationship(foreign_keys=[reviewed_by_id])


class Sample(Base):
    """One recording of a sign: landmark coordinates only, never video.
    See services/sample_store.py for the review statuses."""

    __tablename__ = "samples"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'pending', 'approved', 'rejected')", name="ck_samples_status"),
        Index("ix_samples_word_status", "word_id", "status"),
        Index("ix_samples_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[Optional[int]] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"))  # NULL = Idle (no sign)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))  # NULL = imported
    signer_id: Mapped[str] = mapped_column(String(60))
    source: Mapped[str] = mapped_column(String(200), default="webcam")
    aspect: Mapped[float] = mapped_column(Float)
    num_frames: Mapped[int] = mapped_column(Integer)
    hand_frames: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)  # first to last frame
    frames: Mapped[list] = mapped_column(JSONB, deferred=True)  # large: only loaded when asked for
    status: Mapped[str] = mapped_column(String(10), default=DRAFT)
    submitted_at: Mapped[Optional[datetime]] = _time()
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[Optional[datetime]] = _time()
    review_note: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = _time(nullable=False, default=utcnow)

    word: Mapped[Optional[Word]] = relationship()
    user: Mapped[Optional[User]] = relationship(foreign_keys=[user_id])


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    succeeded: Mapped[bool] = mapped_column(Boolean)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB)
    error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = _time(nullable=False, default=utcnow)
