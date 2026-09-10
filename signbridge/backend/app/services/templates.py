"""
templates.py — deterministic, offline sentence formation.

Signed word order differs from spoken English/Tamil order, so templates
match an unordered SET of recognized words. build_sentence() walks the
signed words left to right and, at each position, takes the longest run of
words (up to MAX_SPAN) that exactly matches a template; any word that isn't
part of a matched template is shown as-is. Nothing is ever guessed: no
template match means plain words, not an invented sentence.

The Tamil case forms below (locative "-இல்", accusative "-ஐ", ablative
"-இலிருந்து") are hand-written. Have a native Tamil speaker review them
before relying on them.
"""

from typing import Dict, FrozenSet, List, Optional, Tuple

from app.services.vocabulary import vocabulary

MAX_SPAN = 5

# body part -> (English, Tamil locative "in the ...")
_BODY_PARTS: Dict[str, Tuple[str, str]] = {
    "stomach": ("stomach", "வயிற்றில்"),
    "head": ("head", "தலையில்"),
    "chest": ("chest", "மார்பில்"),
    "back": ("back", "முதுகில்"),
    "throat": ("throat", "தொண்டையில்"),
    "leg": ("leg", "காலில்"),
    "hand": ("hand", "கையில்"),
    "eye": ("eye", "கண்ணில்"),
    "ear": ("ear", "காதில்"),
    "nose": ("nose", "மூக்கில்"),
    "mouth": ("mouth", "வாயில்"),
    "neck": ("neck", "கழுத்தில்"),
    "heart": ("heart", "இதயத்தில்"),
    "arm": ("arm", "புஜத்தில்"),
    "foot": ("foot", "பாதத்தில்"),
}

# time word -> (English "since ...", Tamil ablative)
_SINCE: Dict[str, Tuple[str, str]] = {
    "yesterday": ("yesterday", "நேற்றிலிருந்து"),
    "today": ("today", "இன்றிலிருந்து"),
    "morning": ("this morning", "காலையிலிருந்து"),
    "night": ("last night", "நேற்று இரவிலிருந்து"),
}

# symptom -> (English present, English "since" form, Tamil clause)
_SYMPTOMS: Dict[str, Tuple[str, str, str]] = {
    "pain": ("I am in pain", "I have been in pain", "எனக்கு வலி உள்ளது"),
    "fever": ("I have a fever", "I have had a fever", "எனக்கு காய்ச்சல் உள்ளது"),
    "headache": ("I have a headache", "I have had a headache", "எனக்கு தலைவலி உள்ளது"),
    "stomach_pain": ("I have stomach pain", "I have had stomach pain", "எனக்கு வயிற்று வலி உள்ளது"),
    "chest_pain": ("I have chest pain", "I have had chest pain", "எனக்கு மார்பு வலி உள்ளது"),
    "back_pain": ("I have back pain", "I have had back pain", "எனக்கு முதுகு வலி உள்ளது"),
    "dizziness": ("I feel dizzy", "I have felt dizzy", "எனக்கு தலைசுற்றுகிறது"),
    "vomiting": ("I am vomiting", "I have been vomiting", "எனக்கு வாந்தி வருகிறது"),
    "nausea": ("I feel nauseous", "I have felt nauseous", "எனக்கு குமட்டலாக உள்ளது"),
    "cough": ("I have a cough", "I have had a cough", "எனக்கு இருமல் உள்ளது"),
    "cold": ("I have a cold", "I have had a cold", "எனக்கு சளி உள்ளது"),
    "breathing_difficulty": ("I have difficulty breathing", "I have had difficulty breathing",
                             "எனக்கு மூச்சுத் திணறல் உள்ளது"),
    "bleeding": ("I am bleeding", "I have been bleeding", "எனக்கு இரத்தப்போக்கு உள்ளது"),
    "swelling": ("I have swelling", "I have had swelling", "எனக்கு வீக்கம் உள்ளது"),
    "weakness": ("I feel weak", "I have felt weak", "எனக்கு பலவீனமாக உள்ளது"),
    "allergy": ("I have an allergy", "I have had an allergy", "எனக்கு ஒவ்வாமை உள்ளது"),
}

# object of want/need -> (English, Tamil used in "எனக்கு ___ வேண்டும்")
_WANT_OBJECTS: Dict[str, Tuple[str, str]] = {
    "water": ("water", "தண்ணீர்"),
    "food": ("food", "உணவு"),
    "medicine": ("medicine", "மருந்து"),
    "tablet": ("a tablet", "மாத்திரை"),
    "doctor": ("a doctor", "மருத்துவர்"),
    "nurse": ("a nurse", "செவிலியர்"),
    "help": ("help", "உதவி"),
    "money": ("money", "பணம்"),
    "family": ("my family", "என் குடும்பம்"),
    "mother": ("my mother", "என் அம்மா"),
    "father": ("my father", "என் அப்பா"),
    "sleep": ("to sleep", "தூங்க"),
    "eat": ("to eat", "சாப்பிட"),
    "drink": ("to drink", "குடிக்க"),
    "sit": ("to sit", "உட்கார"),
    "home": ("to go home", "வீட்டுக்குப் போக"),
    "toilet": ("to go to the toilet", "கழிப்பறைக்குப் போக"),
}

# target of "where" -> (English, Tamil)
_WHERE: Dict[str, Tuple[str, str]] = {
    "toilet": ("the toilet", "கழிப்பறை"),
    "doctor": ("the doctor", "மருத்துவர்"),
    "nurse": ("the nurse", "செவிலியர்"),
    "medicine": ("the medicine", "மருந்து"),
    "water": ("the water", "தண்ணீர்"),
    "food": ("the food", "உணவு"),
    "bus": ("the bus", "பேருந்து"),
    "school": ("the school", "பள்ளி"),
    "phone": ("my phone", "என் தொலைபேசி"),
    "family": ("my family", "என் குடும்பம்"),
    "mother": ("my mother", "என் அம்மா"),
    "father": ("my father", "என் அப்பா"),
    "friend": ("my friend", "என் நண்பர்"),
    "brother": ("my brother", "என் சகோதரர்"),
    "sister": ("my sister", "என் சகோதரி"),
}

# person to call -> (English, Tamil accusative)
_CALL: Dict[str, Tuple[str, str]] = {
    "doctor": ("the doctor", "மருத்துவரை"),
    "nurse": ("the nurse", "செவிலியரை"),
    "mother": ("my mother", "என் அம்மாவை"),
    "father": ("my father", "என் அப்பாவை"),
    "family": ("my family", "என் குடும்பத்தினரை"),
    "friend": ("my friend", "என் நண்பரை"),
    "brother": ("my brother", "என் சகோதரரை"),
    "sister": ("my sister", "என் சகோதரியை"),
}

_FEELINGS: Dict[str, Tuple[str, str]] = {
    "happy": ("I am happy", "நான் மகிழ்ச்சியாக இருக்கிறேன்"),
    "sad": ("I am sad", "நான் வருத்தமாக இருக்கிறேன்"),
    "tired": ("I am tired", "நான் சோர்வாக இருக்கிறேன்"),
    "hungry": ("I am hungry", "எனக்குப் பசிக்கிறது"),
    "thirsty": ("I am thirsty", "எனக்குத் தாகமாக இருக்கிறது"),
    "angry": ("I am angry", "எனக்குக் கோபமாக இருக்கிறது"),
    "scared": ("I am scared", "எனக்குப் பயமாக இருக்கிறது"),
}

# (template_id, required words, optional words, English, Tamil)
_FIXED: List[Tuple[str, FrozenSet[str], FrozenSet[str], str, str]] = [
    ("medicine_plus_allergy", frozenset({"medicine", "allergy"}), frozenset({"i"}),
     "I have an allergy to this medicine.", "எனக்கு இந்த மருந்துக்கு ஒவ்வாமை உள்ளது."),
    ("repeat_slowly", frozenset({"repeat", "slowly"}), frozenset({"please"}),
     "Please repeat slowly.", "தயவுசெய்து மெதுவாக மீண்டும் சொல்லுங்கள்."),
    ("dont_understand_repeat", frozenset({"i_dont_understand", "repeat"}), frozenset({"please"}),
     "I don't understand, please repeat.", "எனக்குப் புரியவில்லை, தயவுசெய்து மீண்டும் சொல்லுங்கள்."),
    ("i_am_deaf", frozenset({"i", "deaf"}), frozenset(),
     "I am deaf.", "நான் காது கேளாதவர்."),
    ("i_use_sign_language", frozenset({"i", "sign_language"}), frozenset(),
     "I use sign language.", "நான் சைகை மொழி பயன்படுத்துகிறேன்."),
    ("thank_you_doctor", frozenset({"thank_you", "doctor"}), frozenset(),
     "Thank you, doctor.", "நன்றி, மருத்துவரே."),
    ("help_alone", frozenset({"help"}), frozenset(),
     "Help needed.", "உதவி தேவை."),
    ("emergency_alone", frozenset({"emergency"}), frozenset(),
     "This is an emergency.", "இது அவசரநிலை."),
]


def _template(template_id: str, english: str, tamil: str, slugs: FrozenSet[str]) -> dict:
    return {"template_id": template_id, "english": english, "tamil": tamil, "matched_concepts": sorted(slugs)}


def _split_time(slugs: FrozenSet[str]) -> Optional[Tuple[FrozenSet[str], Optional[str]]]:
    """Separates an optional "(since) <time word>" from the rest. None if ambiguous."""
    times = slugs & set(_SINCE)
    if len(times) > 1 or ("since" in slugs and not times):
        return None
    return slugs - times - {"since"}, next(iter(times), None)


def _fixed(slugs):
    for template_id, required, optional, english, tamil in _FIXED:
        if required <= slugs <= required | optional:
            return _template(template_id, english, tamil, slugs)
    return None


def _pain_plus_bodypart(slugs):
    split = _split_time(slugs - {"i"})
    if split is None:
        return None
    rest, time_word = split
    if "pain" not in rest:
        return None
    parts = rest - {"pain"}
    if len(parts) != 1 or next(iter(parts)) not in _BODY_PARTS:
        return None  # zero or several body parts: don't guess which one hurts
    english_part, tamil_part = _BODY_PARTS[next(iter(parts))]
    if time_word:
        since_en, since_ta = _SINCE[time_word]
        return _template("pain_plus_bodypart", f"I have had {english_part} pain since {since_en}.",
                         f"{since_ta} எனக்கு {tamil_part} வலி உள்ளது.", slugs)
    return _template("pain_plus_bodypart", f"I have {english_part} pain.",
                     f"எனக்கு {tamil_part} வலி உள்ளது.", slugs)


def _symptom(slugs):
    split = _split_time(slugs - {"i"})
    if split is None:
        return None
    rest, time_word = split
    if len(rest) != 1 or next(iter(rest)) not in _SYMPTOMS:
        return None
    present, since_form, tamil = _SYMPTOMS[next(iter(rest))]
    if time_word:
        since_en, since_ta = _SINCE[time_word]
        return _template("symptom_since", f"{since_form} since {since_en}.", f"{since_ta} {tamil}.", slugs)
    return _template("symptom", f"{present}.", f"{tamil}.", slugs)


def _want(slugs):
    rest = slugs - {"i"}
    verbs = rest & {"want", "need"}
    objects = rest - verbs
    if len(verbs) != 1 or len(objects) != 1 or next(iter(objects)) not in _WANT_OBJECTS:
        return None
    english, tamil = _WANT_OBJECTS[next(iter(objects))]
    return _template("want_object", f"I {next(iter(verbs))} {english}.", f"எனக்கு {tamil} வேண்டும்.", slugs)


def _where(slugs):
    rest = slugs - {"where"}
    if "where" not in slugs or len(rest) != 1 or next(iter(rest)) not in _WHERE:
        return None
    english, tamil = _WHERE[next(iter(rest))]
    return _template("where_is", f"Where is {english}?", f"{tamil} எங்கே?", slugs)


def _call(slugs):
    rest = slugs - {"call_someone", "please"}
    if "call_someone" not in slugs or len(rest) != 1 or next(iter(rest)) not in _CALL:
        return None
    english, tamil = _CALL[next(iter(rest))]
    return _template("call_person", f"Please call {english}.", f"தயவுசெய்து {tamil} கூப்பிடுங்கள்.", slugs)


def _feeling(slugs):
    rest = slugs - {"i"}
    if len(rest) != 1 or next(iter(rest)) not in _FEELINGS:
        return None
    english, tamil = _FEELINGS[next(iter(rest))]
    return _template("feeling", f"{english}.", f"{tamil}.", slugs)


# Order matters: more specific templates first.
_TEMPLATE_FUNCS = [_fixed, _pain_plus_bodypart, _want, _where, _call, _symptom, _feeling]


def match_template(concept_slugs: List[str]) -> Optional[dict]:
    """A template matching exactly this set of words, or None."""
    slugs = frozenset(concept_slugs)
    if not slugs:
        return None
    for fn in _TEMPLATE_FUNCS:
        result = fn(slugs)
        if result:
            return result
    return None


def _join(segments: List[dict], key: str) -> str:
    parts, loose = [], []
    for segment in segments:
        if segment["template_id"] is None:
            loose.append(segment[key])
            continue
        if loose:
            parts.append(" ".join(loose))
            loose = []
        parts.append(segment[key])
    if loose:
        parts.append(" ".join(loose))
    return " ".join(parts)


def build_sentence(words: List[str]) -> dict:
    """Ordered signed words -> {"english", "tamil", "segments"}."""
    segments = []
    i = 0
    while i < len(words):
        match, span = None, 1
        for span in range(min(MAX_SPAN, len(words) - i), 0, -1):
            chunk = words[i:i + span]
            if len(set(chunk)) == span:
                match = match_template(chunk)
                if match:
                    break
        if match:
            segments.append({**match, "concepts": words[i:i + span]})
            i += span
            continue
        row = vocabulary.get_by_concept(words[i])
        segments.append({
            "template_id": None,
            "english": row["english"] if row else words[i],
            "tamil": row["tamil"] if row else words[i],
            "concepts": [words[i]],
        })
        i += 1
    return {"english": _join(segments, "english"), "tamil": _join(segments, "tamil"), "segments": segments}
