// A stable, distinct hue per vocabulary category so words are easy to scan.
// Components pass it to CSS as --hue (see .word-btn, .tag, .selected-word in index.css).
const CATEGORY_HUES = {
  EMERGENCY: 352,
  SYMPTOMS: 14,
  PEOPLE: 30,
  PATIENT_INFO: 44,
  DESCRIBING: 58,
  MEDICATION: 92,
  ACTIONS: 132,
  MEDICAL_ACTIONS: 156,
  CUSTOM: 174,
  BASIC_NEEDS: 190,
  PLACES_THINGS: 204,
  TIME_HISTORY: 220,
  QUESTIONS: 244,
  BODY_PARTS: 266,
  COMMUNICATION: 286,
  FEELINGS: 312,
  GREETINGS: 332,
};

export function hueFor(category = "") {
  if (category in CATEGORY_HUES) return CATEGORY_HUES[category];
  let hash = 0;
  for (const ch of category) hash = (hash * 31 + ch.codePointAt(0)) % 360;
  return hash;
}

export const categoryStyle = (category) => ({ "--hue": hueFor(category) });
