"""Loads and serves sign_metadata.csv — the single source of truth for which
concepts exist, their bilingual text, and their validation status.

Nothing here invents a sign. This module only reads what's already on disk.
"""

import csv
import os
from typing import Dict, List, Optional

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sign_metadata.csv")

EMERGENCY_CONCEPTS = {"help", "emergency", "breathing_difficulty", "bleeding", "accident"}


class Vocabulary:
    def __init__(self, path: str = _DATA_PATH):
        self.by_id: Dict[str, dict] = {}
        self.by_concept: Dict[str, dict] = {}
        self._load(path)

    def _load(self, path: str):
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.by_id[row["sign_id"]] = row
                self.by_concept[row["concept"]] = row

    def get(self, sign_id: str) -> Optional[dict]:
        return self.by_id.get(sign_id)

    def get_by_concept(self, concept: str) -> Optional[dict]:
        return self.by_concept.get(concept)

    def list_all(self, category: Optional[str] = None,
                 validation_status: Optional[str] = None) -> List[dict]:
        rows = list(self.by_id.values())
        if category:
            rows = [r for r in rows if r["healthcare_category"] == category]
        if validation_status:
            rows = [r for r in rows if r["validation_status"] == validation_status]
        return rows

    def is_emergency(self, concept: str) -> bool:
        return concept in EMERGENCY_CONCEPTS

    def usable_in_live_recognizer(self, sign_id: str) -> bool:
        """A concept may only be offered to the live recognizer once it has at
        least research-reference-level sourcing. 'unverified' with no source
        is a candidate concept only - never presented as a recognizable sign."""
        row = self.get(sign_id)
        if not row:
            return False
        return row["validation_status"] in ("validated", "research-reference")


vocabulary = Vocabulary()
