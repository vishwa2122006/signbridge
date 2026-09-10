import React from "react";
import { HashRouter, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider } from "./AuthContext.jsx";
import { LanguageProvider } from "./LanguageContext.jsx";
import AnimatedBackground from "./components/AnimatedBackground.jsx";
import { T } from "./components/Bilingual.jsx";
import RequireAuth from "./components/RequireAuth.jsx";
import SiteHeader from "./components/SiteHeader.jsx";
import Account from "./pages/Account.jsx";
import ConversationMode from "./pages/ConversationMode.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Review from "./pages/Review.jsx";
import TeachSigns from "./pages/TeachSigns.jsx";
import Translate from "./pages/Translate.jsx";
import Vocabulary from "./pages/Vocabulary.jsx";

const WIDE_PAGES = ["/conversation", "/review"];

function Shell() {
  const { pathname } = useLocation();
  return (
    <div className="app-shell">
      <AnimatedBackground />
      <SiteHeader />

      <main className={WIDE_PAGES.includes(pathname) ? "wide" : ""}>
        {/* keyed so each page plays the fade-in when you navigate to it */}
        <div key={pathname} className="page-enter">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/translate" element={<Translate />} />
            <Route path="/conversation" element={<ConversationMode />} />
            <Route path="/vocabulary" element={<Vocabulary />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/teach"
              element={
                <RequireAuth>
                  <TeachSigns />
                </RequireAuth>
              }
            />
            <Route
              path="/review"
              element={
                <RequireAuth admin>
                  <Review />
                </RequireAuth>
              }
            />
            <Route
              path="/account"
              element={
                <RequireAuth>
                  <Account />
                </RequireAuth>
              }
            />
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
      <AuthProvider>
        <HashRouter>
          <Shell />
        </HashRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}
