"""Accounts: registering as a trainer (confirmed with a code sent by email), and
logging in with a password or with a one-time code sent by email.
Admins are created with `python -m app.cli create-user --role admin`."""

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.db import get_db
from app.errors import ApiError
from app.models.schemas import (
    AuthResponse, ChangePasswordRequest, CodeRequest, EmailRequest, LoginRequest, RegisterRequest, UserOut,
)
from app.models.tables import TRAINER, User, utcnow
from app.routers.deps import require_user
from app.services import notifications, security
from app.services.mailer import EmailError

router = APIRouter(prefix="/auth")

REGISTER = "register"
LOGIN = "login"


def _find(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email.lower()))


def _logged_in(db: Session, user: User) -> dict:
    user.last_login_at = utcnow()
    db.commit()
    return {"token": security.create_token(user), "user": UserOut.model_validate(user)}


def _send_code(db: Session, user: User, purpose: str) -> dict:
    """Issues a code, emails it and commits. Nothing is saved if the email can't be sent."""
    code = security.issue_otp(db, user.email, purpose)
    try:
        notifications.send_code(user.name, user.email, code, purpose)
    except EmailError:
        db.rollback()
        raise ApiError(502, "email_failed", "The email with your code couldn't be sent - please try again later.")
    db.commit()
    return {
        "email": user.email,
        "otp_length": config.OTP_LENGTH,
        "expires_in": config.OTP_EXPIRE_MINUTES * 60,
        "resend_after": config.OTP_RESEND_SECONDS,
    }


def _check_can_log_in(user: User):
    if not user.email_verified:
        raise ApiError(403, "email_not_verified", "This email isn't verified yet - register again to get a new code.")
    if not user.is_active:
        raise ApiError(403, "account_disabled", "This account has been disabled - please contact the admin.")


@router.post("/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Step 1 of becoming a trainer: saves the details and emails a code. Registering again
    before the email is verified replaces the details and sends a new code."""
    email = req.email.lower()
    user = _find(db, email)
    if user is not None and (user.email_verified or user.is_admin):
        raise ApiError(409, "email_taken", "An account with this email already exists - log in instead.")
    if user is None:
        user = User(email=email, role=TRAINER)
        db.add(user)
    user.name, user.phone, user.city = req.name, req.phone, req.city
    user.organization, user.about = req.organization, req.about
    user.background, user.signing_level, user.sign_language = req.background, req.signing_level, req.sign_language
    user.password_hash = security.hash_password(req.password)
    user.consent_at = utcnow()
    db.flush()
    return _send_code(db, user, REGISTER)


@router.post("/register/verify", response_model=AuthResponse)
def verify_registration(req: CodeRequest, background: BackgroundTasks, db: Session = Depends(get_db)):
    """Step 2: the emailed code verifies the email, and the new trainer is logged in."""
    user = _find(db, req.email)
    if user is None:
        raise ApiError(404, "no_account", "No registration found for this email - please register first.")
    if user.email_verified:
        raise ApiError(409, "already_verified", "This email is already verified - log in instead.")
    security.check_otp(db, user.email, REGISTER, req.code)
    user.email_verified_at = utcnow()
    response = _logged_in(db, user)
    background.add_task(notifications.trainer_registered, notifications.person(user),
                        notifications.registration_details(user), notifications.admin_emails(db))
    return response


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = _find(db, req.email)
    if user is None or not security.verify_password(req.password, user.password_hash):
        raise ApiError(401, "invalid_credentials", "Incorrect email or password.")
    _check_can_log_in(user)
    return _logged_in(db, user)


@router.post("/otp/request")
def request_login_code(req: EmailRequest, db: Session = Depends(get_db)):
    user = _find(db, req.email)
    if user is None:
        raise ApiError(404, "no_account", "No account found for this email - please register first.")
    _check_can_log_in(user)
    return _send_code(db, user, LOGIN)


@router.post("/otp/verify", response_model=AuthResponse)
def login_with_code(req: CodeRequest, db: Session = Depends(get_db)):
    user = _find(db, req.email)
    if user is None:
        raise ApiError(404, "no_account", "No account found for this email - please register first.")
    _check_can_log_in(user)
    security.check_otp(db, user.email, LOGIN, req.code)
    return _logged_in(db, user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(require_user)):
    return user


@router.post("/change-password", response_model=AuthResponse)
def change_password(req: ChangePasswordRequest, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Returns a new login token: tokens issued before the change stop working."""
    if not security.verify_password(req.current_password, user.password_hash):
        raise ApiError(400, "wrong_password", "The current password is incorrect.")
    user.password_hash = security.hash_password(req.new_password)
    return _logged_in(db, user)
