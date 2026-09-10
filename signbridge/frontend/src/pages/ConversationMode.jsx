import React, { useEffect, useState, useRef } from "react";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";

function speak(text, langHint) {
  if (!("speechSynthesis" in window) || !text) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = langHint === "ta" ? "ta-IN" : "en-IN";
  window.speechSynthesis.speak(utter);
}

export default function ConversationMode() {
  const { lang } = useLanguage();
  const [vocabulary, setVocabulary] = useState([]);
  const [pending, setPending] = useState([]);
  const [log, setLog] = useState([]);
  const [staffText, setStaffText] = useState("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    api.listSigns().then(setVocabulary).catch(() => setVocabulary([]));
  }, []);

  const togglePending = (concept) => {
    setPending((p) => (p.includes(concept) ? p.filter((c) => c !== concept) : [...p, concept]));
  };

  const submitPatientSigns = async () => {
    if (pending.length === 0) return;
    const conceptLabels = pending.map((slug) => vocabulary.find((v) => v.concept === slug));
    const { matched, template } = await api.translateTemplate(pending);
    if (matched) {
      setLog((l) => [...l, { who: "patient", tamil: template.tamil, english: template.english, ts: Date.now() }]);
      speak(lang === "en" ? template.english : template.tamil, lang === "en" ? "en" : "ta");
    } else {
      // No deterministic template matched this combination - show the raw
      // recognized concepts as separate badges instead of guessing a sentence.
      const tamil = conceptLabels.map((c) => c?.tamil).join(" + ");
      const english = conceptLabels.map((c) => c?.english).join(" + ");
      setLog((l) => [...l, { who: "patient", tamil, english, ts: Date.now(), noTemplate: true }]);
    }
    setPending([]);
  };

  const submitStaffText = () => {
    if (!staffText.trim()) return;
    setLog((l) => [...l, { who: "staff", tamil: staffText, english: staffText, ts: Date.now() }]);
    setStaffText("");
  };

  const startListening = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      alert(lang !== "en" ? "இந்த உலாவி பேச்சு-அறிதலை ஆதரிக்கவில்லை." : "This browser doesn't support speech recognition.");
      return;
    }
    const rec = new SR();
    rec.lang = lang === "ta" ? "ta-IN" : "en-IN";
    rec.onresult = (e) => setStaffText(e.results[0][0].transcript);
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    setListening(true);
    rec.start();
  };

  return (
    <div>
      <div className="disclaimer-banner">
        {lang !== "en"
          ? "இது ஒரு தொடர்பு பாலம். மருத்துவ ஆலோசனை அல்ல."
          : "This is a communication bridge, not medical advice."}
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3>🤟 {lang !== "en" ? "நோயாளி" : "Patient"}</h3>
          <p style={{ color: "var(--text-dim)", fontSize: "0.9rem" }}>
            {lang !== "en" ? "ஒன்று அல்லது அதற்கு மேற்பட்ட அடையாளங்களைத் தேர்ந்தெடுக்கவும்:" : "Select one or more recognized concepts:"}
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.75rem" }}>
            {vocabulary.slice(0, 30).map((v) => (
              <button
                key={v.sign_id}
                className={pending.includes(v.concept) ? "" : "secondary"}
                style={{ fontSize: "0.85rem", padding: "0.5em 0.8em" }}
                onClick={() => togglePending(v.concept)}
              >
                {v.tamil} / {v.english}
              </button>
            ))}
          </div>
          <button onClick={submitPatientSigns} disabled={pending.length === 0}>
            {lang !== "en" ? "அனுப்பு" : "Submit"}
          </button>
        </div>

        <div className="card">
          <h3>🎤 {lang !== "en" ? "ஊழியர் / மருத்துவர்" : "Staff / Doctor"}</h3>
          <p style={{ color: "var(--text-dim)", fontSize: "0.9rem" }}>
            {lang !== "en" ? "கேள்வியை தட்டச்சு செய்யவும் அல்லது பேசவும்:" : "Type or speak a question:"}
          </p>
          <textarea
            value={staffText}
            onChange={(e) => setStaffText(e.target.value)}
            rows={3}
            style={{ width: "100%", borderRadius: "8px", padding: "0.6em", fontSize: "1rem" }}
            placeholder={lang !== "en" ? "எ.கா. எவ்வளவு காலமாக வலி இருக்கிறது?" : "e.g. How long have you had the pain?"}
          />
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
            <button onClick={submitStaffText}>{lang !== "en" ? "அனுப்பு" : "Send"}</button>
            <button className="secondary" onClick={startListening} disabled={listening}>
              🎙 {listening ? (lang !== "en" ? "கேட்கிறது..." : "Listening...") : (lang !== "en" ? "பேசு" : "Speak")}
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>{lang !== "en" ? "உரையாடல் பதிவு" : "Conversation Log"}</h3>
        {log.length === 0 && <p style={{ color: "var(--text-dim)" }}>{lang !== "en" ? "இன்னும் எதுவும் இல்லை." : "Nothing yet."}</p>}
        {log.map((entry, i) => (
          <div key={i} style={{ marginBottom: "1rem", paddingBottom: "0.75rem", borderBottom: "1px solid #22304a" }}>
            <strong>{entry.who === "patient" ? (lang !== "en" ? "நோயாளி:" : "PATIENT:") : (lang !== "en" ? "ஊழியர்:" : "STAFF:")}</strong>
            {(lang === "ta" || lang === "both") && <div>{entry.tamil}</div>}
            {(lang === "en" || lang === "both") && <div style={{ color: "var(--text-dim)" }}>{entry.english}</div>}
            {entry.noTemplate && (
              <div style={{ fontSize: "0.8rem", color: "var(--warn)" }}>
                {lang !== "en" ? "(இந்த சேர்க்கைக்கு வாக்கிய வார்ப்புரு இல்லை — தனிப்பட்ட கருத்துக்கள் காட்டப்படுகின்றன)" : "(no sentence template for this combination — showing individual concepts)"}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
