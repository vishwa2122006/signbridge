import React from "react";
import { useLanguage } from "../LanguageContext.jsx";

const STATUS_MAP = {
  RECOGNIZED: { dot: "recognized", emoji: "🟢" },
  UNSTABLE: { dot: "processing", emoji: "🟡" },
  UNCERTAIN: { dot: "unclear", emoji: "🔴" },
  UNKNOWN_SIGN: { dot: "unclear", emoji: "🔴" },
  NO_HAND: { dot: "waiting", emoji: "⚪" },
  NO_MODEL: { dot: "waiting", emoji: "⚪" },
};

export default function StatusIndicator({ status, messageEn, messageTa }) {
  const { lang } = useLanguage();
  const cfg = STATUS_MAP[status] || STATUS_MAP.NO_HAND;
  const message = lang === "en" ? messageEn : lang === "ta" ? messageTa : `${messageTa} / ${messageEn}`;
  return (
    <div className="status-row">
      <span className={`status-dot ${cfg.dot}`} aria-hidden="true" />
      <span>{cfg.emoji} {message}</span>
    </div>
  );
}
