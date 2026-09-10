import React, { useEffect, useRef, useState } from "react";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";

export default function DatasetMode() {
  const { lang } = useLanguage();
  const [vocabulary, setVocabulary] = useState([]);
  const [signId, setSignId] = useState("");
  const [signerId, setSignerId] = useState("");
  const [source, setSource] = useState("community_collected");
  const [consent, setConsent] = useState(false);
  const [recording, setRecording] = useState(false);
  const [clipUrl, setClipUrl] = useState(null);
  const [savedMsg, setSavedMsg] = useState("");

  const [fbSignId, setFbSignId] = useState("");
  const [fbPrediction, setFbPrediction] = useState("");
  const [fbValidatorId, setFbValidatorId] = useState("");
  const [fbComment, setFbComment] = useState("");
  const [fbMsg, setFbMsg] = useState("");

  const videoRef = useRef(null);
  const recorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  useEffect(() => {
    api.listSigns().then(setVocabulary).catch(() => setVocabulary([]));
  }, []);

  const startPreviewAndRecord = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    streamRef.current = stream;
    videoRef.current.srcObject = stream;
    await videoRef.current.play();

    chunksRef.current = [];
    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "video/webm" });
      setClipUrl(URL.createObjectURL(blob));
      stream.getTracks().forEach((t) => t.stop());
    };
    recorderRef.current = recorder;
    recorder.start();
    setRecording(true);
    setClipUrl(null);
  };

  const stopRecording = () => {
    recorderRef.current?.stop();
    setRecording(false);
  };

  const saveMetadata = async () => {
    if (!consent || !signId || !signerId) return;
    const entry = await api.registerDatasetSample({
      sign_id: signId,
      signer_id: signerId,
      source,
      consent_confirmed: consent,
    });
    setSavedMsg(
      lang !== "en"
        ? `மெட்டாடேட்டா பதிவு செய்யப்பட்டது. வீடியோவைப் பதிவிறக்கி dataset/raw/${signId}/${signerId}/ இல் வைக்கவும்.`
        : `Metadata registered. Download the clip and place it under dataset/raw/${signId}/${signerId}/.`
    );
  };

  const submitFeedback = async () => {
    if (!fbSignId || !fbValidatorId) return;
    await api.submitFeedback({
      validator_id: fbValidatorId,
      sign_id: fbSignId,
      prediction: fbPrediction || fbSignId,
      decision: fbDecision,
      comment: fbComment || null,
    });
    setFbMsg(lang !== "en" ? "சமர்ப்பிக்கப்பட்டது. நன்றி!" : "Submitted. Thank you!");
  };

  const [fbDecision, setFbDecision] = useState("unsure");

  return (
    <div>
      <div className="emergency-banner" style={{ background: "#1a2440", borderColor: "var(--accent-2)" }}>
        🔬 {lang !== "en" ? "தரவுத்தொகுப்பு சேகரிப்பு முறை" : "DATA COLLECTION MODE"}
      </div>

      <div className="card">
        <h3>{lang !== "en" ? "புதிய மாதிரியைப் பதிவு செய்" : "Record a new sample"}</h3>
        <p style={{ color: "var(--text-dim)", fontSize: "0.9rem" }}>
          {lang !== "en"
            ? "வெளிப்படையான ஒப்புதலுக்குப் பிறகு மட்டுமே பதிவு செய்யப்படும். இந்த முன்மாதிரி வீடியோவை ரகசியமாக பதிவு செய்யாது."
            : "Nothing is recorded without explicit consent below. This prototype never secretly records — you control start/stop, and metadata is only saved once you confirm consent."}
        </p>

        <div className="grid cols-2" style={{ marginBottom: "1rem" }}>
          <label>
            {lang !== "en" ? "அடையாளம்" : "Sign"}
            <select value={signId} onChange={(e) => setSignId(e.target.value)} style={{ width: "100%", padding: "0.5em", marginTop: "0.3em" }}>
              <option value="">--</option>
              {vocabulary.map((v) => <option key={v.sign_id} value={v.sign_id}>{v.tamil} / {v.english}</option>)}
            </select>
          </label>
          <label>
            {lang !== "en" ? "பதிவு செய்பவர் ஐடி (அநாமதேயம்)" : "Signer ID (anonymized)"}
            <input value={signerId} onChange={(e) => setSignerId(e.target.value)} placeholder="signer_03"
                   style={{ width: "100%", padding: "0.5em", marginTop: "0.3em" }} />
          </label>
          <label>
            {lang !== "en" ? "மொழி / மூலம்" : "Source"}
            <input value={source} onChange={(e) => setSource(e.target.value)}
                   style={{ width: "100%", padding: "0.5em", marginTop: "0.3em" }} />
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5em", marginTop: "1.4em" }}>
            <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
            {lang !== "en" ? "பங்கேற்பாளர் ஒப்புதல் பெறப்பட்டது" : "Participant consent obtained"}
          </label>
        </div>

        <video ref={videoRef} playsInline muted style={{ width: "100%", maxWidth: 480, background: "#000", borderRadius: 10 }} />

        <div style={{ display: "flex", gap: "0.6rem", marginTop: "0.75rem", flexWrap: "wrap" }}>
          <button onClick={startPreviewAndRecord} disabled={recording || !consent}>
            ⏺ {lang !== "en" ? "பதிவைத் தொடங்கு" : "Start Recording"}
          </button>
          <button className="danger" onClick={stopRecording} disabled={!recording}>
            ⏹ {lang !== "en" ? "நிறுத்து" : "Stop"}
          </button>
          {clipUrl && (
            <a href={clipUrl} download={`${signId || "sample"}_${signerId || "signer"}.webm`}>
              <button className="secondary">⬇ {lang !== "en" ? "பதிவிறக்கு" : "Download clip"}</button>
            </a>
          )}
          <button onClick={saveMetadata} disabled={!consent || !signId || !signerId}>
            💾 {lang !== "en" ? "மெட்டாடேட்டாவை சேமி" : "Save metadata"}
          </button>
        </div>
        {!consent && <p style={{ color: "var(--warn)", fontSize: "0.85rem" }}>
          {lang !== "en" ? "பதிவு செய்ய ஒப்புதல் தேவை." : "Consent is required before recording is enabled."}
        </p>}
        {savedMsg && <p style={{ color: "var(--ok)" }}>{savedMsg}</p>}
      </div>

      <div className="card">
        <h3>✅ {lang !== "en" ? "சமூக சரிபார்ப்பு" : "Community Validation"}</h3>
        <p style={{ color: "var(--text-dim)", fontSize: "0.9rem" }}>
          {lang !== "en"
            ? "சமூக சரிபார்ப்பு மாதிரி நம்பகத்தன்மையை விட முக்கியமானதாகக் கருதப்படுகிறது."
            : "Community validation is treated as more important than raw model confidence."}
        </p>
        <div className="grid cols-2" style={{ marginBottom: "0.75rem" }}>
          <label>
            {lang !== "en" ? "சரிபார்ப்பாளர் ஐடி" : "Validator ID"}
            <input value={fbValidatorId} onChange={(e) => setFbValidatorId(e.target.value)}
                   style={{ width: "100%", padding: "0.5em", marginTop: "0.3em" }} />
          </label>
          <label>
            {lang !== "en" ? "அடையாளம்" : "Sign"}
            <select value={fbSignId} onChange={(e) => setFbSignId(e.target.value)} style={{ width: "100%", padding: "0.5em", marginTop: "0.3em" }}>
              <option value="">--</option>
              {vocabulary.map((v) => <option key={v.sign_id} value={v.sign_id}>{v.tamil} / {v.english}</option>)}
            </select>
          </label>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
          {["correct", "incorrect", "different_sign", "unsure"].map((d) => (
            <button key={d} className={fbDecision === d ? "" : "secondary"} onClick={() => setFbDecision(d)}>
              {d.replace("_", " ")}
            </button>
          ))}
        </div>
        <textarea value={fbComment} onChange={(e) => setFbComment(e.target.value)} rows={2}
                  placeholder={lang !== "en" ? "குறிப்புகள் (விருப்பம்)" : "Notes (optional)"}
                  style={{ width: "100%", padding: "0.5em", borderRadius: 8, marginBottom: "0.75rem" }} />
        <button onClick={submitFeedback} disabled={!fbSignId || !fbValidatorId}>
          {lang !== "en" ? "சமர்ப்பி" : "Submit"}
        </button>
        {fbMsg && <p style={{ color: "var(--ok)" }}>{fbMsg}</p>}
      </div>
    </div>
  );
}
