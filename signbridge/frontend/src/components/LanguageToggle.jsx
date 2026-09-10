import React from "react";
import { useLanguage } from "../LanguageContext.jsx";

const OPTIONS = [
  { value: "ta", label: "தமிழ்" },
  { value: "en", label: "English" },
  { value: "both", label: "தமிழ் + English" },
];

export default function LanguageToggle() {
  const { lang, setLang } = useLanguage();
  return (
    <div className="lang-toggle" role="group" aria-label="Language">
      {OPTIONS.map((option) => (
        <button
          key={option.value}
          className={lang === option.value ? "active" : ""}
          aria-pressed={lang === option.value}
          onClick={() => setLang(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
