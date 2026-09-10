import React from "react";
import { useLanguage } from "../LanguageContext.jsx";

/** Displays a recognized/simulated concept's Tamil + English text according
 * to the current language preference, plus an optional speech button. */
export default function BilingualOutput({ tamil, english, onSpeak }) {
  const { lang } = useLanguage();
  if (!tamil && !english) return null;
  return (
    <div className="big-output">
      {(lang === "ta" || lang === "both") && tamil && <div className="ta">{tamil}</div>}
      {(lang === "en" || lang === "both") && english && <div className="en">{english}</div>}
      {onSpeak && (
        <button className="secondary" style={{ marginTop: "0.6rem", fontSize: "1rem" }} onClick={onSpeak}>
          🔊 {lang === "en" ? "Speak" : "பேசு"}
        </button>
      )}
    </div>
  );
}
