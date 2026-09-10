"""Settings, paths and tunables.

Settings come from environment variables, with backend/.env loaded first (copy
.env.example). Variables already set in the environment win over the file,
which is how tests point the app at a separate database.

Users, words and recorded samples live in PostgreSQL. DATA_DIR only holds
files: the trained model, and recordings saved as JSON files before the
database existed (moved in with `python -m app.cli import-legacy`). Paths are
functions rather than constants so tests can point SIGNBRIDGE_DATA_DIR at a
temporary directory.
"""

import logging
import os
import secrets

from dotenv import load_dotenv

_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PROJECT_ROOT = os.path.dirname(_BACKEND_ROOT)

load_dotenv(os.path.join(_BACKEND_ROOT, ".env"))

log = logging.getLogger(__name__)


def _int(name: str, default: int) -> int:
    return int(os.environ.get(name) or default)


def data_dir() -> str:
    return os.environ.get("SIGNBRIDGE_DATA_DIR", os.path.join(_PROJECT_ROOT, "dataset"))


def model_dir() -> str:
    return os.path.join(data_dir(), "models")


def legacy_samples_dir() -> str:
    return os.path.join(data_dir(), "landmarks")


def legacy_custom_signs_path() -> str:
    return os.path.join(data_dir(), "custom_signs.csv")


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is not set: copy backend/.env.example to backend/.env and fill it in.")
    # A plain postgresql:// URL means psycopg2 to SQLAlchemy; this app uses psycopg 3.
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


# Label of the "resting hands / not signing" class recorded on the Teach page.
NONE_LABEL = "_none"

# Recognition: a word is only accepted when the classifier is at least this
# confident AND the same word wins STABILITY_RATIO of the last
# STABILITY_WINDOW predictions (one prediction every ~250 ms).
MIN_CONFIDENCE = float(os.environ.get("SIGNBRIDGE_MIN_CONFIDENCE", "0.70"))
STABILITY_WINDOW = int(os.environ.get("SIGNBRIDGE_STABILITY_WINDOW", "4"))
STABILITY_RATIO = float(os.environ.get("SIGNBRIDGE_STABILITY_RATIO", "0.75"))

# Login tokens
JWT_SECRET = os.environ.get("JWT_SECRET", "").strip()
if not JWT_SECRET:
    JWT_SECRET = secrets.token_urlsafe(32)
    log.warning("JWT_SECRET is not set: using a temporary one, so everyone is logged out when the server restarts.")
JWT_EXPIRE_HOURS = _int("JWT_EXPIRE_HOURS", 24)

# One-time codes sent by email for registration and login
OTP_LENGTH = min(10, max(4, _int("OTP_LENGTH", 6)))
OTP_EXPIRE_MINUTES = _int("OTP_EXPIRE_MINUTES", 10)
OTP_MAX_ATTEMPTS = _int("OTP_MAX_ATTEMPTS", 5)
OTP_RESEND_SECONDS = _int("OTP_RESEND_SECONDS", 60)

# Email. Without SMTP_PASSWORD nothing is sent and messages are logged instead.
SMTP_HOST = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
SMTP_PORT = _int("SMTP_PORT", 587)
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").replace(" ", "")  # Gmail shows app passwords in groups of four
MAIL_FROM = os.environ.get("MAIL_FROM", "").strip() or SMTP_USER
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME") or "SignBridge"

# Links in emails point here (the app uses hash routes: FRONTEND_URL/#/review).
FRONTEND_URL = (os.environ.get("FRONTEND_URL") or "http://localhost:5173").rstrip("/")
CORS_ORIGINS = [origin.strip() for origin in (os.environ.get("CORS_ORIGINS") or "*").split(",") if origin.strip()]
