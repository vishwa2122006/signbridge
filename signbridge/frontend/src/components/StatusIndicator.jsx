import React from "react";
import { Bi } from "./Bilingual.jsx";

const STATUS_CLASS = {
  RECOGNIZED: "recognized",
  UNSTABLE: "processing",
  IDLE: "ready",
  UNCERTAIN: "unclear",
  UNKNOWN_SIGN: "unclear",
  NO_HAND: "waiting",
  NO_MODEL: "waiting",
};

export default function StatusIndicator({ status, messageEn, messageTa }) {
  return (
    <div className={`status-row ${STATUS_CLASS[status] || "waiting"}`} role="status">
      <span className="status-dot" aria-hidden="true" />
      <Bi tamil={messageTa} english={messageEn} />
    </div>
  );
}
