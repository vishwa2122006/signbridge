import React from "react";
import { T } from "./Bilingual.jsx";
import { useLanguage } from "../LanguageContext.jsx";

/** Large Tamil + English text according to the language toggle, with an optional speak button. */
export default function BilingualOutput({ tamil, english, onSpeak }) {
  const { lang } = useLanguage();
  if (!tamil && !english) return null;
  return (
    <div className="big-output">
      {lang !== "en" && tamil && <div className="main">{tamil}</div>}
      {lang !== "ta" && english && <div className={lang === "en" ? "main" : "sub"}>{english}</div>}
      {onSpeak && (
        <button className="secondary small speak-btn" onClick={onSpeak}>
          🔊 <T k="speak" />
        </button>
      )}
    </div>
  );
}
