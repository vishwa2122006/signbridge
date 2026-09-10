import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { T } from "../components/Bilingual.jsx";
import BilingualOutput from "../components/BilingualOutput.jsx";
import CameraFeed from "../components/CameraFeed.jsx";
import EmergencyBanner from "../components/EmergencyBanner.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import SentenceBuilder from "../components/SentenceBuilder.jsx";
import StatusIndicator from "../components/StatusIndicator.jsx";
import { useAuth } from "../AuthContext.jsx";
import { useSignRecognizer } from "../hooks/useSignRecognizer.js";
import { useLanguage } from "../LanguageContext.jsx";
import { OFFLINE_ERROR, api } from "../api.js";
import { STRINGS } from "../i18n.js";
import { speakBilingual } from "../speech.js";

export default function Translate() {
  const { lang } = useLanguage();
  const { user, isAdmin } = useAuth();
  const [cameraOn, setCameraOn] = useState(false);
  const [health, setHealth] = useState(undefined); // undefined = loading, null = backend offline
  const recognizer = useSignRecognizer();
  const { result, words } = recognizer;

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  const lastWord = words[words.length - 1];
  const emergency = result?.status === "RECOGNIZED" && result.is_emergency;
  const confidence = result?.status === "RECOGNIZED" && typeof result.confidence === "number"
    ? Math.round(result.confidence * 100)
    : null;

  return (
    <div>
      {health === null && <ErrorNote error={OFFLINE_ERROR} />}

      {health && !health.model_loaded && (
        <div className="card accent warm">
          <div className="notice-row">
            <div className="notice-icon">🎓</div>
            <div>
              <h3 className="flush">
                <T k="noModelTitle" />
              </h3>
              <p className="dim flush">
                <T k={isAdmin ? "noModelBodyAdmin" : user ? "noModelBodyTrainer" : "noModelBody"} />
              </p>
            </div>
            {user && (
              <Link to={isAdmin ? "/review" : "/teach"}>
                <button className="warm">
                  <T k={isAdmin ? "goReview" : "goTeach"} /> ➜
                </button>
              </Link>
            )}
          </div>
        </div>
      )}

      {emergency && (
        <EmergencyBanner
          englishText={`${STRINGS.patientSigning.en} ${result.english}`}
          tamilText={`${STRINGS.patientSigning.ta} ${result.tamil}`}
        />
      )}

      <div className="page-head">
        <h2 className="page-title">
          🤟 <T k="navTranslate" />
        </h2>
      </div>

      <div className="grid cols-2">
        <div className="card accent teal">
          <div className="toolbar">
            <button className="teal" onClick={() => setCameraOn((on) => !on)}>
              {cameraOn ? (
                <>
                  ⏹ <T k="stopCamera" />
                </>
              ) : (
                <>
                  📷 <T k="startCamera" />
                </>
              )}
            </button>
            <button className="secondary" onClick={recognizer.reset}>
              🔁 <T k="reset" />
            </button>
          </div>
          <CameraFeed active={cameraOn} onWindow={recognizer.onWindow} />
        </div>

        <div className="card spotlight">
          {result ? (
            <StatusIndicator status={result.status} messageEn={result.message_en} messageTa={result.message_ta} />
          ) : (
            <div className="status-row waiting">
              <span className="status-dot" aria-hidden="true" />
              <T k="waitingForCamera" />
            </div>
          )}
          <ErrorNote error={recognizer.error} />

          <div className="spotlight-word" key={words.length}>
            {lastWord ? (
              <BilingualOutput
                tamil={lastWord.tamil}
                english={lastWord.english}
                onSpeak={() => speakBilingual(lastWord, lang)}
              />
            ) : (
              <div className="spotlight-empty">✋</div>
            )}
          </div>

          {confidence !== null && (
            <div>
              <div className="meter">
                <span style={{ width: `${confidence}%` }} />
              </div>
              <div className="small dim">
                <T k="confidence" /> {confidence}%
              </div>
            </div>
          )}
          {health?.model?.words && (
            <div className="known small dim">
              <span className="count-pill">{health.model.words.length}</span>
              <T k="wordsKnown" />
            </div>
          )}
        </div>
      </div>

      <SentenceBuilder words={words} onUndo={recognizer.undo} onClear={recognizer.clear} />
    </div>
  );
}
