import React from "react";
import { Bi, T } from "./Bilingual.jsx";

export default function EmergencyBanner({ englishText, tamilText }) {
  return (
    <div className="emergency-banner" role="alert">
      <span className="siren">🚨</span>
      <div>
        <div className="emergency-title">
          <T k="emergencyAlertTitle" />
        </div>
        <Bi tamil={tamilText} english={englishText} />
      </div>
    </div>
  );
}
