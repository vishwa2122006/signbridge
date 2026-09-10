import React from "react";
import { useLanguage } from "../LanguageContext.jsx";

export default function EmergencyBanner({ englishText, tamilText }) {
  const { lang } = useLanguage();
  return (
    <div className="emergency-banner" role="alert">
      <span>🚨</span>
      <div>
        <div>{lang !== "en" ? "தொடர்பு எச்சரிக்கை" : "COMMUNICATION ALERT"}</div>
        {(lang === "ta" || lang === "both") && <div style={{ fontWeight: 600 }}>{tamilText}</div>}
        {(lang === "en" || lang === "both") && <div style={{ fontWeight: 600 }}>{englishText}</div>}
      </div>
    </div>
  );
}
