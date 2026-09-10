function makeUtterance(text, lang) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang === "ta" ? "ta-IN" : "en-IN";
  const voices = window.speechSynthesis.getVoices();
  const voice =
    voices.find((v) => v.lang === utterance.lang) || voices.find((v) => v.lang?.startsWith(lang === "ta" ? "ta" : "en"));
  if (voice) utterance.voice = voice;
  return utterance;
}

/** Speaks Tamil and/or English text following the display-language setting
 * ("ta" | "en" | "both"). Tamil needs a Tamil voice installed on the device. */
export function speakBilingual({ tamil, english }, lang) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  if (lang !== "en" && tamil) window.speechSynthesis.speak(makeUtterance(tamil, "ta"));
  if (lang !== "ta" && english) window.speechSynthesis.speak(makeUtterance(english, "en"));
}
