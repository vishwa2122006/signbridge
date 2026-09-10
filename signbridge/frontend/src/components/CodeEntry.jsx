import React, { useEffect, useState } from "react";
import { T } from "./Bilingual.jsx";
import ErrorNote from "./ErrorNote.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { t } from "../i18n.js";

/**
 * Second step of registering or logging in with an emailed code: the code box,
 * a countdown until another code can be sent, and a way back to fix the email.
 * `onVerify(code)` and `onResend()` return promises; onResend resolves to the
 * backend's `{ resend_after }`.
 */
export default function CodeEntry({ email, length, resendAfter, onVerify, onResend, onBack }) {
  const { lang } = useLanguage();
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [resent, setResent] = useState(false);
  const [wait, setWait] = useState(resendAfter || 0);

  useEffect(() => {
    if (wait <= 0) return undefined;
    const id = setTimeout(() => setWait((w) => w - 1), 1000);
    return () => clearTimeout(id);
  }, [wait]);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onVerify(code);
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  };

  const resend = async () => {
    setError(null);
    setResent(false);
    try {
      const res = await onResend();
      setWait(res.resend_after || 0);
      setCode("");
      setResent(true);
    } catch (err) {
      setError(err);
      if (err.detail?.retry_after) setWait(err.detail.retry_after);
    }
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <p className="flush">
        📧 <T k="codeSentTo" /> <b className="email">{email}</b>
      </p>
      <input
        className="code-input"
        value={code}
        onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, length))}
        inputMode="numeric"
        autoComplete="one-time-code"
        pattern={`\\d{${length}}`}
        maxLength={length}
        placeholder={"•".repeat(length)}
        aria-label={t("code", lang)}
        required
        autoFocus
      />
      <ErrorNote error={error} />
      {resent && (
        <div className="note ok">
          ✉️ <T k="codeResent" />
        </div>
      )}
      <button type="submit" className="teal" disabled={busy || code.length !== length}>
        {busy ? <span className="spinner" /> : "✅"} <T k="verifyCode" />
      </button>
      <div className="auth-links">
        <button type="button" className="link" onClick={resend} disabled={wait > 0}>
          ↻ {wait > 0 ? <T k="resendIn" vars={{ s: wait }} /> : <T k="resendCode" />}
        </button>
        <button type="button" className="link" onClick={onBack}>
          ✏️ <T k="changeEmail" />
        </button>
      </div>
    </form>
  );
}
