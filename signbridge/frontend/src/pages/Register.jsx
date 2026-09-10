import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AlreadyLoggedIn from "../components/AlreadyLoggedIn.jsx";
import { T } from "../components/Bilingual.jsx";
import CodeEntry from "../components/CodeEntry.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import { useAuth } from "../AuthContext.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { t } from "../i18n.js";

// Same choices as the backend (app/models/schemas.py); labels are i18n keys bg_*, level_*, lang_*.
const BACKGROUNDS = ["deaf", "hard_of_hearing", "interpreter", "teacher", "family", "student", "other"];
const LEVELS = ["native", "fluent", "intermediate", "beginner"];
const SIGN_LANGUAGES = ["tamil", "indian", "both", "other"];

const EMPTY = {
  name: "",
  email: "",
  phone: "",
  city: "",
  organization: "",
  background: "",
  signing_level: "",
  sign_language: "",
  about: "",
  password: "",
  confirm: "",
  consent: false,
};

/** Becoming a trainer: details, then the code emailed to confirm the address. */
export default function Register() {
  const { lang } = useLanguage();
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [codeInfo, setCodeInfo] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (user && !codeInfo) return <AlreadyLoggedIn />;

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  const details = () => {
    const payload = { ...form, email: form.email.trim() };
    delete payload.confirm;
    return payload;
  };

  const submit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) return setError({ key: "passwordsDontMatch" });
    setBusy(true);
    setError(null);
    try {
      setCodeInfo(await api.register(details()));
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  const verify = async (code) => {
    signIn(await api.verifyRegistration(codeInfo.email, code));
    navigate("/teach", { replace: true, state: { welcome: true } });
  };

  const select = (field, labelKey, options, prefix) => (
    <label className="field">
      <span>
        <T k={labelKey} /> *
      </span>
      <select required value={form[field]} onChange={update(field)}>
        <option value="">{t("choose", lang)}</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {t(`${prefix}${option}`, lang)}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <div className="auth-page wide">
      <div className="card accent warm auth-card">
        <h2 className="page-title">
          🎓 <T k="registerTitle" />
        </h2>
        <p className="dim">
          <T k="registerIntro" />
        </p>

        {codeInfo ? (
          <CodeEntry
            email={codeInfo.email}
            length={codeInfo.otp_length}
            resendAfter={codeInfo.resend_after}
            onVerify={verify}
            onResend={() => api.register(details())}
            onBack={() => setCodeInfo(null)}
          />
        ) : (
          <form className="auth-form" onSubmit={submit}>
            <fieldset className="form-grid">
              <legend>
                👤 <T k="aboutYou" />
              </legend>
              <label className="field">
                <span>
                  <T k="fullName" /> *
                </span>
                <input required minLength={2} maxLength={80} autoComplete="name" value={form.name} onChange={update("name")} />
              </label>
              <label className="field">
                <span>
                  <T k="email" /> *
                </span>
                <input type="email" required maxLength={254} autoComplete="email" value={form.email} onChange={update("email")} />
              </label>
              <label className="field">
                <span>
                  <T k="phone" /> *
                </span>
                <input
                  type="tel"
                  required
                  pattern="[+]?[0-9 ()\-]{10,20}"
                  maxLength={20}
                  autoComplete="tel"
                  placeholder="98765 43210"
                  value={form.phone}
                  onChange={update("phone")}
                />
              </label>
              <label className="field">
                <span>
                  <T k="city" /> *
                </span>
                <input required minLength={2} maxLength={80} autoComplete="address-level2" value={form.city} onChange={update("city")} />
              </label>
              <label className="field full">
                <T k="organization" />
                <input maxLength={120} placeholder={t("organizationPlaceholder", lang)} value={form.organization} onChange={update("organization")} />
              </label>
            </fieldset>

            <fieldset className="form-grid">
              <legend>
                🤟 <T k="yourSigning" />
              </legend>
              {select("background", "background", BACKGROUNDS, "bg_")}
              {select("signing_level", "signingLevel", LEVELS, "level_")}
              {select("sign_language", "signLanguage", SIGN_LANGUAGES, "lang_")}
              <label className="field full">
                <T k="about" />
                <textarea rows={2} maxLength={500} value={form.about} onChange={update("about")} />
              </label>
            </fieldset>

            <fieldset className="form-grid">
              <legend>
                🔑 <T k="password" />
              </legend>
              <label className="field">
                <span>
                  <T k="password" /> *
                </span>
                <input type="password" required minLength={6} maxLength={72} autoComplete="new-password" value={form.password} onChange={update("password")} />
                <span className="small">
                  <T k="passwordHint" />
                </span>
              </label>
              <label className="field">
                <span>
                  <T k="confirmPassword" /> *
                </span>
                <input type="password" required minLength={6} maxLength={72} autoComplete="new-password" value={form.confirm} onChange={update("confirm")} />
              </label>
            </fieldset>

            <label className="checkbox">
              <input type="checkbox" required checked={form.consent} onChange={update("consent")} />
              <T k="consentText" />
            </label>
            <ErrorNote error={error} />
            <button type="submit" className="warm" disabled={busy}>
              {busy ? <span className="spinner" /> : "✉️"} <T k="registerAndSendCode" />
            </button>
          </form>
        )}

        <p className="auth-switch dim">
          <T k="haveAccount" />{" "}
          <Link to="/login">
            <T k="logInLink" />
          </Link>
        </p>
      </div>
    </div>
  );
}
