import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.templates import match_template


def test_pain_plus_stomach_template():
    result = match_template(["pain", "stomach"])
    assert result is not None
    assert result["english"] == "I have stomach pain."
    assert "வயிற்றில்" in result["tamil"]


def test_medicine_plus_allergy_template():
    result = match_template(["medicine", "allergy"])
    assert result is not None
    assert "allergy" in result["english"].lower()


def test_help_alone_template():
    result = match_template(["help"])
    assert result is not None
    assert result["english"] == "Help needed."


def test_unsupported_combination_returns_none_not_a_guess():
    """No template exists for this combination - must return None, never a
    fabricated sentence."""
    result = match_template(["xray", "tomorrow", "family"])
    assert result is None


def test_pain_with_two_body_parts_is_ambiguous_and_returns_none():
    """More than one body part with 'pain' is ambiguous - don't guess which one."""
    result = match_template(["pain", "stomach", "chest"])
    assert result is None
