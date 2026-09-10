import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Bi, T } from "../components/Bilingual.jsx";
import CameraFeed from "../components/CameraFeed.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { categoryStyle } from "../colors.js";
import { STRINGS, t } from "../i18n.js";

const NONE = "_none";
const RECORD_MS = 1500; // matches the live translator's window length
const COUNTDOWN_STEP_MS = 600;
const BURST_SIZE = 10;
const MIN_SAMPLES = 5;
const SIGNER_KEY = "signbridge.signer";
const EMPTY_WORD = { english: "", tamil: "", category: "CUSTOM", is_emergency: false };
const CV_METHOD_KEYS = { "signer-held-out": "cvSignerHeldOut", stratified: "cvStratified" };

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const percent = (v) => (typeof v === "number" ? `${Math.round(v * 100)}%` : "—");

function readSigner() {
  try {
    return localStorage.getItem(SIGNER_KEY) || "";
  } catch {
    return "";
  }
}

function TrainingWarnings({ report, wordOf }) {
  if (!report.warning_codes) {
    // model trained by an older version: English text only
    return (report.warnings || []).map((w) => (
      <div key={w} className="note warn">
        ⚠️ {w}
      </div>
    ));
  }
  return report.warning_codes.map((w) => (
    <div key={w.code} className="note warn">
      ⚠️ {w.code === "few_signers" && <T k="warnFewSigners" vars={{ n: w.signers }} />}
      {w.code === "no_idle" && <T k="warnNoIdle" />}
      {w.code === "no_cv" && <T k="warnNoCv" />}
      {w.code === "skipped" && (
        <>
          <T k="warnSkipped" vars={{ min: w.min_samples }} />
          <span className="chips inline">
            {w.words.map((concept) => (
              <span key={concept} className="chip low">
                <Bi {...wordOf(concept)} />
              </span>
            ))}
          </span>
        </>
      )}
    </div>
  ));
}

function TrainingReport({ report, wordOf }) {
  const tiles = [
    { hue: 170, value: percent(report.cv_accuracy), label: "cvAccuracy", sub: CV_METHOD_KEYS[report.cv_method] },
    { hue: 38, value: percent(report.accepted_rate), label: "acceptedRate", note: `≥ ${percent(report.confidence_threshold)}` },
    { hue: 330, value: percent(report.precision_at_threshold), label: "precisionAtThreshold" },
    { hue: 265, value: `${report.num_samples} / ${report.num_signers}`, label: "samplesSigners" },
  ];
  return (
    <div className="report">
      <div className="toolbar">
        <h3 className="flush">
          📊 <T k="lastTraining" />
        </h3>
        <span className="dim small">{report.trained_at?.replace("T", " ")}</span>
      </div>
      <div className="metrics">
        {tiles.map((tile) => (
          <div key={tile.label} className="metric-tile" style={{ "--hue": tile.hue }}>
            <div className="metric">{tile.value}</div>
            <div className="small">
              <T k={tile.label} />
            </div>
            {tile.sub && (
              <div className="dim small">
                <T k={tile.sub} />
              </div>
            )}
            {tile.note && <div className="dim small">{tile.note}</div>}
          </div>
        ))}
      </div>
      <TrainingWarnings report={report} wordOf={wordOf} />
      {report.per_word?.length > 0 && (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>
                  <T k="word" />
                </th>
                <th>F1</th>
                <th>
                  <T k="samples" />
                </th>
              </tr>
            </thead>
            <tbody>
              {report.per_word.map((w) => (
                <tr key={w.concept}>
                  <td>
                    <Bi {...wordOf(w.concept)} />
                  </td>
                  <td>
                    <div className="score">
                      <div className={`bar${w.f1 < 0.7 ? " low" : ""}`}>
                        <span style={{ width: `${Math.round(w.f1 * 100)}%` }} />
                      </div>
                      {percent(w.f1)}
                    </div>
                  </td>
                  <td>{w.samples}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function TeachSigns() {
  const { lang } = useLanguage();
  const [signs, setSigns] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [selected, setSelected] = useState(null);
  const [signer, setSigner] = useState(readSigner);
  const [cameraOn, setCameraOn] = useState(false);
  const [phase, setPhase] = useState("idle"); // idle | countdown | recording | saving
  const [countdown, setCountdown] = useState(0);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null); // { concept, count } after saving, { concept, added } after adding
  const [training, setTraining] = useState(false);
  const [trainError, setTrainError] = useState(null);
  const [report, setReport] = useState(null);
  const [newWord, setNewWord] = useState(EMPTY_WORD);

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
    api.health().then((h) => h.model?.trained_at && setReport(h.model)).catch(() => {});
  }, [refresh]);

  useEffect(() => {
    try {
      localStorage.setItem(SIGNER_KEY, signer);
    } catch {
      // storage unavailable - the name just won't be remembered
    }
  }, [signer]);

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
    await sleep(RECORD_MS);
    recordingRef.current = false;
    if (stopRef.current) return false;

    if (framesRef.current.length < 5) {
      setError({ key: "cameraNotReady" });
      return false;
    }
    setPhase("saving");
    try {
      await api.createSample({
        concept,
        signer_id: signer.trim(),
        frames: framesRef.current,
        aspect: aspectRef.current,
      });
      return true;
    } catch (e) {
      setError(e);
      return false;
    }
  };

  const record = async (count) => {
    if (!selected) return setError({ key: "selectWordFirst" });
    if (!signer.trim()) return setError({ key: "enterSignerName" });
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
      setTrainError(e);
    }
  };

  const train = async () => {
    setTraining(true);
    setTrainError(null);
    try {
      setReport(await api.train());
      await refresh();
    } catch (e) {
      setTrainError(e);
    } finally {
      setTraining(false);
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
  const recorded = Object.entries(stats).sort(([a], [b]) => wordOf(a).english.localeCompare(wordOf(b).english));
  const selectedHue = selected === NONE ? { "--hue": 250 } : categoryStyle(bySlug[selected]?.category);

  return (
    <div>
      <div className="page-head">
        <h2 className="page-title">
          🎓 <T k="navTeach" />
        </h2>
        <p className="dim">
          <T k="teachIntro" />
        </p>
      </div>

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
            <label className="inline-field">
              👤 <T k="signerName" />
              <input value={signer} onChange={(e) => setSigner(e.target.value)} placeholder="e.g. dharun" maxLength={40} />
            </label>
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
              </div>
            )}
          </CameraFeed>

          <div className="selected-word" style={selectedHue}>
            {selected ? (
              <>
                <Bi {...wordOf(selected)} />
                <span className="spacer" />
                <span className={`count-pill${(stats[selected]?.count || 0) < MIN_SAMPLES ? " low" : ""}`}>
                  {stats[selected]?.count || 0}
                </span>
              </>
            ) : (
              <span className="dim">
                <T k="selectWordFirst" />
              </span>
            )}
          </div>

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
          {notice && (
            <div className="note ok">
              ✅ <T k={notice.added ? "wordAdded" : "saved"} /> {notice.count ? <b>{notice.count} ×</b> : null}{" "}
              <Bi {...wordOf(notice.concept)} />
            </div>
          )}
        </div>

        <div className="card accent">
          <button
            className={`word-btn idle${selected === NONE ? " active" : ""}`}
            style={{ "--hue": 250 }}
            onClick={() => setSelected(NONE)}
          >
            ✋ <T k="idleSign" /> <span className="badge">{stats[NONE]?.count || 0}</span>
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
                onClick={() => setSelected(s.concept)}
                title={s.category}
              >
                <Bi tamil={s.tamil} english={s.english} />
                {s.samples > 0 && <span className="badge">{s.samples}</span>}
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
              ➕ <T k="addWord" />
            </summary>
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
                <T k="add" />
              </button>
            </form>
          </details>
        </div>
      </div>

      <div className="card accent teal">
        <div className="toolbar">
          <h3 className="flush">
            🗂️ <T k="recordedWords" />
          </h3>
          <span className="spacer" />
          <button className="teal" onClick={train} disabled={training || busy || recorded.length === 0}>
            {training ? (
              <>
                <span className="spinner" /> <T k="training" />
              </>
            ) : (
              <>
                🧠 <T k="train" />
              </>
            )}
          </button>
        </div>
        <p className="dim small">
          <T k="trainHint" />
        </p>
        <ErrorNote error={trainError} wordOf={wordOf} />

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
                  <th>
                    <T k="samples" />
                  </th>
                  <th>
                    <T k="signers" />
                  </th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {recorded.map(([concept, s]) => (
                  <tr key={concept}>
                    <td>
                      <button className="link" onClick={() => setSelected(concept)}>
                        <Bi {...wordOf(concept)} />
                      </button>
                    </td>
                    <td>
                      <span className={`count-pill${s.count < MIN_SAMPLES ? " low" : ""}`}>{s.count}</span>
                    </td>
                    <td className="small">{s.signers.join(", ")}</td>
                    <td className="right">
                      <button className="secondary small" onClick={() => deleteLast(concept)} disabled={busy}>
                        🗑 <T k="deleteLast" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {report && <TrainingReport report={report} wordOf={wordOf} />}
      </div>
    </div>
  );
}
