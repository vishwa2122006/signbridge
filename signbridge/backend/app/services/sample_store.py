"""
sample_store.py — recorded training samples on disk.

One JSON file per sample under DATA_DIR/landmarks/<concept>/. Only landmark
coordinates are stored, never video. Files are named
<signer>__<timestamp-ms>_<random>.json so counts and signer lists come from a
directory listing without parsing every file.
"""

import json
import logging
import os
import re
import secrets
import shutil
import time
from typing import Iterator, List, Optional, Tuple

from app import config

CONCEPT_RE = re.compile(r"^_?[a-z0-9_]+$")
SAMPLE_ID_RE = re.compile(r"^[A-Za-z0-9-]+__\d+_[0-9a-f]{6}$")

log = logging.getLogger(__name__)


def safe_signer(signer_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9-]+", "-", signer_id.strip()).strip("-")[:40] or "anonymous"


def _concept_dir(concept: str, root: Optional[str]) -> str:
    if not CONCEPT_RE.match(concept):
        raise ValueError(f"Invalid concept name: {concept!r}")
    return os.path.join(root or config.samples_dir(), concept)


def save_sample(concept: str, signer_id: str, frames: List[dict], aspect: float,
                source: str = "webcam", root: Optional[str] = None) -> dict:
    signer = safe_signer(signer_id)
    sample_id = f"{signer}__{int(time.time() * 1000)}_{secrets.token_hex(3)}"
    directory = _concept_dir(concept, root)
    os.makedirs(directory, exist_ok=True)
    record = {
        "id": sample_id,
        "concept": concept,
        "signer_id": signer,
        "source": source,
        "aspect": aspect,
        "created_at": time.time(),
        "frames": frames,
    }
    path = os.path.join(directory, sample_id + ".json")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(record, f, separators=(",", ":"))
    os.replace(path + ".tmp", path)
    return {"id": sample_id, "concept": concept, "signer_id": signer, "num_frames": len(frames)}


def _iter_files(root: Optional[str]) -> Iterator[Tuple[str, str, str]]:
    root = root or config.samples_dir()
    if not os.path.isdir(root):
        return
    for concept in sorted(os.listdir(root)):
        directory = os.path.join(root, concept)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if name.endswith(".json"):
                yield concept, name[:-5], os.path.join(directory, name)


def stats(root: Optional[str] = None) -> dict:
    """{concept: {"count", "signers", "last_id"}}"""
    out = {}
    for concept, sample_id, _ in _iter_files(root):
        signer, _, rest = sample_id.partition("__")
        timestamp = rest.split("_")[0]
        ts = int(timestamp) if timestamp.isdigit() else 0
        entry = out.setdefault(concept, {"count": 0, "signers": set(), "last_id": None, "_ts": -1})
        entry["count"] += 1
        entry["signers"].add(signer)
        if ts >= entry["_ts"]:
            entry["last_id"], entry["_ts"] = sample_id, ts
    for entry in out.values():
        entry["signers"] = sorted(entry["signers"])
        del entry["_ts"]
    return out


def load_all(root: Optional[str] = None) -> List[dict]:
    samples = []
    for _, _, path in _iter_files(root):
        try:
            with open(path, encoding="utf-8") as f:
                samples.append(json.load(f))
        except (OSError, json.JSONDecodeError) as e:
            log.warning("Skipping unreadable sample %s: %s", path, e)
    return samples


def load_concept(concept: str, root: Optional[str] = None) -> List[dict]:
    directory = _concept_dir(concept, root)
    if not os.path.isdir(directory):
        return []
    samples = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(directory, name), encoding="utf-8") as f:
                samples.append(json.load(f))
        except (OSError, json.JSONDecodeError) as e:
            log.warning("Skipping unreadable sample %s: %s", name, e)
    return samples


def delete_sample(sample_id: str, root: Optional[str] = None) -> bool:
    if not SAMPLE_ID_RE.match(sample_id):
        return False
    for _, candidate, path in _iter_files(root):
        if candidate == sample_id:
            os.remove(path)
            return True
    return False


def delete_concept(concept: str, root: Optional[str] = None) -> None:
    directory = _concept_dir(concept, root)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
