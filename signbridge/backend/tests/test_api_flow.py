"""End to end over the HTTP API with synthetic landmarks:
add a custom word -> record samples -> train -> live predict -> sentence."""

import numpy as np
from fastapi.testclient import TestClient

from app import config
from app.main import app
from tests.synthetic import NONE_LABEL, make_clip

SIGNERS = 3
SAMPLES_PER_SIGNER = 6


def post_clip(client, concept, signer, rng):
    return client.post("/samples", json={
        "concept": concept, "signer_id": f"signer {signer}", "frames": make_clip(concept, signer, rng),
    })


def test_teach_train_predict_translate():
    rng = np.random.default_rng(0)
    with TestClient(app) as client:
        assert client.get("/health").json()["model_loaded"] is False
        r = client.post("/train")  # nothing recorded yet
        assert r.status_code == 400
        assert r.json()["detail"]["code"] == "not_enough_data" and r.json()["detail"]["counts"] == {}
        assert "{" not in r.json()["detail"]["message"]  # readable text, not a dumped dict

        # custom word
        r = client.post("/signs", json={"english": "Thumbs up", "tamil": "கட்டைவிரல் மேலே"})
        assert r.status_code == 200, r.text
        custom = r.json()
        assert custom["concept"] == "thumbs_up" and custom["sign_id"].startswith("CU")
        assert client.post("/signs", json={"english": "thumbs  UP", "tamil": "x"}).status_code == 409

        # validation
        assert post_clip(client, "not_a_word", 0, rng).status_code == 404
        no_hands = [{"t": i * 33.0} for i in range(20)]
        r = client.post("/samples", json={"concept": "water", "signer_id": "a", "frames": no_hands})
        assert r.status_code == 422 and r.json()["detail"]["code"] == "no_hands"

        # one word with a few samples is still not enough, and the counts come back per word
        for _ in range(2):
            assert post_clip(client, "hello", 0, rng).status_code == 200
        r = client.post("/train")
        assert r.status_code == 400 and r.json()["detail"]["counts"] == {"hello": 2}

        # record
        words = ["hello", "water", "thumbs_up", NONE_LABEL]
        for concept in words:
            for signer in range(SIGNERS):
                for _ in range(SAMPLES_PER_SIGNER):
                    r = post_clip(client, concept, signer, rng)
                    assert r.status_code == 200, r.text
        stats = client.get("/samples/stats").json()
        assert stats["water"]["count"] == SIGNERS * SAMPLES_PER_SIGNER
        assert stats["water"]["signers"] == ["signer-0", "signer-1", "signer-2"]

        # train
        r = client.post("/train")
        assert r.status_code == 200, r.text
        meta = r.json()
        assert meta["cv_method"] == "signer-held-out"
        assert meta["cv_accuracy"] > 0.9
        assert meta["warning_codes"] == []
        assert sorted(meta["words"]) == ["hello", "thumbs_up", "water"]
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

        # sentence
        sentence = client.post("/translate", json={"words": ["want", "water"]}).json()
        assert sentence["english"] == "I want water." and sentence["tamil"] == "எனக்கு தண்ணீர் வேண்டும்."

        # deleting a custom word removes its samples; built-ins can't be deleted
        assert client.delete(f"/signs/{custom['sign_id']}").status_code == 200
        assert "thumbs_up" not in client.get("/samples/stats").json()
        assert client.delete("/signs/HC001").status_code == 400

        last = stats["hello"]["last_id"]
        assert client.delete(f"/samples/{last}").status_code == 200
        assert client.delete("/samples/../../etc").status_code == 404
