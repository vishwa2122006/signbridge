import React from "react";
import { useLanguage } from "../LanguageContext.jsx";

export default function LanguageToggle() {
  const { lang, setLang } = useLanguage();
  return (
    <div className="lang-toggle" role="group" aria-label="Language">
      <button className={lang === "ta" ? "active" : ""} onClick={() => setLang("ta")}>தமிழ்</button>
      <button className={lang === "en" ? "active" : ""} onClick={() => setLang("en")}>English</button>
      <button className={lang === "both" ? "active" : ""} onClick={() => setLang("both")}>Both</button>
    </div>
  );
}
