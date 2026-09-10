"""Accounts: registration confirmed with an emailed code, password and code
login, the wrong-code limit, and what each role may do."""

import re

import pytest
from fastapi.testclient import TestClient

from app import config
from app.cli import create_user
from app.db import session_scope
from app.main import app
from app.services import mailer

REGISTRATION = {
    "name": "Priya", "phone": "98765 43210", "password": "secret1", "city": "Chennai", "organization": " ",
    "background": "interpreter", "signing_level": "fluent", "sign_language": "tamil", "consent": True,
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def emailed_code(email):
    message = next(m for m in reversed(mailer.outbox)
                   if m["to"] == [email] and m["subject"].endswith("is your SignBridge code"))
    return message["subject"].split()[0]


def wrong(code):
    return "1" * len(code) if code == "0" * len(code) else "0" * len(code)


def error_code(response):
    return response.json()["detail"]["code"]


def make_user(email, role="trainer"):
    with session_scope() as db:
        create_user(db, name=email.split("@")[0], email=email, password="123456", role=role)


def login(client, email, password="123456"):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return bearer(r.json()["token"])


def test_registration_is_confirmed_with_the_emailed_code(client):
    make_user("boss@example.com", role="admin")
    email = "priya@example.com"
    r = client.post("/auth/register", json={**REGISTRATION, "email": "Priya@Example.com"})
    assert r.status_code == 201, r.text
    assert r.json()["otp_length"] == config.OTP_LENGTH == 6
    code = emailed_code(email)
    assert re.fullmatch(r"\d{6}", code)

    r = client.post("/auth/login", json={"email": email, "password": "secret1"})
    assert r.status_code == 403 and error_code(r) == "email_not_verified"

    r = client.post("/auth/register/verify", json={"email": email, "code": wrong(code)})
    assert r.status_code == 400 and error_code(r) == "otp_invalid" and r.json()["detail"]["remaining"] == 4

    mailer.outbox.clear()
    r = client.post("/auth/register/verify", json={"email": email, "code": code})
    assert r.status_code == 200, r.text
    user = r.json()["user"]
    assert (user["role"], user["email"], user["phone"], user["organization"]) == ("trainer", email, "9876543210", None)
    assert client.get("/auth/me", headers=bearer(r.json()["token"])).json()["name"] == "Priya"
    assert {m["subject"] for m in mailer.outbox} == {"Welcome to SignBridge", "New trainer registered: Priya"}

    assert client.post("/auth/register/verify", json={"email": email, "code": code}).status_code == 409
    r = client.post("/auth/register", json={**REGISTRATION, "email": email})
    assert r.status_code == 409 and error_code(r) == "email_taken"
    assert client.post("/auth/login", json={"email": email, "password": "secret1"}).status_code == 200


def test_invalid_registration_details(client):
    details = {**REGISTRATION, "email": "someone@example.com"}
    for field, value in [("phone", "12345"), ("password", "12345"), ("consent", False), ("background", "astronaut"),
                         ("email", "not-an-email"), ("name", " ")]:
        assert client.post("/auth/register", json={**details, field: value}).status_code == 422, field


def test_password_and_code_login(client):
    email = "kumar@example.com"
    make_user(email)
    r = client.post("/auth/login", json={"email": "KUMAR@example.com", "password": "wrong"})
    assert r.status_code == 401 and error_code(r) == "invalid_credentials"
    login(client, "KUMAR@example.com")

    r = client.post("/auth/otp/request", json={"email": email})
    assert r.status_code == 200 and r.json()["otp_length"] == 6
    code = emailed_code(email)
    r = client.post("/auth/otp/verify", json={"email": email, "code": code})
    assert r.status_code == 200 and r.json()["user"]["email"] == email
    r = client.post("/auth/otp/verify", json={"email": email, "code": code})  # a code works once
    assert r.status_code == 400 and error_code(r) == "otp_expired"

    r = client.post("/auth/otp/request", json={"email": "nobody@example.com"})
    assert r.status_code == 404 and error_code(r) == "no_account"


def test_a_code_is_locked_after_too_many_wrong_attempts(client):
    email = "latha@example.com"
    make_user(email)
    client.post("/auth/otp/request", json={"email": email})
    code = emailed_code(email)
    results = [
        error_code(client.post("/auth/otp/verify", json={"email": email, "code": wrong(code)}))
        for _ in range(config.OTP_MAX_ATTEMPTS)
    ]
    assert results == ["otp_invalid"] * (config.OTP_MAX_ATTEMPTS - 1) + ["otp_too_many_attempts"]
    r = client.post("/auth/otp/verify", json={"email": email, "code": code})
    assert r.status_code == 400 and error_code(r) == "otp_too_many_attempts"


def test_codes_cannot_be_requested_again_straight_away(client, monkeypatch):
    monkeypatch.setattr(config, "OTP_RESEND_SECONDS", 60)
    email = "ravi@example.com"
    make_user(email)
    assert client.post("/auth/otp/request", json={"email": email}).status_code == 200
    r = client.post("/auth/otp/request", json={"email": email})
    assert r.status_code == 429 and error_code(r) == "otp_cooldown" and 0 < r.json()["detail"]["retry_after"] <= 60


def test_roles_disabled_accounts_and_password_change(client):
    make_user("chief@example.com", role="admin")
    make_user("meena@example.com")
    admin = login(client, "chief@example.com")
    trainer = login(client, "meena@example.com")

    r = client.get("/samples/stats")
    assert r.status_code == 401 and error_code(r) == "login_required"
    assert error_code(client.get("/samples/stats", headers=bearer("stale"))) == "session_expired"
    assert client.get("/signs", headers=bearer("stale")).status_code == 200  # public pages ignore a stale login
    r = client.get("/admin/users", headers=trainer)
    assert r.status_code == 403 and error_code(r) == "admin_only"

    users = {u["email"]: u for u in client.get("/admin/users", headers=admin).json()}
    meena = users["meena@example.com"]
    assert meena["role"] == "trainer" and meena["recordings"]["draft"] == 0
    r = client.patch(f"/admin/users/{users['chief@example.com']['id']}", headers=admin, json={"is_active": False})
    assert r.status_code == 400

    # changing the password ends the other logins
    r = client.post("/auth/change-password", headers=trainer, json={"current_password": "wrong", "new_password": "newpass1"})
    assert r.status_code == 400 and error_code(r) == "wrong_password"
    r = client.post("/auth/change-password", headers=trainer, json={"current_password": "123456", "new_password": "newpass1"})
    assert r.status_code == 200
    assert client.get("/auth/me", headers=trainer).status_code == 401
    trainer = bearer(r.json()["token"])
    assert client.get("/auth/me", headers=trainer).status_code == 200

    # a disabled account is logged out and can't log in again
    assert client.patch(f"/admin/users/{meena['id']}", headers=admin, json={"is_active": False}).status_code == 200
    assert client.get("/auth/me", headers=trainer).status_code == 401
    r = client.post("/auth/login", json={"email": "meena@example.com", "password": "newpass1"})
    assert r.status_code == 403 and error_code(r) == "account_disabled"
