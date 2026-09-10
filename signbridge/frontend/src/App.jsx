import React from "react";
import { HashRouter, Routes, Route, NavLink } from "react-router-dom";
import { LanguageProvider, useLanguage } from "./LanguageContext.jsx";
import LanguageToggle from "./components/LanguageToggle.jsx";
import Home from "./pages/Home.jsx";
import LiveTranslator from "./pages/LiveTranslator.jsx";
import ConversationMode from "./pages/ConversationMode.jsx";
import HealthcareVocabulary from "./pages/HealthcareVocabulary.jsx";
import DatasetMode from "./pages/DatasetMode.jsx";
import AboutResponsibleAI from "./pages/AboutResponsibleAI.jsx";

function Shell() {
  const { lang } = useLanguage();
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <h1>🤟 SignBridge</h1>
          <span className="tagline">
            {lang !== "en"
              ? "காது கேளாத நோயாளிகளுக்கும் சுகாதார ஊழியர்களுக்கும் இடையிலான தொடர்பு தடையை உடைத்தல்."
              : "Breaking the communication barrier between Deaf patients and healthcare workers."}
          </span>
        </div>
        <LanguageToggle />
      </header>

      <nav className="main-nav">
        <NavLink to="/" end>{lang !== "en" ? "முகப்பு" : "Home"}</NavLink>
        <NavLink to="/live">{lang !== "en" ? "நேரடி மொழிபெயர்ப்பு" : "Live Translator"}</NavLink>
        <NavLink to="/conversation">{lang !== "en" ? "உரையாடல் முறை" : "Conversation Mode"}</NavLink>
        <NavLink to="/vocabulary">{lang !== "en" ? "சுகாதார சொல்லகராதி" : "Healthcare Vocabulary"}</NavLink>
        <NavLink to="/dataset">{lang !== "en" ? "தரவுத்தொகுப்பு முறை" : "Dataset / Research Mode"}</NavLink>
        <NavLink to="/about">{lang !== "en" ? "பொறுப்பான AI" : "About / Responsible AI"}</NavLink>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/live" element={<LiveTranslator />} />
          <Route path="/conversation" element={<ConversationMode />} />
          <Route path="/vocabulary" element={<HealthcareVocabulary />} />
          <Route path="/dataset" element={<DatasetMode />} />
          <Route path="/about" element={<AboutResponsibleAI />} />
        </Routes>
      </main>

      <p className="footer-note">
        SignBridge — {lang !== "en" ? "முன்மாதிரி" : "Prototype"} · {lang !== "en"
          ? "மருத்துவ நோய் கண்டறிதல் அல்ல. சான்றளிக்கப்பட்ட மொழிபெயர்ப்பாளர்களுக்கு மாற்றல்ல."
          : "Not medical diagnosis. Not a replacement for certified interpreters."}
      </p>
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <HashRouter>
        <Shell />
      </HashRouter>
    </LanguageProvider>
  );
}
