"""
text_to_signs.py — turns a hearing person's message into the vocabulary words
that can be shown to the signer as hand signs.

Deterministic word matching, no machine translation: English and Tamil words
are matched against the vocabulary, longest phrase first ("blood test" before
"test"), with simple plural/verb endings, Tamil suffixes ("வலிக்கிறது" -> வலி)
and a small hand-written synonym list. Words that aren't in the vocabulary are
returned too (concept None) so the UI can still show them as text. A sign can
only be shown for words that have recorded samples (has_sign).
"""

import re
from typing import Dict, List, Optional, Tuple

from app.services import sample_store
from app.services.vocabulary import vocabulary

MAX_PHRASE_WORDS = 4
MIN_TAMIL_PREFIX_CHARS = 3  # "வலி" matches "வலிக்கிறது"; two-character words like "கை" are too ambiguous

_TOKEN_RE = re.compile(r"[\w஀-௿'’]+")

_STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "was", "were", "be", "been", "being", "do", "does", "did",
    "have", "has", "had", "any", "some", "to", "of", "on", "in", "at", "for", "with", "by", "it", "its",
    "this", "that", "these", "those", "will", "would", "can", "could", "should", "shall", "may", "might",
    "must", "and", "or", "but", "so", "very", "just", "soon", "down", "up", "also", "too", "let", "lets",
}

# message word -> vocabulary concept
_SYNONYMS = {
    "hurt": "pain", "hurts": "pain", "hurting": "pain", "painful": "pain", "ache": "pain", "aches": "pain",
    "hi": "hello", "hey": "hello", "bye": "goodbye", "thanks": "thank_you",
    "me": "i", "my": "i", "myself": "i", "your": "you", "yours": "you", "yourself": "you",
    "physician": "doctor", "doc": "doctor",
    "medication": "medicine", "medications": "medicine", "medicines": "medicine",
    "pill": "tablet", "pills": "tablet",
    "allergies": "allergy", "allergic": "allergy",
    "bathroom": "toilet", "restroom": "toilet", "washroom": "toilet",
    "mom": "mother", "mum": "mother", "dad": "father",
    "okay": "ok",
    "vomit": "vomiting", "coughing": "cough", "bleed": "bleeding", "afraid": "scared",
    "sleeping": "sleep", "eating": "eat", "drinking": "drink", "waiting": "wait",
    "sitting": "sit", "standing": "stand", "coming": "come", "going": "go",
}


def _normalize(token: str) -> str:
    return token.lower().replace("'", "").replace("’", "")


def _index() -> Tuple[Dict[tuple, str], Dict[tuple, str]]:
    """Phrase -> concept for English and Tamil, rebuilt per call so custom words count."""
    english, tamil = {}, {}
    for row in vocabulary.list_all():
        words = tuple(_normalize(w) for w in _TOKEN_RE.findall(row["english"]))
        if words:
            english.setdefault(words, row["concept"])
        words = tuple(_TOKEN_RE.findall(row["tamil"]))
        if words:
            tamil.setdefault(words, row["concept"])
    return english, tamil


def _single_word(token: str, english: dict, tamil: dict) -> Optional[str]:
    synonym = _SYNONYMS.get(token)
    if synonym and vocabulary.get_by_concept(synonym):
        return synonym
    for suffix in ("es", "s", "ing", "ed"):
        if len(token) > len(suffix) + 2 and token.endswith(suffix) and (token[: -len(suffix)],) in english:
            return english[(token[: -len(suffix)],)]
    prefixes = [
        (len(words[0]), concept)
        for words, concept in tamil.items()
        if len(words) == 1 and len(words[0]) >= MIN_TAMIL_PREFIX_CHARS and token.startswith(words[0])
    ]
    return max(prefixes)[1] if prefixes else None


def text_to_signs(text: str) -> List[dict]:
    raw = _TOKEN_RE.findall(text)
    tokens = [_normalize(t) for t in raw]
    english, tamil = _index()
    recorded = sample_store.stats()

    items, i = [], 0
    while i < len(tokens):
        concept, span = None, 1
        for n in range(min(MAX_PHRASE_WORDS, len(tokens) - i), 0, -1):
            phrase = tuple(tokens[i:i + n])
            concept = english.get(phrase) or tamil.get(tuple(raw[i:i + n]))
            if concept:
                span = n
                break
        if concept is None:
            concept = _single_word(tokens[i], english, tamil)
        if concept is None and tokens[i] in _STOP_WORDS:
            i += 1
            continue

        row = vocabulary.get_by_concept(concept) if concept else None
        items.append({
            "text": " ".join(raw[i:i + span]),
            "concept": concept,
            "english": row["english"] if row else None,
            "tamil": row["tamil"] if row else None,
            "has_sign": bool(concept and recorded.get(concept, {}).get("count")),
        })
        i += span
    return items
