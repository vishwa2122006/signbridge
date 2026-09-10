"""
sign_demos.py — picks the recording used to show a word to the signer as a hand sign.

The app replays one approved recording per word. It uses the most typical
one (closest to the average of all the word's approved recordings in feature
space), so a one-off sloppy take isn't the one shown.
"""

from typing import Dict, Optional, Tuple

import numpy as np

from app.ml import features
from app.services import sample_store

MIN_HAND_FRAMES = 5

_chosen: Dict[str, Tuple[tuple, int]] = {}  # concept -> (recordings fingerprint, sample id)


def _hand_frames(sample: dict) -> int:
    return sum(1 for f in sample["frames"] if f.get("left") is not None or f.get("right") is not None)


def representative_sample(concept: str) -> Optional[dict]:
    stats = sample_store.approved_stats().get(concept)
    if not stats:
        return None
    samples = [s for s in sample_store.approved_for_concept(concept) if _hand_frames(s) >= MIN_HAND_FRAMES]
    if not samples:
        return None

    fingerprint = (stats["count"], stats["last_id"])
    cached = _chosen.get(concept)
    if cached and cached[0] == fingerprint:
        match = next((s for s in samples if s["id"] == cached[1]), None)
        if match:
            return match

    vectors = np.stack([features.clip_vector(s["frames"], s.get("aspect") or features.DEFAULT_ASPECT) for s in samples])
    best = samples[int(np.argmin(np.linalg.norm(vectors - vectors.mean(axis=0), axis=1)))]
    _chosen[concept] = (fingerprint, best["id"])
    return best
