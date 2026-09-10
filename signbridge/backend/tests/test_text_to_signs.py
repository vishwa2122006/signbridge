from app.services.text_to_signs import text_to_signs


def concepts(text):
    return [item["concept"] for item in text_to_signs(text)]


def test_english_sentence_with_synonym_and_unknown_word():
    items = text_to_signs("Where does it hurt? Please point.")
    assert [i["concept"] for i in items] == ["where", "pain", "please", None]
    assert items[-1]["text"] == "point"


def test_longest_phrase_wins():
    assert concepts("How long have you had this problem?") == ["how_long", "you", None]
    assert concepts("We need to do a blood test.") == [None, "need", "blood_test"]
    assert concepts("Please wait") == ["please_wait"]


def test_apostrophes_and_plurals():
    assert concepts("I don't understand") == ["i_dont_understand"]
    assert concepts("doctors and tablets") == ["doctor", "tablet"]


def test_tamil_words_and_suffixes():
    assert concepts("எனக்கு தண்ணீர் வேண்டும்") == [None, "water", "want"]
    assert concepts("வலிக்கிறது") == ["pain"]


def test_items_carry_bilingual_text():
    item = text_to_signs("Water")[0]
    assert item["english"] == "Water" and item["tamil"] == "தண்ணீர்"
    assert "has_sign" in item


def test_empty_and_stop_words_only():
    assert text_to_signs("") == []
    assert text_to_signs("the a is") == []
