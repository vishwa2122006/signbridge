import React, { useEffect, useMemo, useRef, useState } from "react";
import { Bi, T } from "../components/Bilingual.jsx";
import CameraFeed from "../components/CameraFeed.jsx";
import EmergencyBanner from "../components/EmergencyBanner.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import SentenceBuilder from "../components/SentenceBuilder.jsx";
import SignPlayer from "../components/SignPlayer.jsx";
import StatusIndicator from "../components/StatusIndicator.jsx";
import STAFF_PHRASES from "../data/staffPhrases.js";
import { useSignRecognizer } from "../hooks/useSignRecognizer.js";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { categoryStyle } from "../colors.js";
import { STRINGS, t } from "../i18n.js";

const MANUAL_WORD_LIMIT = 40;

const clock = (timestamp) => new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

/** The hearing person's message as hand signs for the signer (collapsible). */
function StaffSigns({ signs, open, onToggle }) {
  if (signs === null) {
    return (
      <div className="bubble-note">
        <span className="spinner" /> <T k="loadingSigns" />
      </div>
    );
  }
  if (!signs?.length) return null;
  return (
    <div className="bubble-signs">
      <button className="link" onClick={onToggle}>
        🤟 <T k={open ? "hideSigns" : "showSigns"} />
      </button>
      {open && <SignPlayer items={signs} />}
    </div>
  );
}

function Bubble({ entry, latest, lang, signsOpen, onToggleSigns }) {
  const signer = entry.who === "signer";
  return (
    <div
      className={`bubble ${entry.who}${latest ? " latest" : ""}${signsOpen ? " with-signs" : ""}`}
      data-entry-id={entry.id}
    >
      <div className="bubble-meta">
        <span>
          {signer ? "🤟" : "🎤"} {t(signer ? "patient" : "staff", lang)}
        </span>
        <span>
          {latest && <span className="latest-tag">{t("latest", lang)}</span>}
          {clock(entry.at)}
        </span>
      </div>
      {entry.text ? (
        <>
          <div className="bubble-main">{entry.text}</div>
          <div className="bubble-note">
            <T k="untranslated" />
          </div>
        </>
      ) : (
        <>
          {lang !== "en" && <div className="bubble-main">{entry.tamil}</div>}
          {lang !== "ta" && <div className={lang === "en" ? "bubble-main" : "bubble-sub"}>{entry.english}</div>}
        </>
      )}
      {!signer && <StaffSigns signs={entry.signs} open={signsOpen} onToggle={onToggleSigns} />}
    </div>
  );
}

/**
 * Three columns on wide screens: the signer's camera | the conversation | both
 * reply boxes stacked (signed words above the hearing person's messages), so
 * either side can send from the same place. The hearing person's messages are
 * shown to the signer as hand signs inside the chat. On narrow screens: camera,
 * signed words, conversation, hearing person.
 */
export default function ConversationMode() {
  const { lang } = useLanguage();
  const recognizer = useSignRecognizer();
  const { result } = recognizer;
  const [cameraOn, setCameraOn] = useState(false);
  const [vocabulary, setVocabulary] = useState([]);
  const [wordSearch, setWordSearch] = useState("");
  const [log, setLog] = useState([]);
  const [openSignsId, setOpenSignsId] = useState(null);
  const [staffText, setStaffText] = useState("");
  const [speechLang, setSpeechLang] = useState("ta");
  const [listening, setListening] = useState(false);
  const [error, setError] = useState(null);
  const nextId = useRef(0);
  const latestStaffId = useRef(null);
  const chatRef = useRef(null);
  const stackRef = useRef(null);
  const stickToBottom = useRef(true);
  const revealId = useRef(null);

  useEffect(() => {
    api
      .listSigns()
      .then((signs) => setVocabulary(signs.filter((s) => s.status === "approved")))
      .catch(() => setVocabulary([]));
  }, []);

  // New messages scroll the chat to the bottom.
  useEffect(() => {
    const chat = chatRef.current;
    if (!chat) return;
    chat.scrollTop = chat.scrollHeight;
    stickToBottom.current = true;
  }, [log]);

  // Messages can grow afterwards (e.g. a sign player loading); stay at the bottom
  // unless the reader has scrolled up to read something older.
  useEffect(() => {
    const chat = chatRef.current;
    const stack = stackRef.current;
    const onScroll = () => {
      stickToBottom.current = chat.scrollHeight - chat.scrollTop - chat.clientHeight < 60;
    };
    const observer = new ResizeObserver(() => {
      if (stickToBottom.current) chat.scrollTop = chat.scrollHeight;
    });
    chat.addEventListener("scroll", onScroll, { passive: true });
    observer.observe(stack);
    return () => {
      chat.removeEventListener("scroll", onScroll);
      observer.disconnect();
    };
  }, []);

  // Opening signs on an older message brings that message into view.
  useEffect(() => {
    if (revealId.current === null) return;
    chatRef.current?.querySelector(`[data-entry-id="${revealId.current}"]`)?.scrollIntoView({ block: "nearest" });
    revealId.current = null;
  }, [openSignsId]);

  const toggleSigns = (id) => {
    stickToBottom.current = false;
    revealId.current = id;
    setOpenSignsId((current) => (current === id ? null : id));
  };

  const manualWords = useMemo(() => {
    const q = wordSearch.trim().toLowerCase();
    const matches = vocabulary.filter((v) => !q || v.english.toLowerCase().includes(q) || v.tamil.includes(q));
    // trained words first: those are the ones the signer can also sign
    return [...matches.filter((v) => v.trained), ...matches.filter((v) => !v.trained)].slice(0, MANUAL_WORD_LIMIT);
  }, [vocabulary, wordSearch]);

  const addEntry = (entry) => {
    const id = nextId.current++;
    setLog((l) => [...l, { ...entry, id, at: Date.now() }]);
    return id;
  };
  const updateEntry = (id, changes) => setLog((l) => l.map((e) => (e.id === id ? { ...e, ...changes } : e)));

  const sendSigned = (sentence) => {
    if (!sentence) return;
    addEntry({ who: "signer", tamil: sentence.tamil, english: sentence.english });
    recognizer.clear();
  };

  /** Adds the hearing person's message, then looks up its words as signs and
   * opens the sign player on it (if it's still the newest message). */
  const sendStaff = (message, textToMatch) => {
    const id = addEntry({ who: "staff", ...message, signs: null });
    latestStaffId.current = id;
    api
      .textToSigns(textToMatch)
      .then((signs) => {
        updateEntry(id, { signs });
        if (latestStaffId.current === id) setOpenSignsId(id);
      })
      .catch(() => updateEntry(id, { signs: [] }));
  };

  const sendTyped = () => {
    const text = staffText.trim();
    if (!text) return;
    sendStaff({ text }, text);
    setStaffText("");
  };

  const clearLog = () => {
    setLog([]);
    setOpenSignsId(null);
    latestStaffId.current = null;
  };

  const dictate = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError({ key: "noSpeechRecognition" });
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = speechLang === "ta" ? "ta-IN" : "en-IN";
    recognition.onresult = (e) => setStaffText(e.results[0][0].transcript);
    recognition.onerror = (e) => setError({ message: e.error });
    recognition.onend = () => setListening(false);
    setError(null);
    setListening(true);
    recognition.start();
  };

  return (
    <div>
      {result?.status === "RECOGNIZED" && result.is_emergency && (
        <EmergencyBanner
          englishText={`${STRINGS.patientSigning.en} ${result.english}`}
          tamilText={`${STRINGS.patientSigning.ta} ${result.tamil}`}
        />
      )}

      <div className="convo-grid">
        {/* Signer: camera + manual word picker */}
        <section className="card accent teal signer-card">
          <div className="panel-head">
            <span className="avatar teal">🤟</span>
            <h3 className="flush">
              <T k="patient" />
            </h3>
            <span className="spacer" />
            <button className="teal small" onClick={() => setCameraOn((on) => !on)}>
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
          </div>
          <CameraFeed active={cameraOn} onWindow={recognizer.onWindow} windowMs={recognizer.windowMs} />
          {result && (
            <StatusIndicator status={result.status} messageEn={result.message_en} messageTa={result.message_ta} />
          )}
          <ErrorNote error={recognizer.error} />

          <details>
            <summary>
              <T k="pickWordsManually" />
            </summary>
            <input
              type="search"
              value={wordSearch}
              onChange={(e) => setWordSearch(e.target.value)}
              placeholder={t("searchWords", lang)}
              className="grow"
            />
            <div className="word-list compact">
              {manualWords.map((v) => (
                <button
                  key={v.sign_id}
                  className="word-btn"
                  style={categoryStyle(v.category)}
                  onClick={() =>
                    recognizer.addWord({
                      concept: v.concept,
                      english: v.english,
                      tamil: v.tamil,
                      is_emergency: v.is_emergency,
                    })
                  }
                >
                  <Bi tamil={v.tamil} english={v.english} />
                </button>
              ))}
            </div>
          </details>
        </section>

        {/* Conversation, between the two people */}
        <section className="card chat-card">
          <div className="chat-head">
            <span className="avatar brand">💬</span>
            <h3 className="flush">
              <T k="conversationLog" />
            </h3>
            {log.length > 0 && <span className="count-badge">{log.length}</span>}
            <span className="spacer" />
            <button className="secondary small" onClick={clearLog} disabled={!log.length}>
              ✕ <T k="clear" />
            </button>
          </div>
          <div className="chat-legend">
            <span className="legend signer">◀ 🤟 {t("patient", lang)}</span>
            <span className="legend staff">
              {t("staff", lang)} 🎤 ▶
            </span>
          </div>
          <div className="chat-body" ref={chatRef} aria-live="polite">
            <div className="chat-stack" ref={stackRef}>
              {log.length === 0 ? (
                <div className="chat-empty">
                  <div className="big">🤟 ⇄ 🎤</div>
                  <T k="conversationEmpty" />
                </div>
              ) : (
                log.map((entry, i) => (
                  <Bubble
                    key={entry.id}
                    entry={entry}
                    latest={i === log.length - 1}
                    lang={lang}
                    signsOpen={openSignsId === entry.id}
                    onToggleSigns={() => toggleSigns(entry.id)}
                  />
                ))
              )}
            </div>
          </div>
        </section>

        {/* Both reply boxes: the signer's signed words above the hearing person's messages */}
        <div className="compose-col">
          <SentenceBuilder
            className="teal compose-card"
            words={recognizer.words}
            onUndo={recognizer.undo}
            onClear={recognizer.clear}
            onSend={sendSigned}
          />

          <section className="card accent warm compose-card hearing-card">
            <div className="panel-head">
              <span className="avatar warm">🎤</span>
              <h3 className="flush">
                <T k="staff" />
              </h3>
              <span className="spacer" />
              <span className="dim small" title={t("quickPhrases", lang)}>
                ⚡ <T k="quickReplies" />
              </span>
            </div>
            <div className="phrase-grid">
              {STAFF_PHRASES.map((phrase) => (
                <button key={phrase.english} className="phrase" onClick={() => sendStaff(phrase, phrase.english)}>
                  <span className="phrase-ta">{phrase.tamil}</span>
                  <span className="phrase-en">{phrase.english}</span>
                </button>
              ))}
            </div>

            <div className="composer">
              <textarea
                value={staffText}
                onChange={(e) => setStaffText(e.target.value)}
                rows={1}
                placeholder={t("typeShort", lang)}
                aria-label={t("typeOrDictate", lang)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendTyped();
                  }
                }}
              />
              <div className="composer-actions">
                <button
                  className={`secondary icon-btn${listening ? " listening" : ""}`}
                  onClick={dictate}
                  disabled={listening}
                  title={t(listening ? "listening" : "dictate", lang)}
                  aria-label={t("dictate", lang)}
                >
                  🎙
                </button>
                <select value={speechLang} onChange={(e) => setSpeechLang(e.target.value)} aria-label="Speech language">
                  <option value="ta">தமிழ்</option>
                  <option value="en">English</option>
                </select>
                <button
                  className="warm icon-btn send-icon"
                  onClick={sendTyped}
                  disabled={!staffText.trim()}
                  title={t("send", lang)}
                  aria-label={t("send", lang)}
                >
                  ➤
                </button>
              </div>
            </div>
            <ErrorNote error={error} />
          </section>
        </div>
      </div>
    </div>
  );
}
