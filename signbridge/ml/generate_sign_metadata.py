"""
generate_sign_metadata.py

Builds backend/app/data/sign_metadata.csv — the built-in vocabulary.

Each row is a word the app can learn: its English and Tamil display text,
a category, and whether recognizing it should raise the emergency banner.
The Tamil is standard written Tamil for the English word (what is shown and
spoken once the sign is recognized) — it says nothing about how the sign
looks. Signs themselves are learned from recordings (Teach Signs page or
ml/import_videos.py). Words added from the app are stored separately in
dataset/custom_signs.csv, so re-running this script never loses them.

Usage:
    python ml/generate_sign_metadata.py
"""

import csv
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "app", "data", "sign_metadata.csv")

EMERGENCY = {"help", "emergency", "accident", "breathing_difficulty", "bleeding", "chest_pain"}

# (concept_slug, english, tamil, category) — ids HC001.. in this order; keep appending, never reorder.
HEALTHCARE = [
    # EMERGENCY
    ("help", "Help", "உதவி", "EMERGENCY"),
    ("emergency", "Emergency", "அவசரம்", "EMERGENCY"),
    ("accident", "Accident", "விபத்து", "EMERGENCY"),
    ("danger", "Danger", "ஆபத்து", "EMERGENCY"),
    ("stop", "Stop", "நிறுத்து", "EMERGENCY"),
    ("call_someone", "Call someone", "யாரையாவது கூப்பிடுங்கள்", "EMERGENCY"),
    ("doctor", "Doctor", "மருத்துவர்", "EMERGENCY"),
    ("nurse", "Nurse", "செவிலியர்", "EMERGENCY"),

    # BASIC NEEDS
    ("water", "Water", "தண்ணீர்", "BASIC_NEEDS"),
    ("food", "Food", "உணவு", "BASIC_NEEDS"),
    ("toilet", "Toilet", "கழிப்பறை", "BASIC_NEEDS"),
    ("sleep", "Sleep", "தூக்கம்", "BASIC_NEEDS"),
    ("sit", "Sit", "உட்காருங்கள்", "BASIC_NEEDS"),
    ("stand", "Stand", "நில்லுங்கள்", "BASIC_NEEDS"),
    ("wait", "Wait", "காத்திருங்கள்", "BASIC_NEEDS"),
    ("come", "Come", "வாருங்கள்", "BASIC_NEEDS"),
    ("go", "Go", "போங்கள்", "BASIC_NEEDS"),
    ("help_me", "Help me", "எனக்கு உதவி செய்யுங்கள்", "BASIC_NEEDS"),

    # SYMPTOMS
    ("pain", "Pain", "வலி", "SYMPTOMS"),
    ("fever", "Fever", "காய்ச்சல்", "SYMPTOMS"),
    ("headache", "Headache", "தலைவலி", "SYMPTOMS"),
    ("stomach_pain", "Stomach pain", "வயிற்று வலி", "SYMPTOMS"),
    ("chest_pain", "Chest pain", "மார்பு வலி", "SYMPTOMS"),
    ("back_pain", "Back pain", "முதுகு வலி", "SYMPTOMS"),
    ("dizziness", "Dizziness", "தலைசுற்றல்", "SYMPTOMS"),
    ("vomiting", "Vomiting", "வாந்தி", "SYMPTOMS"),
    ("nausea", "Nausea", "குமட்டல்", "SYMPTOMS"),
    ("cough", "Cough", "இருமல்", "SYMPTOMS"),
    ("cold", "Cold", "சளி", "SYMPTOMS"),
    ("breathing_difficulty", "Breathing difficulty", "மூச்சுத் திணறல்", "SYMPTOMS"),
    ("bleeding", "Bleeding", "இரத்தப்போக்கு", "SYMPTOMS"),
    ("swelling", "Swelling", "வீக்கம்", "SYMPTOMS"),
    ("weakness", "Weakness", "பலவீனம்", "SYMPTOMS"),

    # BODY PARTS
    ("head", "Head", "தலை", "BODY_PARTS"),
    ("eye", "Eye", "கண்", "BODY_PARTS"),
    ("ear", "Ear", "காது", "BODY_PARTS"),
    ("nose", "Nose", "மூக்கு", "BODY_PARTS"),
    ("mouth", "Mouth", "வாய்", "BODY_PARTS"),
    ("throat", "Throat", "தொண்டை", "BODY_PARTS"),
    ("neck", "Neck", "கழுத்து", "BODY_PARTS"),
    ("chest", "Chest", "மார்பு", "BODY_PARTS"),
    ("heart", "Heart", "இதயம்", "BODY_PARTS"),
    ("stomach", "Stomach", "வயிறு", "BODY_PARTS"),
    ("hand", "Hand", "கை", "BODY_PARTS"),
    ("arm", "Arm", "புஜம்", "BODY_PARTS"),
    ("leg", "Leg", "கால்", "BODY_PARTS"),
    ("foot", "Foot", "பாதம்", "BODY_PARTS"),
    ("back", "Back", "முதுகு", "BODY_PARTS"),

    # MEDICAL ACTIONS
    ("medicine", "Medicine", "மருந்து", "MEDICAL_ACTIONS"),
    ("injection", "Injection", "ஊசி", "MEDICAL_ACTIONS"),
    ("operation", "Operation", "அறுவை சிகிச்சை", "MEDICAL_ACTIONS"),
    ("test", "Test", "பரிசோதனை", "MEDICAL_ACTIONS"),
    ("scan", "Scan", "ஸ்கேன்", "MEDICAL_ACTIONS"),
    ("blood_test", "Blood test", "இரத்த பரிசோதனை", "MEDICAL_ACTIONS"),
    ("xray", "X-ray", "எக்ஸ்-ரே", "MEDICAL_ACTIONS"),
    ("treatment", "Treatment", "சிகிச்சை", "MEDICAL_ACTIONS"),
    ("check", "Check", "பரிசோதி", "MEDICAL_ACTIONS"),
    ("examination", "Examination", "பரிசோதனை", "MEDICAL_ACTIONS"),

    # PATIENT INFORMATION
    ("name", "Name", "பெயர்", "PATIENT_INFO"),
    ("age", "Age", "வயது", "PATIENT_INFO"),
    ("address", "Address", "முகவரி", "PATIENT_INFO"),
    ("phone", "Phone", "தொலைபேசி", "PATIENT_INFO"),
    ("family", "Family", "குடும்பம்", "PATIENT_INFO"),
    ("mother", "Mother", "அம்மா", "PATIENT_INFO"),
    ("father", "Father", "அப்பா", "PATIENT_INFO"),
    ("emergency_contact", "Emergency contact", "அவசர தொடர்பு", "PATIENT_INFO"),

    # TIME / HISTORY
    ("today", "Today", "இன்று", "TIME_HISTORY"),
    ("yesterday", "Yesterday", "நேற்று", "TIME_HISTORY"),
    ("tomorrow", "Tomorrow", "நாளை", "TIME_HISTORY"),
    ("morning", "Morning", "காலை", "TIME_HISTORY"),
    ("night", "Night", "இரவு", "TIME_HISTORY"),
    ("before", "Before", "முன்பு", "TIME_HISTORY"),
    ("after", "After", "பின்பு", "TIME_HISTORY"),
    ("now", "Now", "இப்போது", "TIME_HISTORY"),
    ("since", "Since", "முதல்", "TIME_HISTORY"),
    ("how_long", "How long?", "எவ்வளவு காலமாக?", "TIME_HISTORY"),

    # MEDICATION
    ("tablet", "Tablet", "மாத்திரை", "MEDICATION"),
    ("dose", "Dose", "அளவு", "MEDICATION"),
    ("before_food", "Before food", "சாப்பிடுவதற்கு முன்", "MEDICATION"),
    ("after_food", "After food", "சாப்பிட்ட பிறகு", "MEDICATION"),
    ("allergy", "Allergy", "ஒவ்வாமை", "MEDICATION"),

    # COMMUNICATION
    ("yes", "Yes", "ஆம்", "COMMUNICATION"),
    ("no", "No", "இல்லை", "COMMUNICATION"),
    ("i_understand", "I understand", "எனக்கு புரிகிறது", "COMMUNICATION"),
    ("i_dont_understand", "I don't understand", "எனக்கு புரியவில்லை", "COMMUNICATION"),
    ("repeat", "Repeat", "மீண்டும் சொல்லுங்கள்", "COMMUNICATION"),
    ("slowly", "Slowly", "மெதுவாக", "COMMUNICATION"),
    ("please_wait", "Please wait", "தயவுசெய்து காத்திருங்கள்", "COMMUNICATION"),
    ("thank_you", "Thank you", "நன்றி", "COMMUNICATION"),
    ("sorry", "Sorry", "மன்னிக்கவும்", "COMMUNICATION"),
]

# ids EV001.. in this order; keep appending, never reorder.
EVERYDAY = [
    # GREETINGS
    ("hello", "Hello", "வணக்கம்", "GREETINGS"),
    ("goodbye", "Goodbye", "போய் வருகிறேன்", "GREETINGS"),
    ("please", "Please", "தயவுசெய்து", "GREETINGS"),
    ("ok", "OK", "சரி", "GREETINGS"),

    # PEOPLE
    ("i", "I", "நான்", "PEOPLE"),
    ("you", "You", "நீங்கள்", "PEOPLE"),
    ("friend", "Friend", "நண்பர்", "PEOPLE"),
    ("brother", "Brother", "சகோதரர்", "PEOPLE"),
    ("sister", "Sister", "சகோதரி", "PEOPLE"),
    ("deaf", "Deaf", "காது கேளாதவர்", "PEOPLE"),

    # QUESTIONS
    ("what", "What", "என்ன", "QUESTIONS"),
    ("where", "Where", "எங்கே", "QUESTIONS"),
    ("when", "When", "எப்போது", "QUESTIONS"),
    ("why", "Why", "ஏன்", "QUESTIONS"),
    ("how", "How", "எப்படி", "QUESTIONS"),
    ("who", "Who", "யார்", "QUESTIONS"),

    # FEELINGS
    ("happy", "Happy", "மகிழ்ச்சி", "FEELINGS"),
    ("sad", "Sad", "வருத்தம்", "FEELINGS"),
    ("tired", "Tired", "சோர்வு", "FEELINGS"),
    ("hungry", "Hungry", "பசி", "FEELINGS"),
    ("thirsty", "Thirsty", "தாகம்", "FEELINGS"),
    ("angry", "Angry", "கோபம்", "FEELINGS"),
    ("scared", "Scared", "பயம்", "FEELINGS"),
    ("love", "Love", "அன்பு", "FEELINGS"),

    # ACTIONS
    ("eat", "Eat", "சாப்பிடு", "ACTIONS"),
    ("drink", "Drink", "குடி", "ACTIONS"),
    ("want", "Want", "வேண்டும்", "ACTIONS"),
    ("need", "Need", "தேவை", "ACTIONS"),
    ("like", "Like", "பிடிக்கும்", "ACTIONS"),
    ("finish", "Finished", "முடிந்தது", "ACTIONS"),
    ("learn", "Learn", "கற்றுக்கொள்", "ACTIONS"),

    # PLACES & THINGS
    ("home", "Home", "வீடு", "PLACES_THINGS"),
    ("school", "School", "பள்ளி", "PLACES_THINGS"),
    ("work", "Work", "வேலை", "PLACES_THINGS"),
    ("bus", "Bus", "பேருந்து", "PLACES_THINGS"),
    ("money", "Money", "பணம்", "PLACES_THINGS"),
    ("time", "Time", "நேரம்", "PLACES_THINGS"),
    ("sign_language", "Sign language", "சைகை மொழி", "PLACES_THINGS"),

    # DESCRIBING
    ("good", "Good", "நல்லது", "DESCRIBING"),
    ("bad", "Bad", "கெட்டது", "DESCRIBING"),
    ("more", "More", "இன்னும்", "DESCRIBING"),
]


def main():
    rows = []
    for prefix, words in (("HC", HEALTHCARE), ("EV", EVERYDAY)):
        for i, (slug, english, tamil, category) in enumerate(words, start=1):
            rows.append([f"{prefix}{i:03d}", slug, english, tamil, category,
                         "yes" if slug in EMERGENCY else "no", "builtin"])

    slugs = [r[1] for r in rows]
    duplicates = {s for s in slugs if slugs.count(s) > 1}
    if duplicates:
        raise SystemExit(f"Duplicate concept slugs: {sorted(duplicates)}")

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sign_id", "concept", "english", "tamil", "category", "is_emergency", "source"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} words to {os.path.normpath(OUT_PATH)}")


if __name__ == "__main__":
    main()
