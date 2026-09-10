"""Passwords (bcrypt), login tokens (JWT) and one-time codes sent by email."""

import hashlib
import hmac
import math
import secrets
from datetime import timedelta
from typing import Optional

import bcrypt
import jwt
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import config
from app.errors import ApiError
from app.models.tables import OtpCode, User, utcnow

_ALGORITHM = "HS256"


def _hmac(message: str) -> str:
    return hmac.new(config.JWT_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()


def hash_password(password: str) -> str:
    # bcrypt only uses the first 72 bytes
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:72], password_hash.encode("ascii"))
    except ValueError:
        return False


def _password_version(user: User) -> str:
    """Changes whenever the password does, so a password change ends every other login."""
    return _hmac(user.password_hash)[:16]


def create_token(user: User) -> str:
    now = utcnow()
    claims = {"sub": str(user.id), "pv": _password_version(user), "iat": now,
              "exp": now + timedelta(hours=config.JWT_EXPIRE_HOURS)}
    return jwt.encode(claims, config.JWT_SECRET, algorithm=_ALGORITHM)


def user_for_token(db: Session, token: str) -> Optional[User]:
    """The active user a token belongs to, or None if it's invalid, expired or outdated."""
    try:
        claims = jwt.decode(token, config.JWT_SECRET, algorithms=[_ALGORITHM])
        user = db.get(User, int(claims["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
    if user is None or not user.is_active or claims.get("pv") != _password_version(user):
        return None
    return user


def _code_hash(email: str, purpose: str, code: str) -> str:
    return _hmac(f"{purpose}:{email}:{code}")


def issue_otp(db: Session, email: str, purpose: str) -> str:
    """A new code for this email and purpose; earlier unused codes stop working."""
    now = utcnow()
    latest = db.scalars(
        select(OtpCode).where(OtpCode.email == email, OtpCode.purpose == purpose)
        .order_by(OtpCode.created_at.desc()).limit(1)
    ).first()
    if latest is not None:
        wait = math.ceil(config.OTP_RESEND_SECONDS - (now - latest.created_at).total_seconds())
        if wait > 0:
            raise ApiError(429, "otp_cooldown", f"Please wait {wait} seconds before asking for another code.",
                           retry_after=wait)
    db.execute(
        update(OtpCode)
        .where(OtpCode.email == email, OtpCode.purpose == purpose, OtpCode.consumed_at.is_(None))
        .values(consumed_at=now)
    )
    code = "".join(secrets.choice("0123456789") for _ in range(config.OTP_LENGTH))
    db.add(OtpCode(email=email, purpose=purpose, code_hash=_code_hash(email, purpose, code), created_at=now,
                   expires_at=now + timedelta(minutes=config.OTP_EXPIRE_MINUTES)))
    db.flush()
    return code


def check_otp(db: Session, email: str, purpose: str, code: str):
    """Uses up the latest code if `code` matches, else raises ApiError. A wrong
    guess is committed right away so the attempt limit can't be bypassed."""
    now = utcnow()
    otp = db.scalars(
        select(OtpCode)
        .where(OtpCode.email == email, OtpCode.purpose == purpose, OtpCode.consumed_at.is_(None))
        .order_by(OtpCode.created_at.desc()).limit(1)
    ).first()
    if otp is None or otp.expires_at <= now:
        raise ApiError(400, "otp_expired", "This code has expired or was already used - ask for a new one.")
    too_many = ApiError(400, "otp_too_many_attempts", "Too many wrong attempts - ask for a new code.")
    if otp.attempts >= config.OTP_MAX_ATTEMPTS:
        raise too_many
    if not hmac.compare_digest(otp.code_hash, _code_hash(email, purpose, code.strip())):
        otp.attempts += 1
        remaining = config.OTP_MAX_ATTEMPTS - otp.attempts
        db.commit()
        if remaining <= 0:
            raise too_many
        raise ApiError(400, "otp_invalid", f"Wrong code - {remaining} attempt(s) left.", remaining=remaining)
    otp.consumed_at = now
