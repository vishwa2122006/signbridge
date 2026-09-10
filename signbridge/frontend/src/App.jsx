import React from "react";
import { HashRouter, Route, Routes, useLocation } from "react-router-dom";
import { LanguageProvider } from "./LanguageContext.jsx";
import AnimatedBackground from "./components/AnimatedBackground.jsx";
import { T } from "./components/Bilingual.jsx";
import SiteHeader from "./components/SiteHeader.jsx";
import ConversationMode from "./pages/ConversationMode.jsx";
import Home from "./pages/Home.jsx";
import TeachSigns from "./pages/TeachSigns.jsx";
import Translate from "./pages/Translate.jsx";
import Vocabulary from "./pages/Vocabulary.jsx";

function Shell() {
  const { pathname } = useLocation();
  return (
    <div className="app-shell">
      <AnimatedBackground />
      <SiteHeader />

      <main className={pathname === "/conversation" ? "wide" : ""}>
        {/* keyed so each page plays the fade-in when you navigate to it */}
        <div key={pathname} className="page-enter">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/translate" element={<Translate />} />
            <Route path="/teach" element={<TeachSigns />} />
            <Route path="/conversation" element={<ConversationMode />} />
            <Route path="/vocabulary" element={<Vocabulary />} />
          </Routes>
        </div>
      </main>

      <footer className="footer-note">
        <span className="heart">♥</span> SignBridge · <T k="footer" />
      </footer>
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
