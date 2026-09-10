import os
import sys
import tempfile

import pytest
from dotenv import dotenv_values

BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND)

# Must happen before any `app` import: tests never touch the real dataset/ folder, the real
# database or a real mailbox (emails only land in app.services.mailer.outbox).
os.environ["SIGNBRIDGE_DATA_DIR"] = tempfile.mkdtemp(prefix="signbridge-test-")
os.environ["SMTP_PASSWORD"] = ""
os.environ["OTP_RESEND_SECONDS"] = "0"
os.environ["OTP_LENGTH"] = "6"
os.environ["JWT_SECRET"] = "test-secret-" + "x" * 32

_env_file = dotenv_values(os.path.join(BACKEND, ".env"))
_test_url = os.environ.get("TEST_DATABASE_URL") or _env_file.get("TEST_DATABASE_URL")
_app_url = os.environ.get("DATABASE_URL") or _env_file.get("DATABASE_URL")
if not _test_url:
    pytest.exit("Set TEST_DATABASE_URL (in backend/.env) to an empty PostgreSQL database for tests.", returncode=4)
if _test_url == _app_url:
    pytest.exit("TEST_DATABASE_URL must not be DATABASE_URL: the tests wipe that database.", returncode=4)
os.environ["DATABASE_URL"] = _test_url


@pytest.fixture(scope="session", autouse=True)
def database():
    """A fresh schema with the built-in vocabulary for every test run."""
    from app import db
    from app.models import tables  # noqa: F401

    db.Base.metadata.drop_all(db.engine())
    db.init_db()
    yield
    db.engine().dispose()
