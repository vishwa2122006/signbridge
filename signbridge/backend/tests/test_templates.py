from app.services.templates import build_sentence, match_template


def test_pain_plus_stomach_template():
    result = match_template(["pain", "stomach"])
    assert result is not None
    assert result["english"] == "I have stomach pain."
    assert "வயிற்றில்" in result["tamil"]


def test_word_order_does_not_matter():
    assert match_template(["stomach", "pain"])["english"] == "I have stomach pain."


def test_medicine_plus_allergy_template():
    result = match_template(["medicine", "allergy"])
    assert result is not None
    assert "allergy" in result["english"].lower()


def test_help_alone_template():
    assert match_template(["help"])["english"] == "Help needed."


def test_unsupported_combination_returns_none_not_a_guess():
    assert match_template(["xray", "tomorrow", "family"]) is None


def test_pain_with_two_body_parts_is_ambiguous_and_returns_none():
    assert match_template(["pain", "stomach", "chest"]) is None


def test_want_water():
    result = build_sentence(["i", "want", "water"])
    assert result["english"] == "I want water."
    assert result["tamil"] == "எனக்கு தண்ணீர் வேண்டும்."


def test_where_is_toilet():
    result = build_sentence(["toilet", "where"])
    assert result["english"] == "Where is the toilet?"
    assert result["tamil"] == "கழிப்பறை எங்கே?"


def test_symptom_since_time():
    result = build_sentence(["fever", "yesterday"])
    assert result["english"] == "I have had a fever since yesterday."
    assert result["tamil"].startswith("நேற்றிலிருந்து")


def test_pain_body_part_since_time():
    result = build_sentence(["pain", "stomach", "since", "yesterday"])
    assert result["english"] == "I have had stomach pain since yesterday."


def test_call_doctor():
    result = build_sentence(["call_someone", "doctor"])
    assert result["english"] == "Please call the doctor."
    assert "மருத்துவரை" in result["tamil"]


def test_multiple_segments_in_one_signed_sequence():
    result = build_sentence(["help", "pain", "stomach"])
    assert result["english"] == "Help needed. I have stomach pain."
    assert [s["template_id"] for s in result["segments"]] == ["help_alone", "pain_plus_bodypart"]


def test_unmatched_words_are_shown_as_plain_words():
    result = build_sentence(["xray", "tomorrow"])
    assert result["english"] == "X-ray Tomorrow"
    assert result["tamil"] == "எக்ஸ்-ரே நாளை"
    assert all(s["template_id"] is None for s in result["segments"])


def test_empty_sequence():
    assert build_sentence([]) == {"english": "", "tamil": "", "segments": []}
