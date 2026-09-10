import React from "react";
import { useLanguage } from "../LanguageContext.jsx";

export default function AboutResponsibleAI() {
  const { lang } = useLanguage();
  return (
    <div>
      <div className="card">
        <h2>SignBridge</h2>
        <p style={{ color: "var(--text-dim)" }}>
          {lang !== "en"
            ? "காது கேளாத நோயாளிகளுக்கும் சுகாதார ஊழியர்களுக்கும் இடையிலான தொடர்பு தடையை உடைத்தல்."
            : "Breaking the communication barrier between Deaf patients and healthcare workers."}
        </p>
      </div>

      <div className="card">
        <h3>{lang !== "en" ? "இது என்ன இல்லை" : "What this is NOT"}</h3>
        <ul>
          <li>{lang !== "en" ? "மருத்துவ நோய் கண்டறிதல் அமைப்பு அல்ல" : "Not a medical diagnosis system"}</li>
          <li>{lang !== "en" ? "தீவிர சிகிச்சை வகைப்பாட்டு அமைப்பு அல்ல" : "Not a triage system"}</li>
          <li>{lang !== "en" ? "சிகிச்சை பரிந்துரை அமைப்பு அல்ல" : "Not a treatment recommendation system"}</li>
          <li>{lang !== "en" ? "மருத்துவ ஆலோசனை அமைப்பு அல்ல" : "Not a medical advice system"}</li>
          <li>{lang !== "en" ? "சான்றளிக்கப்பட்ட சைகை மொழி மொழிபெயர்ப்பாளர்களுக்கு மாற்றல்ல" : "Not a replacement for certified sign-language interpreters"}</li>
        </ul>
        <p>{lang !== "en" ? "இது ஒரு தொடர்பு உதவி கருவி மட்டுமே." : "This is a communication assistance tool only — it translates communication, it never interprets medical meaning."}</p>
        <p style={{ fontSize: "0.9rem", color: "var(--text-dim)" }}>
          {lang !== "en" ? "எடுத்துக்காட்டு (நல்லது): \"நோயாளி மார்பு வலி பற்றி தொடர்பு கொள்கிறார்.\"" : "Example (good): \"Patient appears to be communicating 'chest pain'.\""}<br />
          {lang !== "en" ? "எடுத்துக்காட்டு (தவறானது): \"நோயாளிக்கு மாரடைப்பு உள்ளது.\"" : "Example (bad, never said): \"Patient is having a heart attack.\""}
        </p>
      </div>

      <div className="card">
        <h3>{lang !== "en" ? "வரம்புகள்" : "Limitations — read before you rely on this"}</h3>
        <ul>
          <li>{lang !== "en" ? "முன்மாதிரி." : "This is a prototype."}</li>
          <li>{lang !== "en" ? "வரையறுக்கப்பட்ட, பெரும்பாலும் சரிபார்க்கப்படாத சொல்லகராதி — Healthcare Vocabulary பக்கத்தில் ஒவ்வொரு உள்ளீட்டின் சரிபார்ப்பு நிலையையும் பார்க்கவும்." : "Limited vocabulary, most of it still unverified — check every entry's validation status on the Healthcare Vocabulary page."}</li>
          <li>{lang !== "en" ? "அங்கீகாரம் ஆதரிக்கப்படும் அடையாளங்கள் மற்றும் சரிபார்க்கப்பட்ட தரவுகளைப் பொறுத்தது." : "Recognition depends entirely on supported signs and validated data — it was not trained on, and does not claim to cover, Tamil Sign Language broadly."}</li>
          <li>{lang !== "en" ? "தெரியாத அடையாளங்கள் வேண்டுமென்றே நிராகரிக்கப்படுகின்றன, யூகிக்கப்படுவதில்லை." : "Unknown signs are intentionally rejected rather than guessed. This is a feature, not a weakness."}</li>
          <li>{lang !== "en" ? "தற்போது எந்த அடையாளமும் 'சரிபார்க்கப்பட்டது' என குறிக்கப்படவில்லை — அனைத்தும் சமூக சரிபார்ப்புக்காக காத்திருக்கின்றன." : "As shipped, no sign is marked 'validated' yet — every concept is awaiting community/interpreter review. See DATASET_SOURCES.md."}</li>
        </ul>
      </div>

      <div className="card">
        <h3>{lang !== "en" ? "தனியுரிமை" : "Privacy, by design"}</h3>
        <p>{lang !== "en"
          ? "கேமரா → உள்ளூர் செயலாக்கம் → அடையாளங்கள் → கணிப்பு → சட்டகம் நிராகரிக்கப்படும். இயல்பாக வீடியோ சேமிக்கப்படாது அல்லது பதிவேற்றப்படாது."
          : "Camera → local (in-browser) processing → landmarks extracted → prediction → frame discarded. Raw video is never saved or uploaded by default. Only in the clearly-labeled Dataset Collection Mode, with explicit consent, is a clip ever recorded — and even then, it's saved to your own device, not silently uploaded."}
        </p>
      </div>

      <div className="card">
        <h3>{lang !== "en" ? "தரவு மற்றும் ஆதாரங்கள்" : "Data and sources"}</h3>
        <p>{lang !== "en"
          ? "இந்த முன்மாதிரியுடன் வழங்கப்பட்ட DATASET_SOURCES.md மற்றும் DATA_LICENSE.md ஆவணங்களைப் பார்க்கவும்."
          : "See DATASET_SOURCES.md and DATA_LICENSE.md, shipped alongside this prototype, for a full audit of every dataset considered, what's verified vs. not, and the license/consent policy for any data this project collects."}
        </p>
      </div>
    </div>
  );
}
