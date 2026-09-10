import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import AlreadyLoggedIn from "../components/AlreadyLoggedIn.jsx";
import { T } from "../components/Bilingual.jsx";
import CodeEntry from "../components/CodeEntry.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import { useAuth } from "../AuthContext.jsx";
import { api } from "../api.js";

/** Trainer and admin login: with a password, or with a one-time code sent by email. */
export default function Login() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState("password"); // password | code
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [codeInfo, setCodeInfo] = useState(null); // the backend's reply once a code was sent
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (user) return <AlreadyLoggedIn />;

  const finish = (auth) => {
    signIn(auth);
    const from = location.state?.from;
    navigate(from || (auth.user.role === "admin" ? "/review" : "/teach"), { replace: true });
  };

  const run = async (action) => {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  const switchMode = (next) => {
    setMode(next);
    setError(null);
  };

  const emailField = (
    <label className="field">
      <T k="email" />
      <input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
    </label>
  );

  return (
    <div className="auth-page">
      <div className="card accent auth-card">
        <h2 className="page-title">
          🔐 <T k="loginTitle" />
        </h2>
        <p className="dim">
          <T k="loginIntro" />
        </p>

        <div className="tabs" role="tablist">
          <button role="tab" aria-selected={mode === "password"} className={mode === "password" ? "active" : ""} onClick={() => switchMode("password")}>
            🔑 <T k="withPassword" />
          </button>
          <button role="tab" aria-selected={mode === "code"} className={mode === "code" ? "active" : ""} onClick={() => switchMode("code")}>
            ✉️ <T k="withEmailCode" />
          </button>
        </div>

        {mode === "password" && (
          <form className="auth-form" onSubmit={(e) => (e.preventDefault(), run(async () => finish(await api.login(email.trim(), password))))}>
            {emailField}
            <label className="field">
              <T k="password" />
              <input type="password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </label>
            <ErrorNote error={error} />
            <button type="submit" disabled={busy}>
              {busy ? <span className="spinner" /> : "➜"} <T k="logIn" />
            </button>
          </form>
        )}

        {mode === "code" && !codeInfo && (
          <form className="auth-form" onSubmit={(e) => (e.preventDefault(), run(async () => setCodeInfo(await api.requestLoginCode(email.trim()))))}>
            {emailField}
            <p className="dim small flush">
              <T k="codeLoginHelp" />
            </p>
            <ErrorNote error={error} />
            <button type="submit" disabled={busy}>
              {busy ? <span className="spinner" /> : "✉️"} <T k="sendCode" />
            </button>
          </form>
        )}

        {mode === "code" && codeInfo && (
          <CodeEntry
            email={codeInfo.email}
            length={codeInfo.otp_length}
            resendAfter={codeInfo.resend_after}
            onVerify={async (code) => finish(await api.loginWithCode(codeInfo.email, code))}
            onResend={() => api.requestLoginCode(codeInfo.email)}
            onBack={() => setCodeInfo(null)}
          />
        )}

        <p className="auth-switch dim">
          <T k="newTrainer" />{" "}
          <Link to="/register">
            <T k="registerLink" />
          </Link>
        </p>
      </div>
    </div>
  );
}
