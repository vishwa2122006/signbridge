// Text-to-speech with the device's voices. Speaking Tamil needs a Tamil voice:
// Windows (Settings › Time & language › Speech), Android (Google Text-to-speech)
// and Chrome on Linux (speech-dispatcher + espeak-ng) can provide one.

const LANG_TAGS = { ta: "ta-IN", en: "en-IN" };
const VOICE_WAIT_MS = 1500; // Chrome fills the voice list only after it's first asked for
const CANCEL_SETTLE_MS = 60; // Chrome drops an utterance queued in the same moment as cancel()

let voicesPromise = null;

function loadVoices() {
  if (!voicesPromise) {
    const synth = window.speechSynthesis;
    voicesPromise = new Promise((resolve) => {
      const done = () => resolve(synth.getVoices());
      if (synth.getVoices().length) return done();
      synth.addEventListener("voiceschanged", done, { once: true });
      setTimeout(done, VOICE_WAIT_MS);
    }).then((voices) => {
      if (!voices.length) voicesPromise = null; // ask again next time
      return voices;
    });
  }
  return voicesPromise;
}

if (typeof window !== "undefined" && "speechSynthesis" in window) loadVoices();

/** A voice for "ta" or "en": exact region first, then any variant of the language (e.g. "ta" from espeak-ng). */
function findVoice(voices, code) {
  const langOf = (voice) => (voice.lang || "").toLowerCase().replace("_", "-");
  return (
    voices.find((v) => langOf(v) === LANG_TAGS[code].toLowerCase()) ||
    voices.find((v) => langOf(v) === code || langOf(v).startsWith(`${code}-`)) ||
    (code === "ta" ? voices.find((v) => /tamil/i.test(v.name)) : undefined)
  );
}

/** Speaks Tamil and/or English: `lang` is "ta", "en" or "both" (Tamil first). Resolves to
 * `{ missing }`, the languages not spoken because the device has no voice for them - Tamil
 * text given to an English voice comes out silent or garbled, so it's skipped instead. */
export async function speakBilingual({ tamil, english }, lang) {
  if (!("speechSynthesis" in window)) return { missing: tamil && lang !== "en" ? ["ta"] : [] };
  const synth = window.speechSynthesis;
  synth.cancel();
  const [voices] = await Promise.all([loadVoices(), new Promise((resolve) => setTimeout(resolve, CANCEL_SETTLE_MS))]);

  const missing = [];
  const parts = [];
  if (lang !== "en" && tamil) parts.push([tamil, "ta"]);
  if (lang !== "ta" && english) parts.push([english, "en"]);
  for (const [text, code] of parts) {
    const voice = findVoice(voices, code);
    if (!voice && code === "ta") {
      missing.push("ta");
      continue;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = voice?.lang || LANG_TAGS[code];
    if (voice) utterance.voice = voice;
    synth.speak(utterance);
  }
  return { missing };
}
