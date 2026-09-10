"""
feedback_store.py — community validation storage.

Per spec: community validation is treated as more important than raw model
confidence. This is deliberately simple (append-only JSON Lines file) so it
is easy to inspect and merge into sign_metadata.csv by hand during/after
the hackathon - no hidden database, no silent overwrite of prior feedback.
"""

import json
import os
import time
from typing import List

_FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feedback_log.jsonl")
_DATASET_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset_collection_log.jsonl")


def record_feedback(validator_id: str, sign_id: str, prediction: str, decision: str, comment: str = None) -> dict:
    entry = {
        "validator_id": validator_id,
        "sign_id": sign_id,
        "prediction": prediction,
        "decision": decision,
        "comment": comment,
        "timestamp": time.time(),
    }
    with open(_FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def list_feedback(sign_id: str = None) -> List[dict]:
    if not os.path.exists(_FEEDBACK_PATH):
        return []
    out = []
    with open(_FEEDBACK_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if sign_id is None or entry["sign_id"] == sign_id:
                out.append(entry)
    return out


def record_dataset_sample(sign_id: str, signer_id: str, source: str, frame_count, fps,
                           consent_confirmed: bool) -> dict:
    if not consent_confirmed:
        raise ValueError("Dataset samples cannot be registered without explicit consent_confirmed=true")
    entry = {
        "sign_id": sign_id,
        "signer_id": signer_id,
        "source": source,
        "frame_count": frame_count,
        "fps": fps,
        "consent_confirmed": consent_confirmed,
        "timestamp": time.time(),
    }
    with open(_DATASET_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
