import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { T } from "../components/Bilingual.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import { useAuth } from "../AuthContext.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { formatDate, t } from "../i18n.js";

const EMPTY = { current: "", next: "", confirm: "" };

export default function Account() {
  const { lang } = useLanguage();
  const { user, signIn, signOut } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [changed, setChanged] = useState(false);

  const rows = [
    ["email", user.email],
    ["phone", user.phone],
    ["city", user.city],
    ["organizationLabel", user.organization],
    ["background", user.background && t(`bg_${user.background}`, lang)],
    ["signingLevel", user.signing_level && t(`level_${user.signing_level}`, lang)],
    ["signLanguage", user.sign_language && t(`lang_${user.sign_language}`, lang)],
    ["joined", formatDate(user.created_at, lang)],
  ].filter(([, value]) => value);

  const submit = async (e) => {
    e.preventDefault();
    setChanged(false);
    if (form.next !== form.confirm) return setError({ key: "passwordsDontMatch" });
    setBusy(true);
    setError(null);
    try {
      signIn(await api.changePassword(form.current, form.next));
      setForm(EMPTY);
      setChanged(true);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  const field = (key, labelKey, autoComplete) => (
    <label className="field">
      <T k={labelKey} />
      <input
        type="password"
        required
        minLength={key === "current" ? 1 : 6}
        maxLength={72}
        autoComplete={autoComplete}
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
      />
    </label>
  );

  return (
    <div>
      <div className="page-head">
        <h2 className="page-title">
          👤 <T k="navAccount" />
        </h2>
      </div>
      <div className="grid cols-2">
        <div className="card accent">
          <div className="profile-head">
            <span className="avatar brand">{user.name.slice(0, 1).toUpperCase()}</span>
            <div>
              <h3 className="flush">{user.name}</h3>
              <span className={`role-tag ${user.role}`}>{t(user.role === "admin" ? "roleAdmin" : "roleTrainer", lang)}</span>
            </div>
          </div>
          <dl className="details">
            {rows.map(([key, value]) => (
              <div key={key}>
                <dt>
                  <T k={key} />
                </dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          <button
            className="secondary"
            onClick={() => {
              navigate("/");
              signOut();
            }}
          >
            🚪 <T k="logOut" />
          </button>
        </div>

        <form className="card accent teal auth-form" onSubmit={submit}>
          <h3 className="flush">
            🔑 <T k="changePassword" />
          </h3>
          <p className="dim small flush">
            <T k="changePasswordHint" />
          </p>
          {field("current", "currentPassword", "current-password")}
          {field("next", "newPassword", "new-password")}
          {field("confirm", "confirmPassword", "new-password")}
          <ErrorNote error={error} />
          {changed && (
            <div className="note ok">
              ✅ <T k="passwordChanged" />
            </div>
          )}
          <button type="submit" className="teal" disabled={busy}>
            {busy ? <span className="spinner" /> : "💾"} <T k="changePassword" />
          </button>
        </form>
      </div>
    </div>
  );
}
