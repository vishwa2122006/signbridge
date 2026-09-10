import React from "react";
import { Bi, T } from "./Bilingual.jsx";

// Backend error codes the UI explains in the current language.
const CODE_KEYS = {
  offline: "backendOffline",
  busy: "trainingBusy",
  no_hands: "noHandsInRecording",
  invalid_credentials: "errInvalidCredentials",
  email_not_verified: "errEmailNotVerified",
  account_disabled: "errAccountDisabled",
  email_taken: "errEmailTaken",
  no_account: "errNoAccount",
  already_verified: "errAlreadyVerified",
  otp_invalid: "errOtpInvalid",
  otp_expired: "errOtpExpired",
  otp_too_many_attempts: "errOtpTooMany",
  otp_cooldown: "errOtpCooldown",
  email_failed: "errEmailFailed",
  login_required: "errLoginRequired",
  session_expired: "errSessionExpired",
  admin_only: "errAdminOnly",
  wrong_password: "errWrongPassword",
  word_exists: "errWordExists",
  word_pending: "errWordPending",
  word_not_approved: "errWordNotApproved",
  nothing_to_submit: "errNothingToSubmit",
  no_recordings: "errNoRecordings",
  already_reviewed: "errAlreadyReviewed",
  not_allowed: "errNotAllowed",
};

/**
 * Shows an error readably in the current language. Accepts an ApiError from
 * api.js, `{ key, vars }` for a UI string, `{ message }`, or a plain string.
 * `wordOf(concept) -> { tamil, english }` names words in per-word details.
 */
export default function ErrorNote({ error, wordOf }) {
  if (!error) return null;
  if (typeof error === "string") return <div className="note error" role="alert">⚠️ {error}</div>;

  const detail = error.detail;
  const key = error.key || CODE_KEYS[detail?.code];
  if (key) {
    return (
      <div className="note error" role="alert">
        ⚠️ <T k={key} vars={error.vars || detail} />
      </div>
    );
  }

  if (detail?.code === "sign_already_used") {
    const word = wordOf?.(detail.word) ?? { english: detail.english, tamil: detail.tamil };
    return (
      <div className="note error" role="alert">
        ⚠️{" "}
        <T
          k={detail.recorded === "_none" ? "errIdleLooksLikeSign" : "errSignAlreadyUsed"}
          vars={{ pct: Math.round(detail.confidence * 100) }}
        />
        <span className="chips inline">
          <span className="chip low">
            <Bi {...word} />
          </span>
        </span>
      </div>
    );
  }

  if (detail?.code === "not_enough_data") {
    const counts = Object.entries(detail.counts || {}).sort((a, b) => b[1] - a[1]);
    return (
      <div className="note error" role="alert">
        <div>
          ⚠️ <T k="notEnoughData" vars={{ min: detail.min_samples }} />
        </div>
        {counts.length > 0 && (
          <div className="chips">
            {counts.map(([concept, count]) => (
              <span key={concept} className={`chip ${count >= detail.min_samples ? "ok" : "low"}`}>
                {wordOf ? <Bi {...wordOf(concept)} /> : concept}
                <b>
                  {count}/{detail.min_samples}
                </b>
              </span>
            ))}
          </div>
        )}
      </div>
    );
  }

  return <div className="note error" role="alert">⚠️ {error.message || String(error)}</div>;
}
