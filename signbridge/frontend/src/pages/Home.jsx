import React from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../LanguageContext.jsx";

export default function Home() {
  const { lang } = useLanguage();
  return (
    <div>
      <div className="disclaimer-banner">
        {lang !== "en"
          ? "தொடர்பு உதவி மட்டுமே. இந்த அமைப்பு மருத்துவ நோய் கண்டறிதலை வழங்காது."
          : "Communication assistance only. This system does not provide medical diagnosis or medical advice."}
        {" — "}
        {lang !== "en" ? "முன்மாதிரி." : "Prototype."}
      </div>

      <div className="card" style={{ textAlign: "center" }}>
        <h2 style={{ fontSize: "1.6rem" }}>
          {lang !== "en" ? "நோயாளி மருத்துவமனையில் நுழைகிறார்..." : "A Deaf patient enters a hospital..."}
        </h2>
        <p style={{ color: "var(--text-dim)", maxWidth: 560, margin: "0.5rem auto 1.5rem" }}>
          {lang !== "en"
            ? "வரவேற்பாளருக்கு சைகை மொழி தெரியாது. SignBridge இந்த இடைவெளியை நிரப்புகிறது."
            : "The receptionist doesn't know sign language. SignBridge helps bridge that gap."}
        </p>
        <Link to="/live">
          <button style={{ fontSize: "1.3rem", padding: "1em 2em" }}>
            📷 {lang !== "en" ? "நேரடி மொழிபெயர்ப்பைத் தொடங்கு" : "Start Live Translator"}
          </button>
        </Link>
      </div>

      <div className="grid cols-3">
        <Link to="/conversation" className="card" style={{ textDecoration: "none", color: "inherit" }}>
          <h3>💬 {lang !== "en" ? "உரையாடல் முறை" : "Conversation Mode"}</h3>
          <p style={{ color: "var(--text-dim)" }}>
            {lang !== "en" ? "நோயாளி மற்றும் ஊழியர் இடையே இரு திசை தொடர்பு." : "Two-way exchange between patient and staff."}
          </p>
        </Link>
        <Link to="/vocabulary" className="card" style={{ textDecoration: "none", color: "inherit" }}>
          <h3>📖 {lang !== "en" ? "சுகாதார சொல்லகராதி" : "Healthcare Vocabulary"}</h3>
          <p style={{ color: "var(--text-dim)" }}>
            {lang !== "en" ? "ஆதரிக்கப்படும் கருத்துக்களையும் அவற்றின் சரிபார்ப்பு நிலையையும் உலாவவும்." : "Browse supported concepts and their validation status."}
          </p>
        </Link>
        <Link to="/about" className="card" style={{ textDecoration: "none", color: "inherit" }}>
          <h3>ℹ️ {lang !== "en" ? "பொறுப்பான AI" : "Responsible AI"}</h3>
          <p style={{ color: "var(--text-dim)" }}>
            {lang !== "en" ? "இந்த முன்மாதிரி என்ன செய்யும், என்ன செய்யாது." : "What this prototype does and does not do."}
          </p>
        </Link>
      </div>
    </div>
  );
}
