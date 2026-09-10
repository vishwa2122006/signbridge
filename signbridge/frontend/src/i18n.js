export const STRINGS = {
  appName: { en: "SignBridge", ta: "SignBridge" },
  tagline: {
    en: "Breaking the communication barrier between Deaf patients and healthcare workers.",
    ta: "காது கேளாத நோயாளிகளுக்கும் சுகாதார ஊழியர்களுக்கும் இடையிலான தொடர்பு தடையை உடைத்தல்.",
  },
  disclaimer: {
    en: "Communication assistance only. This system does not provide medical diagnosis or medical advice.",
    ta: "தொடர்பு உதவி மட்டுமே. இந்த அமைப்பு மருத்துவ நோய் கண்டறிதல் அல்லது மருத்துவ ஆலோசனையை வழங்காது.",
  },
  prototypeNotice: {
    en: "Prototype. Limited, unverified vocabulary. Not a replacement for certified sign-language interpreters. Unknown signs are intentionally rejected rather than guessed.",
    ta: "முன்மாதிரி. வரையறுக்கப்பட்ட, சரிபார்க்கப்படாத சொல்லகராதி. சான்றளிக்கப்பட்ட சைகை மொழி மொழிபெயர்ப்பாளர்களுக்கு மாற்றல்ல.",
  },
  navHome: { en: "Home", ta: "முகப்பு" },
  navLive: { en: "Live Translator", ta: "நேரடி மொழிபெயர்ப்பு" },
  navConversation: { en: "Conversation Mode", ta: "உரையாடல் முறை" },
  navVocabulary: { en: "Healthcare Vocabulary", ta: "சுகாதார சொல்லகராதி" },
  navDataset: { en: "Dataset / Research Mode", ta: "தரவுத்தொகுப்பு / ஆராய்ச்சி முறை" },
  navAbout: { en: "About / Responsible AI", ta: "பற்றி / பொறுப்பான AI" },
  startCamera: { en: "Start Camera", ta: "கேமராவைத் தொடங்கு" },
  stopCamera: { en: "Stop Camera", ta: "கேமராவை நிறுத்து" },
  positionHands: { en: "Position your hands inside the camera area.", ta: "உங்கள் கைகளை கேமரா பகுதிக்குள் வையுங்கள்." },
  speak: { en: "Speak", ta: "பேசு" },
  repeat: { en: "Repeat", ta: "மீண்டும்" },
  confidence: { en: "Confidence", ta: "நம்பகத்தன்மை" },
  simulationMode: { en: "Simulation Mode (demo, not live camera)", ta: "உருவகப்படுத்தல் முறை" },
  emergencyAlertTitle: { en: "COMMUNICATION ALERT", ta: "தொடர்பு எச்சரிக்கை" },
};

export function t(key, lang) {
  const entry = STRINGS[key];
  if (!entry) return key;
  if (lang === "both") return `${entry.ta} / ${entry.en}`;
  return entry[lang] ?? entry.en;
}
