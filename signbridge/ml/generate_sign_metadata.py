"""
generate_sign_metadata.py

Builds sign_metadata.csv — the CANDIDATE healthcare concept ontology.

IMPORTANT: this generates candidate concepts (English word, Tamil text
translation, healthcare category) — it does NOT claim any of them have a
verified Tamil Sign Language gesture. Every row is written with
validation_status="unverified" and sign_language="not yet mapped" by
design. A concept only becomes usable in the live recognizer once someone
actually records/validates a real sign for it (see DATASET_SOURCES.md and
the Dataset Collection Mode) and this file is updated by hand or via the
/feedback + dataset pipeline — never by a script guessing gestures.

The Tamil text given here is standard written Tamil for the English word —
i.e. what should be DISPLAYED/SPOKEN once a sign is recognized. It is a
language translation, not a sign-language claim.
"""

import csv

# (concept_slug, english, tamil, healthcare_category, likely_static_or_dynamic, priority_demo_candidate)
# likely_static_or_dynamic is a PRELIMINARY GUESS for planning purposes only —
# must be confirmed once an actual reference sign video exists.
CONCEPTS = [
    # EMERGENCY
    ("help", "Help", "உதவி", "EMERGENCY", "unknown", True),
    ("emergency", "Emergency", "அவசரம்", "EMERGENCY", "unknown", True),
    ("accident", "Accident", "விபத்து", "EMERGENCY", "unknown", False),
    ("danger", "Danger", "ஆபத்து", "EMERGENCY", "unknown", False),
    ("stop", "Stop", "நிறுத்து", "EMERGENCY", "unknown", False),
    ("call_someone", "Call someone", "யாரையாவது கூப்பிடுங்கள்", "EMERGENCY", "unknown", False),
    ("doctor", "Doctor", "மருத்துவர்", "EMERGENCY", "unknown", True),
    ("nurse", "Nurse", "செவிலியர்", "EMERGENCY", "unknown", False),

    # BASIC NEEDS
    ("water", "Water", "தண்ணீர்", "BASIC_NEEDS", "unknown", True),
    ("food", "Food", "உணவு", "BASIC_NEEDS", "unknown", False),
    ("toilet", "Toilet", "கழிப்பறை", "BASIC_NEEDS", "unknown", False),
    ("sleep", "Sleep", "தூக்கம்", "BASIC_NEEDS", "unknown", False),
    ("sit", "Sit", "உட்காருங்கள்", "BASIC_NEEDS", "unknown", False),
    ("stand", "Stand", "நில்லுங்கள்", "BASIC_NEEDS", "unknown", False),
    ("wait", "Wait", "காத்திருங்கள்", "BASIC_NEEDS", "unknown", True),
    ("come", "Come", "வாருங்கள்", "BASIC_NEEDS", "unknown", False),
    ("go", "Go", "போங்கள்", "BASIC_NEEDS", "unknown", False),
    ("help_me", "Help me", "எனக்கு உதவி செய்யுங்கள்", "BASIC_NEEDS", "unknown", False),

    # SYMPTOMS
    ("pain", "Pain", "வலி", "SYMPTOMS", "unknown", True),
    ("fever", "Fever", "காய்ச்சல்", "SYMPTOMS", "unknown", False),
    ("headache", "Headache", "தலைவலி", "SYMPTOMS", "unknown", False),
    ("stomach_pain", "Stomach pain", "வயிற்று வலி", "SYMPTOMS", "unknown", False),
    ("chest_pain", "Chest pain", "மார்பு வலி", "SYMPTOMS", "unknown", False),
    ("back_pain", "Back pain", "முதுகு வலி", "SYMPTOMS", "unknown", False),
    ("dizziness", "Dizziness", "தலைசுற்றல்", "SYMPTOMS", "unknown", False),
    ("vomiting", "Vomiting", "வாந்தி", "SYMPTOMS", "unknown", False),
    ("nausea", "Nausea", "குமட்டல்", "SYMPTOMS", "unknown", False),
    ("cough", "Cough", "இருமல்", "SYMPTOMS", "unknown", False),
    ("cold", "Cold", "சளி", "SYMPTOMS", "unknown", False),
    ("breathing_difficulty", "Breathing difficulty", "மூச்சுத் திணறல்", "SYMPTOMS", "unknown", True),
    ("bleeding", "Bleeding", "இரத்தப்போக்கு", "SYMPTOMS", "unknown", True),
    ("swelling", "Swelling", "வீக்கம்", "SYMPTOMS", "unknown", False),
    ("weakness", "Weakness", "பலவீனம்", "SYMPTOMS", "unknown", False),

    # BODY PARTS
    ("head", "Head", "தலை", "BODY_PARTS", "static", False),
    ("eye", "Eye", "கண்", "BODY_PARTS", "static", False),
    ("ear", "Ear", "காது", "BODY_PARTS", "static", False),
    ("nose", "Nose", "மூக்கு", "BODY_PARTS", "static", False),
    ("mouth", "Mouth", "வாய்", "BODY_PARTS", "static", False),
    ("throat", "Throat", "தொண்டை", "BODY_PARTS", "static", False),
    ("neck", "Neck", "கழுத்து", "BODY_PARTS", "static", False),
    ("chest", "Chest", "மார்பு", "BODY_PARTS", "static", False),
    ("heart", "Heart", "இதயம்", "BODY_PARTS", "static", False),
    ("stomach", "Stomach", "வயிறு", "BODY_PARTS", "static", True),
    ("hand", "Hand", "கை", "BODY_PARTS", "static", False),
    ("arm", "Arm", "புஜம்", "BODY_PARTS", "static", False),
    ("leg", "Leg", "கால்", "BODY_PARTS", "static", False),
    ("foot", "Foot", "பாதம்", "BODY_PARTS", "static", False),
    ("back", "Back", "முதுகு", "BODY_PARTS", "static", False),

    # MEDICAL ACTIONS
    ("medicine", "Medicine", "மருந்து", "MEDICAL_ACTIONS", "unknown", True),
    ("injection", "Injection", "ஊசி", "MEDICAL_ACTIONS", "unknown", False),
    ("operation", "Operation", "அறுவை சிகிச்சை", "MEDICAL_ACTIONS", "unknown", False),
    ("test", "Test", "பரிசோதனை", "MEDICAL_ACTIONS", "unknown", False),
    ("scan", "Scan", "ஸ்கேன்", "MEDICAL_ACTIONS", "unknown", False),
    ("blood_test", "Blood test", "இரத்த பரிசோதனை", "MEDICAL_ACTIONS", "unknown", False),
    ("xray", "X-ray", "எக்ஸ்-ரே", "MEDICAL_ACTIONS", "unknown", False),
    ("treatment", "Treatment", "சிகிச்சை", "MEDICAL_ACTIONS", "unknown", False),
    ("check", "Check", "பரிசோதி", "MEDICAL_ACTIONS", "unknown", False),
    ("examination", "Examination", "பரிசோதனை", "MEDICAL_ACTIONS", "unknown", False),

    # PATIENT INFORMATION
    ("name", "Name", "பெயர்", "PATIENT_INFO", "unknown", False),
    ("age", "Age", "வயது", "PATIENT_INFO", "unknown", False),
    ("address", "Address", "முகவரி", "PATIENT_INFO", "unknown", False),
    ("phone", "Phone", "தொலைபேசி", "PATIENT_INFO", "unknown", False),
    ("family", "Family", "குடும்பம்", "PATIENT_INFO", "unknown", False),
    ("mother", "Mother", "அம்மா", "PATIENT_INFO", "unknown", False),
    ("father", "Father", "அப்பா", "PATIENT_INFO", "unknown", False),
    ("emergency_contact", "Emergency contact", "அவசர தொடர்பு", "PATIENT_INFO", "unknown", False),

    # TIME / HISTORY
    ("today", "Today", "இன்று", "TIME_HISTORY", "unknown", False),
    ("yesterday", "Yesterday", "நேற்று", "TIME_HISTORY", "unknown", False),
    ("tomorrow", "Tomorrow", "நாளை", "TIME_HISTORY", "unknown", False),
    ("morning", "Morning", "காலை", "TIME_HISTORY", "unknown", False),
    ("night", "Night", "இரவு", "TIME_HISTORY", "unknown", False),
    ("before", "Before", "முன்பு", "TIME_HISTORY", "unknown", False),
    ("after", "After", "பின்பு", "TIME_HISTORY", "unknown", False),
    ("now", "Now", "இப்போது", "TIME_HISTORY", "unknown", False),
    ("since", "Since", "முதல்", "TIME_HISTORY", "unknown", False),
    ("how_long", "How long?", "எவ்வளவு காலமாக?", "TIME_HISTORY", "unknown", False),

    # MEDICATION
    ("tablet", "Tablet", "மாத்திரை", "MEDICATION", "unknown", False),
    ("dose", "Dose", "அளவு", "MEDICATION", "unknown", False),
    ("before_food", "Before food", "சாப்பிடுவதற்கு முன்", "MEDICATION", "unknown", False),
    ("after_food", "After food", "சாப்பிட்ட பிறகு", "MEDICATION", "unknown", False),
    ("allergy", "Allergy", "ஒவ்வாமை", "MEDICATION", "unknown", True),

    # COMMUNICATION
    ("yes", "Yes", "ஆம்", "COMMUNICATION", "static", True),
    ("no", "No", "இல்லை", "COMMUNICATION", "static", True),
    ("i_understand", "I understand", "எனக்கு புரிகிறது", "COMMUNICATION", "unknown", False),
    ("i_dont_understand", "I don't understand", "எனக்கு புரியவில்லை", "COMMUNICATION", "unknown", False),
    ("repeat", "Repeat", "மீண்டும் சொல்லுங்கள்", "COMMUNICATION", "unknown", True),
    ("slowly", "Slowly", "மெதுவாக", "COMMUNICATION", "unknown", False),
    ("please_wait", "Please wait", "தயவுசெய்து காத்திருங்கள்", "COMMUNICATION", "unknown", False),
    ("thank_you", "Thank you", "நன்றி", "COMMUNICATION", "static", False),
    ("sorry", "Sorry", "மன்னிக்கவும்", "COMMUNICATION", "unknown", False),
]


def main():
    out_path = "../backend/app/data/sign_metadata.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "sign_id", "concept", "english", "tamil", "sign_language", "source",
            "license", "validation_status", "healthcare_category",
            "static_or_dynamic", "priority_demo_candidate", "notes",
        ])
        for i, (slug, english, tamil, category, motion_guess, is_priority) in enumerate(CONCEPTS, start=1):
            sign_id = f"HC{i:03d}"
            writer.writerow([
                sign_id,
                slug,
                english,
                tamil,
                "not yet mapped - pending validation",  # sign_language
                "none (candidate concept only, no reference video yet)",  # source
                "",  # license - N/A until a source exists
                "unverified",  # validation_status - HARD DEFAULT, never auto-promoted
                category,
                motion_guess,
                "yes" if is_priority else "no",
                "Tamil text is a language translation for display/speech only; "
                "it is NOT a claim about what the sign looks like. This concept "
                "has no validated sign yet - see DATASET_SOURCES.md and "
                "Dataset Collection Mode before adding it to the live recognizer.",
            ])
    print(f"Wrote {len(CONCEPTS)} candidate concepts to {out_path}")


if __name__ == "__main__":
    main()
