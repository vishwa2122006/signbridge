"""
templates.py — deterministic sentence formation.

Per the spec: no LLM, no generative sentence construction. A sentence is
only ever produced by an explicit, human-written template matched against
a set of recognized concept slugs. If no template matches, the caller gets
None back and should fall back to showing the individual recognized
concepts as separate badges rather than a fabricated sentence.

Tamil grammatical forms (e.g. locative case endings on body parts) are
hand-curated below and have NOT been reviewed by a native Tamil-language
or Deaf-community validator as part of this prototype - treat them as a
best-effort draft, and get them checked before relying on them in a real
deployment.
"""

from typing import List, Optional, Dict

# Hand-curated locative ("in the ...") forms for body parts used in the
# PAIN + <body part> template. Only covers what's needed for the demo
# vocabulary - extend deliberately, don't auto-generate.
_LOCATIVE_TAMIL: Dict[str, str] = {
    "stomach": "வயிற்றில்",
    "head": "தலையில்",
    "chest": "மார்பில்",
    "back": "முதுகில்",
    "throat": "தொண்டையில்",
    "leg": "காலில்",
    "hand": "கையில்",
    "eye": "கண்ணில்",
    "ear": "காதில்",
}

_BODY_PART_SLUGS = set(_LOCATIVE_TAMIL.keys())


def _pain_plus_bodypart(slugs: set) -> Optional[dict]:
    if "pain" not in slugs:
        return None
    body_parts = slugs & _BODY_PART_SLUGS
    if len(body_parts) != 1:
        return None
    part = next(iter(body_parts))
    return {
        "template_id": "pain_plus_bodypart",
        "tamil": f"எனக்கு {_LOCATIVE_TAMIL[part]} வலி உள்ளது.",
        "english": f"I have {part} pain.",
        "matched_concepts": ["pain", part],
    }


def _medicine_plus_allergy(slugs: set) -> Optional[dict]:
    if {"medicine", "allergy"} <= slugs:
        return {
            "template_id": "medicine_plus_allergy",
            "tamil": "எனக்கு இந்த மருந்துக்கு ஒவ்வாமை உள்ளது.",
            "english": "I have an allergy to this medicine.",
            "matched_concepts": ["medicine", "allergy"],
        }
    return None


def _help_alone(slugs: set) -> Optional[dict]:
    if slugs == {"help"}:
        return {
            "template_id": "help_alone",
            "tamil": "உதவி தேவை.",
            "english": "Help needed.",
            "matched_concepts": ["help"],
        }
    return None


def _emergency_alone(slugs: set) -> Optional[dict]:
    if slugs == {"emergency"}:
        return {
            "template_id": "emergency_alone",
            "tamil": "இது அவசரநிலை.",
            "english": "This is an emergency.",
            "matched_concepts": ["emergency"],
        }
    return None


# Order matters: more specific templates are tried first.
_TEMPLATE_FUNCS = [
    _medicine_plus_allergy,
    _pain_plus_bodypart,
    _help_alone,
    _emergency_alone,
]


def match_template(concept_slugs: List[str]) -> Optional[dict]:
    """Returns a matched template dict, or None if no deterministic template
    fits this exact combination of recognized concepts. Never falls back to
    guessing a sentence - the caller should display raw concept badges instead."""
    slugs = set(concept_slugs)
    for fn in _TEMPLATE_FUNCS:
        result = fn(slugs)
        if result:
            return result
    return None
