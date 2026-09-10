import React, { useCallback, useEffect, useRef, useState } from "react";
import CameraFeed from "../components/CameraFeed.jsx";
import StatusIndicator from "../components/StatusIndicator.jsx";
import BilingualOutput from "../components/BilingualOutput.jsx";
import EmergencyBanner from "../components/EmergencyBanner.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";

function speak(text, langHint) {
  if (!("speechSynthesis" in window) || !text) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = langHint === "ta" ? "ta-IN" : "en-IN";
  window.speechSynthesis.speak(utter);
}

export default function LiveTranslator() {
  const { lang } = useLanguage();
  const sessionId = useRef(`session_${Math.random().toString(36).slice(2)}`);
  const [cameraOn, setCameraOn] = useState(false);
  const [result, setResult] = useState(null);
  const [modelLoaded, setModelLoaded] = useState(null);
  const [simMode, setSimMode] = useState(false);
  const [demoSigns, setDemoSigns] = useState([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.health().then((h) => setModelLoaded(h.model_loaded)).catch(() => setModelLoaded(null));
    api.demoPrioritySigns().then(setDemoSigns).catch(() => setDemoSigns([]));
  }, []);

  const handleWindowReady = useCallback(async (window) => {
    try {
      const res = await api.predict(sessionId.current, window);
      setResult(res);
    } catch (e) {
      // Network/backend errors surface as a visible message, never as a
      // silent guessed recognition.
      setResult({
        status: "NO_MODEL",
        message_en: `Backend unavailable: ${e.message}`,
        message_ta: "பின்தள சேவை கிடைக்கவில்லை.",
      });
    }
  }, []);

  const runSimulation = async (signId) => {
    setBusy(true);
    try {
      const res = await api.predictSimulate(sessionId.current, signId);
      setResult(res);
    } finally {
      setBusy(false);
    }
  };

  const reset = async () => {
    await api.resetSession(sessionId.current);
    setResult(null);
  };

  return (
    <div>
      <div className="disclaimer-banner">
        {lang !== "en"
          ? "தொடர்பு உதவி மட்டுமே. இது மருத்துவ நோய் கண்டறிதல் அல்ல."
          : "Communication assistance only. This is not a medical diagnosis."}
      </div>

      {result?.is_emergency && (
        <EmergencyBanner englishText={result.english ? `Patient is requesting: ${result.english}` : ""} tamilText={result.tamil ? `நோயாளிக்கு தேவை: ${result.tamil}` : ""} />
      )}

      <div className="card">
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center", marginBottom: "1rem" }}>
          <button onClick={() => setCameraOn((v) => !v)}>
            {cameraOn ? "⏹ " + (lang !== "en" ? "கேமராவை நிறுத்து" : "Stop Camera") : "📷 " + (lang !== "en" ? "கேமராவைத் தொடங்கு" : "Start Camera")}
          </button>
          <button className="secondary" onClick={reset}>
            🔁 {lang !== "en" ? "மீண்டும் தொடங்கு" : "Reset"}
          </button>
          <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginLeft: "auto", fontSize: "0.9rem" }}>
            <input type="checkbox" checked={simMode} onChange={(e) => setSimMode(e.target.checked)} />
            {lang !== "en" ? "உருவகப்படுத்தல் முறை (டெமோ)" : "Simulation Mode (demo, not live camera)"}
          </label>
        </div>

        {modelLoaded === false && !simMode && (
          <div className="disclaimer-banner">
            {lang !== "en"
              ? "இன்னும் பயிற்சி பெற்ற மாதிரி இல்லை. கேமரா மற்றும் கை-கண்காணிப்பு இயங்கும், ஆனால் அடையாளங்கள் இன்னும் அங்கீகரிக்கப்படாது. கீழே உள்ள உருவகப்படுத்தல் முறையை முயற்சிக்கவும்."
              : "No trained model is loaded yet — camera and hand-tracking will run, but signs won't be recognized. Try Simulation Mode below to see how the full flow works once a model is trained."}
          </div>
        )}

        {simMode ? (
          <div>
            <p style={{ color: "var(--text-dim)" }}>
              {lang !== "en"
                ? "ஒரு அடையாளத்தைத் தேர்ந்தெடுத்து முழு பின்தொடர் ஓட்டத்தைக் காணவும் (உண்மையான கேமரா அங்கீகாரம் அல்ல)."
                : "Pick a sign to walk through the full downstream flow (not real camera recognition)."}
            </p>
            <div className="grid cols-3">
              {demoSigns.map((s) => (
                <button key={s.sign_id} disabled={busy} onClick={() => runSimulation(s.sign_id)} className="secondary">
                  {s.tamil} / {s.english}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <CameraFeed active={cameraOn} onWindowReady={handleWindowReady} />
        )}
      </div>

      <div className="card">
        {result ? (
          <>
            <StatusIndicator status={result.status} messageEn={result.message_en} messageTa={result.message_ta} />
            {result.simulated && (
              <p style={{ color: "var(--warn)", fontWeight: 700 }}>
                {lang !== "en" ? "(உருவகப்படுத்தப்பட்டது — உண்மையான அங்கீகாரம் அல்ல)" : "(SIMULATED — not a real recognition)"}
              </p>
            )}
            <BilingualOutput
              tamil={result.tamil}
              english={result.english}
              onSpeak={result.tamil || result.english ? () => speak(lang === "en" ? result.english : result.tamil, lang === "en" ? "en" : "ta") : null}
            />
            {typeof result.confidence === "number" && (
              <p>{lang !== "en" ? "நம்பகத்தன்மை" : "Confidence"}: {(result.confidence * 100).toFixed(0)}%</p>
            )}
          </>
        ) : (
          <StatusIndicator status="NO_HAND" messageEn="Position your hands inside the camera area." messageTa="உங்கள் கைகளை கேமரா பகுதிக்குள் வையுங்கள்." />
        )}
      </div>
    </div>
  );
}
