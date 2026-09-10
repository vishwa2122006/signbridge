"""End to end over the HTTP API with synthetic landmarks: trainers propose a
word and record -> submit -> an admin reviews -> the admin trains -> live
predict -> sentence."""

import numpy as np
from fastapi.testclient import TestClient

from app import config
from app.cli import create_user
from app.db import session_scope
from app.main import app
from app.services import mailer
from tests.synthetic import NONE_LABEL, make_clip

SIGNERS = 3
SAMPLES_PER_SIGNER = 6


def login(client, email):
    r = client.post("/auth/login", json={"email": email, "password": "123456"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def post_clip(client, headers, concept, signer, rng):
    return client.post("/samples", headers=headers, json={"concept": concept, "frames": make_clip(concept, signer, rng)})


def record(client, headers, concept, signer, rng, n=SAMPLES_PER_SIGNER):
    for _ in range(n):
        r = post_clip(client, headers, concept, signer, rng)
        assert r.status_code == 200, r.text
    return r.json()


def concepts(response):
    return {s["concept"] for s in response.json()}


def pending_ids(client, admin, concept):
    samples = client.get(f"/review/words/{concept}/samples", headers=admin).json()["samples"]
    return [s["id"] for s in samples if s["status"] == "pending"]


def test_record_review_train_predict_translate():
    rng = np.random.default_rng(0)
    with session_scope() as db:
        create_user(db, name="Admin", email="admin@example.com", password="123456", role="admin")
        for i in range(SIGNERS):
            create_user(db, name=f"Trainer {i}", email=f"trainer{i}@example.com", password="123456", role="trainer")

    with TestClient(app) as client:
        admin = login(client, "admin@example.com")
        trainers = [login(client, f"trainer{i}@example.com") for i in range(SIGNERS)]
        assert client.get("/health").json()["model_loaded"] is False

        # the public can't record or train; trainers can't train or review
        assert post_clip(client, {}, "hello", 0, rng).status_code == 401
        assert client.post("/train").status_code == 401
        assert client.post("/train", headers=trainers[0]).status_code == 403
        assert client.get("/review/words", headers=trainers[0]).status_code == 403
        r = client.post("/train", headers=admin)  # nothing approved yet
        assert r.status_code == 400
        assert r.json()["detail"]["code"] == "not_enough_data" and r.json()["detail"]["counts"] == {}
        assert "{" not in r.json()["detail"]["message"]  # readable text, not a dumped dict

        # a trainer proposes a word: only they see it until an admin approves it
        mailer.outbox.clear()
        r = client.post("/signs", headers=trainers[0], json={"english": "Thumbs up", "tamil": "கட்டைவிரல் மேலே"})
        assert r.status_code == 200, r.text
        custom = r.json()
        assert (custom["concept"], custom["status"]) == ("thumbs_up", "pending") and custom["sign_id"].startswith("CU")
        label = "Thumbs up / கட்டைவிரல் மேலே"
        assert {m["subject"] for m in mailer.outbox} == {f"New word proposed: {label}", f"Word sent for review: {label}"}
        assert "thumbs_up" not in concepts(client.get("/signs"))
        assert "thumbs_up" in concepts(client.get("/signs", headers=trainers[0]))
        assert "thumbs_up" not in concepts(client.get("/signs", headers=trainers[1]))
        r = client.post("/signs", headers=trainers[1], json={"english": "thumbs  UP", "tamil": "x"})
        assert r.status_code == 409 and r.json()["detail"]["code"] == "word_pending"
        r = client.post("/signs", headers=admin, json={"english": "Water", "tamil": "x"})
        assert r.status_code == 409 and r.json()["detail"]["code"] == "word_exists"

        # validation
        assert post_clip(client, trainers[0], "not_a_word", 0, rng).status_code == 404
        assert post_clip(client, trainers[1], "thumbs_up", 1, rng).status_code == 404  # someone else's proposal
        no_hands = [{"t": i * 33.0} for i in range(20)]
        r = client.post("/samples", headers=trainers[0], json={"concept": "water", "frames": no_hands})
        assert r.status_code == 422 and r.json()["detail"]["code"] == "no_hands"

        # recordings stay drafts until submitted
        for i, headers in enumerate(trainers):
            for concept in ["hello", "water", NONE_LABEL]:
                assert record(client, headers, concept, i, rng)["status"] == "draft"
        record(client, trainers[0], "thumbs_up", 0, rng)
        bad_take = record(client, trainers[0], "water", 0, rng, n=1)["id"]
        stats = client.get("/samples/stats", headers=trainers[0]).json()
        assert stats["water"]["mine"] == {"draft": 7, "pending": 0, "approved": 0, "rejected": 0}
        assert 1400 <= stats["water"]["typical_ms"] <= 1500  # 45 frames at 30 fps
        too_long = [{"t": i * 100.0, "right": make_clip("water", 0, rng)[0]["right"]} for i in range(80)]
        r = client.post("/samples", headers=trainers[0], json={"concept": "water", "frames": too_long})
        assert r.status_code == 422 and r.json()["detail"]["code"] == "too_long"
        assert stats["water"]["last_id"] == bad_take
        assert [w["concept"] for w in client.get("/review/words", headers=admin).json()] == ["thumbs_up"]

        mailer.outbox.clear()
        for headers in trainers:
            assert client.post("/samples/submit", headers=headers, json={}).status_code == 200
        r = client.post("/samples/submit", headers=trainers[0], json={})
        assert r.status_code == 400 and r.json()["detail"]["code"] == "nothing_to_submit"
        assert "Review needed: 25 recordings from Trainer 0" in {m["subject"] for m in mailer.outbox}

        # review: a new word's recordings wait for the word itself
        queue = {w["concept"]: w for w in client.get("/review/words", headers=admin).json()}
        assert queue["thumbs_up"]["status"] == "pending" and queue["thumbs_up"]["proposed_by"]["name"] == "Trainer 0"
        assert queue["water"]["counts"] == {"pending": 19, "approved": 0, "rejected": 0}
        assert queue["water"]["trainers"] == SIGNERS
        r = client.post("/review/samples", headers=admin, json={"approve": pending_ids(client, admin, "thumbs_up")})
        assert r.status_code == 400 and r.json()["detail"]["code"] == "word_not_approved"
        r = client.post(f"/review/words/{custom['sign_id']}", headers=admin, json={"action": "approve"})
        assert r.status_code == 200 and r.json()["status"] == "approved"
        assert "thumbs_up" in concepts(client.get("/signs"))

        # now everyone can record the word; an admin's own recordings skip review
        for i in (1, 2):
            record(client, trainers[i], "thumbs_up", i, rng)
            assert client.post("/samples/submit", headers=trainers[i], json={"concept": "thumbs_up"}).status_code == 200
        admin_take = record(client, admin, "hello", 0, rng, n=1)
        assert admin_take["status"] == "approved"
        assert client.delete(f"/samples/{admin_take['id']}", headers=admin).status_code == 200

        # one batch of decisions: one email per trainer, one summary for the admins
        mailer.outbox.clear()
        ids = [i for concept in ["hello", "water", "thumbs_up", NONE_LABEL] for i in pending_ids(client, admin, concept)]
        r = client.post("/review/samples", headers=admin, json={
            "approve": [i for i in ids if i != bad_take], "reject": [bad_take], "note": "Hands out of frame",
        })
        assert r.status_code == 200 and r.json()["updated"] == len(ids) == 73
        to_trainer = [m for m in mailer.outbox if m["to"] == ["trainer0@example.com"]]
        assert [m["subject"] for m in to_trainer] == ["Your recordings were reviewed: 24 approved, 1 rejected"]
        assert "Hands out of frame" in to_trainer[0]["text"]
        assert [m["subject"] for m in mailer.outbox if "admin@example.com" in m["to"]] == [
            "Review saved: 72 approved, 1 rejected"]

        assert client.delete(f"/samples/{bad_take}", headers=trainers[0]).status_code == 403  # already reviewed
        stats = client.get("/samples/stats", headers=trainers[0]).json()
        assert stats["water"]["mine"]["rejected"] == 1 and stats["water"]["last_note"] == "Hands out of frame"
        assert stats["water"]["approved_total"] == SIGNERS * SAMPLES_PER_SIGNER and stats["water"]["last_id"] is None

        # train
        r = client.post("/train", headers=admin)
        assert r.status_code == 200, r.text
        meta = r.json()
        assert meta["cv_method"] == "signer-held-out"
        assert meta["cv_accuracy"] > 0.9
        assert meta["warning_codes"] == []
        assert sorted(meta["words"]) == ["hello", "thumbs_up", "water"]
        assert meta["max_window_ms"] == 1500 and meta["window_ms"]["water"] == 1500
        assert client.get("/health").json()["model_loaded"] is True
        signs = {s["concept"]: s for s in client.get("/signs").json()}
        assert signs["water"]["trained"] and signs["water"]["samples"] == SIGNERS * SAMPLES_PER_SIGNER

        # live prediction: a held sign is emitted exactly once
        results = [
            client.post("/predict", json={"session_id": "live", "window": make_clip("water", 1, rng)}).json()
            for _ in range(config.STABILITY_WINDOW + 4)
        ]
        recognized = [r for r in results if r["status"] == "RECOGNIZED"]
        assert recognized, results[-1]
        assert {r["accepted_concept"] for r in recognized} == {"water"}
        assert sum(r["new_word"] for r in results) == 1
        assert recognized[0]["tamil"] == "தண்ணீர்"

        no_hand = client.post("/predict", json={"session_id": "live", "window": [{"t": 0}, {"t": 33}]}).json()
        assert no_hand["status"] == "NO_HAND"

        # a hearing person's reply shown as signs: only words with approved recordings have a clip to replay
        items = client.post("/text-to-signs", json={"text": "Do you want water?"}).json()["items"]
        assert [i["concept"] for i in items] == ["you", "want", "water"]
        assert [i["has_sign"] for i in items] == [False, False, True]
        demo = client.get("/signs/water/demo")
        assert demo.status_code == 200, demo.text
        assert len(demo.json()["frames"]) >= 5 and demo.json()["tamil"] == "தண்ணீர்"
        missing = client.get("/signs/fever/demo")
        assert missing.status_code == 404 and missing.json()["detail"]["code"] == "no_recording"

        # sentence
        sentence = client.post("/translate", json={"words": ["want", "water"]}).json()
        assert sentence["english"] == "I want water." and sentence["tamil"] == "எனக்கு தண்ணீர் வேண்டும்."

        # an approved word can only be deleted by an admin, together with its recordings; built-ins can't be
        assert client.delete(f"/signs/{custom['sign_id']}", headers=trainers[0]).status_code == 403
        assert client.delete(f"/signs/{custom['sign_id']}", headers=admin).status_code == 200
        assert "thumbs_up" not in client.get("/samples/stats", headers=admin).json()
        assert client.delete("/signs/HC001", headers=admin).status_code == 400
        assert client.delete(f"/samples/{bad_take}", headers=admin).status_code == 200
        assert client.delete("/samples/abc", headers=admin).status_code == 422
