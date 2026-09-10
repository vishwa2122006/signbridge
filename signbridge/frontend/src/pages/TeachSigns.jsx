import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Bi, T } from "../components/Bilingual.jsx";
import CameraFeed from "../components/CameraFeed.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import { useAuth } from "../AuthContext.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { categoryStyle } from "../colors.js";
import { STRINGS, t } from "../i18n.js";

const NONE = "_none";
// Slow or two-part signs need longer recordings. The live translator watches each
// word for about as long as its recordings last, so one word should keep one length.
const RECORD_LENGTHS_MS = [1500, 2000, 3000, 4000, 5000, 6000];
const RECORD_LENGTH_KEY = "signbridge.recordMs";
const COUNTDOWN_STEP_MS = 600;
const BURST_SIZE = 10;
const MIN_SAMPLES = 5;
const EMPTY_WORD = { english: "", tamil: "", category: "CUSTOM", is_emergency: false };
const TRAINER_COLUMNS = ["draft", "pending", "approved", "rejected"];

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const seconds = (ms) => `${ms / 1000} s`;
const closestLength = (ms) => RECORD_LENGTHS_MS.reduce((best, len) => (Math.abs(len - ms) < Math.abs(best - ms) ? len : best));

function readRecordLength() {
  try {
    const ms = Number(localStorage.getItem(RECORD_LENGTH_KEY));
    return RECORD_LENGTHS_MS.includes(ms) ? ms : RECORD_LENGTHS_MS[0];
  } catch {
    return RECORD_LENGTHS_MS[0];
  }
}

function StatusCount({ status, n }) {
  return n ? <span className={`status-pill ${status}`}>{n}</span> : <span className="dim">0</span>;
}

/**
 * Recording signs, for trainers and admins. A trainer's recordings are private
 * drafts until submitted for review; an admin's are approved straight away.
 * The model is trained on the Review page, from approved recordings only.
 */
export default function TeachSigns() {
  const { lang } = useLanguage();
  const { user, isAdmin } = useAuth();
  const location = useLocation();
  const [signs, setSigns] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [selected, setSelected] = useState(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [phase, setPhase] = useState("idle"); // idle | countdown | recording | saving
  const [countdown, setCountdown] = useState(0);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null); // { concept, count } after saving, { concept, added } after adding
  const [listError, setListError] = useState(null);
  const [submitted, setSubmitted] = useState(null); // how many drafts were just submitted
  const [submitting, setSubmitting] = useState(false);
  const [newWord, setNewWord] = useState(EMPTY_WORD);
  const [recordMs, setRecordMs] = useState(readRecordLength);

  const framesRef = useRef([]);
  const recordingRef = useRef(false);
  const aspectRef = useRef(4 / 3);
  const stopRef = useRef(false);

  const refresh = useCallback(
    () =>
      Promise.all([api.listSigns(), api.sampleStats()]).then(([signList, sampleStats]) => {
        setSigns(signList);
        setStats(sampleStats);
      }),
    [],
  );

  useEffect(() => {
    refresh().catch(setError);
    api.categories().then(setCategories).catch(() => {});
  }, [refresh]);

  useEffect(() => {
    try {
      localStorage.setItem(RECORD_LENGTH_KEY, String(recordMs));
    } catch {
      // storage unavailable - the length just won't be remembered
    }
  }, [recordMs]);

  const onFrame = useCallback((frame, aspect) => {
    aspectRef.current = aspect;
    if (recordingRef.current) framesRef.current.push(frame);
  }, []);

  const bySlug = useMemo(() => Object.fromEntries(signs.map((s) => [s.concept, s])), [signs]);
  const wordOf = useCallback(
    (concept) => {
      if (concept === NONE) return { tamil: STRINGS.idleSign.ta, english: STRINGS.idleSign.en };
      const sign = bySlug[concept];
      return sign ? { tamil: sign.tamil, english: sign.english } : { tamil: concept, english: concept };
    },
    [bySlug],
  );
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return signs.filter(
      (s) => (!category || s.category === category) && (!q || s.english.toLowerCase().includes(q) || s.tamil.includes(q)),
    );
  }, [signs, search, category]);

  /** Recordings that count for a word: every approved one for an admin; a trainer's own that aren't rejected. */
  const countFor = useCallback(
    (concept) => {
      const s = stats[concept];
      if (!s) return 0;
      return isAdmin ? s.approved_total : s.mine.draft + s.mine.pending + s.mine.approved;
    },
    [stats, isAdmin],
  );

  /** Selects a word and switches to the length its recordings already use. */
  const selectWord = (concept) => {
    setSelected(concept);
    const typical = stats[concept]?.typical_ms;
    if (typical) setRecordMs(closestLength(typical));
  };

  const recordOne = async (concept, countdownSteps) => {
    for (let n = countdownSteps; n > 0; n--) {
      setPhase("countdown");
      setCountdown(n);
      await sleep(COUNTDOWN_STEP_MS);
      if (stopRef.current) return false;
    }
    framesRef.current = [];
    recordingRef.current = true;
    setPhase("recording");
    await sleep(recordMs);
    recordingRef.current = false;
    if (stopRef.current) return false;

    if (framesRef.current.length < 5) {
      setError({ key: "cameraNotReady" });
      return false;
    }
    setPhase("saving");
    try {
      await api.createSample({ concept, frames: framesRef.current, aspect: aspectRef.current });
      return true;
    } catch (e) {
      setError(e);
      return false;
    }
  };

  const record = async (count) => {
    if (!selected) return setError({ key: "selectWordFirst" });
    stopRef.current = false;
    setError(null);
    setNotice(null);
    let saved = 0;
    for (let i = 0; i < count && !stopRef.current; i++) {
      setProgress({ done: i, total: count });
      if (!(await recordOne(selected, i === 0 ? 3 : 1))) break;
      saved++;
    }
    setPhase("idle");
    setProgress(null);
    if (saved) setNotice({ concept: selected, count: saved });
    refresh().catch(() => {});
  };

  const deleteLast = async (concept) => {
    const last = stats[concept]?.last_id;
    if (!last) return;
    try {
      await api.deleteSample(last);
      await refresh();
    } catch (e) {
      setListError(e);
    }
  };

  const submitDrafts = async () => {
    setSubmitting(true);
    setListError(null);
    setSubmitted(null);
    try {
      setSubmitted((await api.submitSamples()).submitted);
      await refresh();
    } catch (e) {
      setListError(e);
    } finally {
      setSubmitting(false);
    }
  };

  const addWord = async (e) => {
    e.preventDefault();
    try {
      const row = await api.createSign(newWord);
      setNewWord(EMPTY_WORD);
      await refresh();
      api.categories().then(setCategories).catch(() => {});
      setSelected(row.concept);
      setError(null);
      setNotice({ concept: row.concept, added: true });
    } catch (err) {
      setError(err);
    }
  };

  const busy = phase !== "idle";
  const recorded = Object.entries(stats)
    .filter(([, s]) => Object.values(s.mine).some(Boolean) || (isAdmin && s.approved_total > 0))
    .sort(([a], [b]) => wordOf(a).english.localeCompare(wordOf(b).english));
  const drafts = Object.values(stats).reduce((n, s) => n + s.mine.draft, 0);
  const selectedHue = selected === NONE ? { "--hue": 250 } : categoryStyle(bySlug[selected]?.category);
  const typicalLength = selected && stats[selected]?.typical_ms ? closestLength(stats[selected].typical_ms) : null;
  const noticeKey =notice?.added ? (isAdmin ? "wordAdded" : "wordProposed") : isAdmin ? "saved" : "savedDraft";

  return (
    <div>
      <div className="page-head">
        <h2 className="page-title">
          🎓 <T k="navTeach" />
        </h2>
        <p className="dim">
          <T k={isAdmin ? "teachIntroAdmin" : "teachIntroTrainer"} />
        </p>
      </div>
      {location.state?.welcome && (
        <div className="note ok">
          🎉 <T k="welcomeTrainer" />
        </div>
      )}

      <div className="grid cols-2">
        <div className="card accent warm">
          <div className="toolbar">
            <button className="teal" onClick={() => setCameraOn((on) => !on)} disabled={busy}>
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
            <span className="signer-pill">
              👤 <T k="recordingAs" /> <b>{user.name}</b>
            </span>
          </div>

          <CameraFeed active={cameraOn} onFrame={onFrame}>
            {phase === "countdown" && (
              <div className="countdown">
                <div className="countdown-label">
                  <T k="getReady" />
                </div>
                <div className="countdown-num" key={countdown}>
                  {countdown}
                </div>
              </div>
            )}
            {phase === "recording" && (
              <div className="countdown recording">
                <span className="rec-dot" /> <T k="recording" />
                <div className="rec-progress">
                  <span style={{ animationDuration: `${recordMs}ms` }} />
                </div>
              </div>
            )}
          </CameraFeed>

          <div className="selected-word" style={selectedHue}>
            {selected ? (
              <>
                <Bi {...wordOf(selected)} />
                <span className="spacer" />
                <span className={`count-pill${countFor(selected) < MIN_SAMPLES ? " low" : ""}`}>{countFor(selected)}</span>
              </>
            ) : (
              <span className="dim">
                <T k="selectWordFirst" />
              </span>
            )}
          </div>

          <div className="length-picker" role="radiogroup" aria-label={t("recordingLength", lang)}>
            <span className="small dim">
              ⏱ <T k="recordingLength" />
            </span>
            {RECORD_LENGTHS_MS.map((ms) => (
              <button
                key={ms}
                role="radio"
                aria-checked={recordMs === ms}
                className={recordMs === ms ? "active" : ""}
                onClick={() => setRecordMs(ms)}
                disabled={busy}
              >
                {seconds(ms)}
              </button>
            ))}
          </div>
          {typicalLength && typicalLength !== recordMs && (
            <div className="note warn">
              ⚠️ <T k="lengthMismatch" vars={{ s: seconds(typicalLength) }} />
            </div>
          )}

          <div className="toolbar">
            <button onClick={() => record(1)} disabled={!cameraOn || !selected || busy}>
              ⏺ <T k="recordOne" />
            </button>
            <button className="warm" onClick={() => record(BURST_SIZE)} disabled={!cameraOn || !selected || busy}>
              ⏺ <T k="recordTen" />
            </button>
            <button
              className="danger"
              onClick={() => {
                stopRef.current = true;
              }}
              disabled={!busy}
            >
              ⏹ <T k="stop" />
            </button>
            {progress && (
              <span className="count-pill">
                {progress.done + 1} / {progress.total}
              </span>
            )}
          </div>

          <ErrorNote error={error} wordOf={wordOf} />
          {error?.detail?.code === "sign_already_used" && error.detail.recorded !== NONE && bySlug[error.detail.word] && (
            <button
              className="secondary small"
              onClick={() => {
                selectWord(error.detail.word);
                setError(null);
              }}
            >
              ➜ <T k="switchToWord" /> <Bi {...wordOf(error.detail.word)} />
            </button>
          )}
          {notice && (
            <div className="note ok">
              ✅ <T k={noticeKey} /> {notice.count ? <b>{notice.count} ×</b> : null} <Bi {...wordOf(notice.concept)} />
            </div>
          )}
        </div>

        <div className="card accent">
          <button
            className={`word-btn idle${selected === NONE ? " active" : ""}`}
            style={{ "--hue": 250 }}
            onClick={() => selectWord(NONE)}
          >
            ✋ <T k="idleSign" /> <span className="badge">{countFor(NONE)}</span>
          </button>
          <p className="dim small">
            <T k="idleHelp" />
          </p>

          <div className="toolbar">
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("searchWords", lang)}
              className="grow"
            />
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">{t("allCategories", lang)}</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>

          <div className="word-list">
            {filtered.map((s) => (
              <button
                key={s.sign_id}
                className={`word-btn${selected === s.concept ? " active" : ""}`}
                style={categoryStyle(s.category)}
                onClick={() => selectWord(s.concept)}
                title={s.status === "pending" ? t("awaitingApproval", lang) : s.category}
              >
                <Bi tamil={s.tamil} english={s.english} />
                {s.status === "pending" && <span aria-label={t("awaitingApproval", lang)}>⏳</span>}
                {countFor(s.concept) > 0 && <span className="badge">{countFor(s.concept)}</span>}
                {s.trained && (
                  <span className="tick" title={t("trained", lang)}>
                    ✓
                  </span>
                )}
              </button>
            ))}
          </div>

          <details>
            <summary>
              ➕ <T k={isAdmin ? "addWord" : "proposeWord"} />
            </summary>
            {!isAdmin && (
              <p className="dim small">
                <T k="proposeHint" />
              </p>
            )}
            <form className="add-word" onSubmit={addWord}>
              <label>
                <T k="english" />
                <input
                  required
                  maxLength={60}
                  value={newWord.english}
                  onChange={(e) => setNewWord({ ...newWord, english: e.target.value })}
                />
              </label>
              <label>
                <T k="tamil" />
                <input
                  required
                  maxLength={120}
                  value={newWord.tamil}
                  onChange={(e) => setNewWord({ ...newWord, tamil: e.target.value })}
                />
              </label>
              <label>
                <T k="category" />
                <input
                  list="category-options"
                  maxLength={40}
                  value={newWord.category}
                  onChange={(e) => setNewWord({ ...newWord, category: e.target.value })}
                />
                <datalist id="category-options">
                  {categories.map((c) => (
                    <option key={c} value={c} />
                  ))}
                </datalist>
              </label>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={newWord.is_emergency}
                  onChange={(e) => setNewWord({ ...newWord, is_emergency: e.target.checked })}
                />
                🚨 <T k="emergencyWord" />
              </label>
              <button type="submit" className="teal">
                <T k={isAdmin ? "add" : "propose"} />
              </button>
            </form>
          </details>
        </div>
      </div>

      <div className="card accent teal">
        <div className="toolbar">
          <h3 className="flush">
            🗂️ <T k={isAdmin ? "recordedWords" : "myRecordings"} />
          </h3>
          <span className="spacer" />
          {isAdmin ? (
            <Link to="/review">
              <button className="teal">
                ✅ <T k="goReviewTrain" /> ➜
              </button>
            </Link>
          ) : (
            <button className="teal" onClick={submitDrafts} disabled={submitting || busy || drafts === 0}>
              {submitting ? <span className="spinner" /> : "📤"} <T k="submitForReview" vars={{ n: drafts }} />
            </button>
          )}
        </div>
        <p className="dim small">
          <T k={isAdmin ? "adminRecordHint" : "reviewHint"} /> <T k="trainHint" />
        </p>
        <ErrorNote error={listError} wordOf={wordOf} />
        {submitted !== null && (
          <div className="note ok">
            📤 <T k="submittedNotice" vars={{ n: submitted }} />
          </div>
        )}

        {recorded.length === 0 ? (
          <p className="dim">
            <T k="nothingRecorded" />
          </p>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>
                    <T k="word" />
                  </th>
                  {isAdmin ? (
                    <>
                      <th>
                        <T k="status_approved" />
                      </th>
                      <th>
                        <T k="signers" />
                      </th>
                    </>
                  ) : (
                    TRAINER_COLUMNS.map((status) => (
                      <th key={status}>
                        <T k={`status_${status}`} />
                      </th>
                    ))
                  )}
                  <th />
                </tr>
              </thead>
              <tbody>
                {recorded.map(([concept, s]) => (
                  <tr key={concept}>
                    <td>
                      <button className="link" onClick={() => selectWord(concept)}>
                        <Bi {...wordOf(concept)} />
                      </button>
                    </td>
                    {isAdmin ? (
                      <>
                        <td>
                          <span className={`count-pill${s.approved_total < MIN_SAMPLES ? " low" : ""}`}>{s.approved_total}</span>
                        </td>
                        <td>{s.signers}</td>
                      </>
                    ) : (
                      TRAINER_COLUMNS.map((status) => (
                        <td key={status}>
                          <StatusCount status={status} n={s.mine[status]} />
                          {status === "rejected" && s.last_note && <div className="small review-note">💬 {s.last_note}</div>}
                        </td>
                      ))
                    )}
                    <td className="right">
                      <button className="secondary small" onClick={() => deleteLast(concept)} disabled={busy || !s.last_id}>
                        🗑 <T k="deleteLast" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
