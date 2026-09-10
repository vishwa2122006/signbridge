import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Bi, T } from "../components/Bilingual.jsx";
import ClipPlayer from "../components/ClipPlayer.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import TrainingReport from "../components/TrainingReport.jsx";
import { useAuth } from "../AuthContext.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { categoryStyle } from "../colors.js";
import { STRINGS, formatDate, t } from "../i18n.js";

const NONE = "_none";
const MIN_SAMPLES = 5;
const STATUS_FILTERS = ["pending", "approved", "rejected", "all"];
const STATUS_ICONS = { draft: "✎", pending: "⏳", approved: "✓", rejected: "✕" };

const needsReview = (w) => w.status === "pending" || w.counts.pending > 0;

function TrainCard({ queue, wordOf, onTrained }) {
  const [report, setReport] = useState(null);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.health().then((h) => h.model?.trained_at && setReport(h.model)).catch(() => {});
  }, []);

  const approvedWords = queue.filter((w) => w.status === "approved");
  const tiles = [
    { key: "wordsReady", hue: 150, value: approvedWords.filter((w) => w.counts.approved >= MIN_SAMPLES).length },
    { key: "approvedRecordings", hue: 170, value: approvedWords.reduce((n, w) => n + w.counts.approved, 0) },
    { key: "waitingReview", hue: 38, value: queue.reduce((n, w) => n + w.counts.pending, 0) },
    { key: "newWordsWaiting", hue: 330, value: queue.filter((w) => w.status === "pending").length },
  ];

  const train = async () => {
    setTraining(true);
    setError(null);
    try {
      setReport(await api.train());
      onTrained();
    } catch (e) {
      setError(e);
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="card accent teal">
      <div className="toolbar">
        <h3 className="flush">
          🧠 <T k="trainModelTitle" />
        </h3>
        <span className="spacer" />
        <button className="teal" onClick={train} disabled={training}>
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
      <p className="dim small flush">
        <T k="trainApprovedHint" vars={{ min: MIN_SAMPLES }} />
      </p>
      <div className="metrics">
        {tiles.map((tile) => (
          <div key={tile.key} className="metric-tile" style={{ "--hue": tile.hue }}>
            <div className="metric">{tile.value}</div>
            <div className="small">
              <T k={tile.key} />
            </div>
          </div>
        ))}
      </div>
      <ErrorNote error={error} wordOf={wordOf} />
      {report && <TrainingReport report={report} wordOf={wordOf} />}
    </div>
  );
}

function QueueList({ queue, wordOf, selected, onSelect }) {
  const { lang } = useLanguage();
  const [filter, setFilter] = useState("todo");
  const shown = filter === "todo" ? queue.filter(needsReview) : queue;

  return (
    <div className="card accent review-queue">
      <div className="toolbar">
        <h3 className="flush">
          📋 <T k="wordsToReview" />
        </h3>
        <span className="spacer" />
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="todo">{t("needsReview", lang)}</option>
          <option value="all">{t("allWithRecordings", lang)}</option>
        </select>
      </div>
      {shown.length === 0 ? (
        <p className="dim">
          <T k={filter === "todo" ? "queueEmpty" : "noRecordingsYet"} />
        </p>
      ) : (
        <div className="queue-list">
          {shown.map((w) => (
            <button
              key={w.concept}
              className={`queue-item${selected === w.concept ? " active" : ""}`}
              style={w.concept === NONE ? { "--hue": 250 } : categoryStyle(w.category)}
              onClick={() => onSelect(w.concept)}
            >
              <Bi {...wordOf(w.concept)} />
              <span className="queue-counts">
                {w.status === "pending" && (
                  <span className="status-pill new" title={t("newWord", lang)}>
                    🆕
                  </span>
                )}
                {["pending", "approved", "rejected"].map(
                  (status) =>
                    w.counts[status] > 0 && (
                      <span key={status} className={`status-pill ${status}`} title={t(`status_${status}`, lang)}>
                        {STATUS_ICONS[status]} {w.counts[status]}
                      </span>
                    ),
                )}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function WordDecision({ word, onDone }) {
  const { lang } = useLanguage();
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const decide = async (action) => {
    setBusy(true);
    setError(null);
    try {
      await api.reviewWord(word.sign_id, action, note.trim() || null);
      onDone();
    } catch (e) {
      setError(e);
      setBusy(false);
    }
  };

  return (
    <div className={`word-decision ${word.status}`}>
      <div className="grow">
        <b>
          {word.status === "pending" ? "🆕 " : "🚫 "}
          <T k={word.status === "pending" ? "wordAwaitsApproval" : "wordWasRejected"} />
        </b>
        {word.proposed_by && (
          <div className="small dim">
            <T k="proposedBy" /> {word.proposed_by.name} · {word.proposed_by.email}
          </div>
        )}
        {word.review_note && <div className="small review-note">💬 {word.review_note}</div>}
      </div>
      <input
        className="grow"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        maxLength={500}
        placeholder={t("noteForTrainer", lang)}
      />
      <div className="toolbar">
        <button className="teal small" onClick={() => decide("approve")} disabled={busy}>
          ✓ <T k="approveWord" />
        </button>
        {word.status === "pending" && (
          <button className="danger small" onClick={() => decide("reject")} disabled={busy}>
            ✕ <T k="rejectWord" />
          </button>
        )}
      </div>
      <ErrorNote error={error} />
    </div>
  );
}

function EditWord({ word, onSaved }) {
  const [form, setForm] = useState({
    english: word.english,
    tamil: word.tamil,
    category: word.category,
    is_emergency: word.is_emergency,
  });
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaved(false);
    try {
      await api.updateSign(word.sign_id, form);
      setSaved(true);
      onSaved();
    } catch (err) {
      setError(err);
    }
  };

  return (
    <details>
      <summary>
        ✏️ <T k="editWord" />
      </summary>
      <form className="add-word" onSubmit={submit}>
        <label>
          <T k="english" />
          <input required maxLength={60} value={form.english} onChange={(e) => setForm({ ...form, english: e.target.value })} />
        </label>
        <label>
          <T k="tamil" />
          <input required maxLength={120} value={form.tamil} onChange={(e) => setForm({ ...form, tamil: e.target.value })} />
        </label>
        <label>
          <T k="category" />
          <input required maxLength={40} value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={form.is_emergency} onChange={(e) => setForm({ ...form, is_emergency: e.target.checked })} />
          🚨 <T k="emergencyWord" />
        </label>
        <button type="submit" className="teal">
          💾 <T k="save" />
        </button>
      </form>
      <ErrorNote error={error} />
      {saved && (
        <div className="note ok">
          ✅ <T k="wordUpdated" />
        </div>
      )}
    </details>
  );
}

function RecordingTile({ sample, decision, onToggle, approveBlocked }) {
  const { lang } = useLanguage();
  const handsPct = sample.num_frames ? Math.round((sample.hand_frames / sample.num_frames) * 100) : 0;
  return (
    <div className={`recording-tile${decision ? ` marked-${decision}` : ""}`}>
      <ClipPlayer sampleId={sample.id} />
      <div className="tile-meta">
        <span className={`status-pill ${sample.status}`} title={t(`status_${sample.status}`, lang)}>
          {STATUS_ICONS[sample.status]} {t(`status_${sample.status}`, lang === "both" ? "en" : lang)}
        </span>
        <span className={`small ${handsPct < 60 ? "error-text" : "dim"}`} title={t("handsVisible", lang)}>
          ✋ {handsPct}%
        </span>
      </div>
      <div className="small dim">{formatDate(sample.submitted_at || sample.created_at, lang, true)}</div>
      {sample.review_note && <div className="small review-note">💬 {sample.review_note}</div>}
      <div className="tile-actions">
        <button
          className={`decision approve${decision === "approved" ? " on" : ""}`}
          aria-pressed={decision === "approved"}
          onClick={() => onToggle("approved")}
          disabled={sample.status === "approved" || approveBlocked}
          title={t("approve", lang)}
          aria-label={t("approve", lang)}
        >
          ✓
        </button>
        <button
          className={`decision reject${decision === "rejected" ? " on" : ""}`}
          aria-pressed={decision === "rejected"}
          onClick={() => onToggle("rejected")}
          disabled={sample.status === "rejected"}
          title={t("reject", lang)}
          aria-label={t("reject", lang)}
        >
          ✕
        </button>
      </div>
    </div>
  );
}

/**
 * One word's submitted recordings, grouped by trainer. Decisions are marked on
 * each recording (or in bulk) and saved together, so every trainer gets one email.
 */
function WordReview({ concept, wordOf, onChanged }) {
  const { lang } = useLanguage();
  const [detail, setDetail] = useState(null);
  const [version, setVersion] = useState(0);
  const [filter, setFilter] = useState(null); // null until loaded: "pending" if anything waits, else "all"
  const [decisions, setDecisions] = useState({}); // sample id -> "approved" | "rejected"
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [savedCount, setSavedCount] = useState(null);

  useEffect(() => {
    let cancelled = false;
    api
      .wordRecordings(concept)
      .then((d) => {
        if (cancelled) return;
        setDetail(d);
        setFilter((f) => f ?? (d.samples.some((s) => s.status === "pending") ? "pending" : "all"));
      })
      .catch((e) => !cancelled && setError(e));
    return () => {
      cancelled = true;
    };
  }, [concept, version]);

  const reload = () => {
    setVersion((v) => v + 1);
    onChanged();
  };

  if (!detail) {
    return <div className="card review-detail">{error ? <ErrorNote error={error} /> : <div className="page-loading"><span className="spinner big" /></div>}</div>;
  }

  const { word, samples } = detail;
  const approveBlocked = word.status !== "approved";
  const counts = { all: samples.length, pending: 0, approved: 0, rejected: 0 };
  for (const s of samples) counts[s.status] += 1;
  const shown = filter === "all" ? samples : samples.filter((s) => s.status === filter);

  const groups = [];
  const groupIndex = {};
  for (const sample of shown) {
    const key = sample.trainer ? `user-${sample.trainer.id}` : "imported";
    if (!(key in groupIndex)) {
      groupIndex[key] = groups.length;
      groups.push({ key, trainer: sample.trainer, samples: [] });
    }
    groups[groupIndex[key]].samples.push(sample);
  }

  const toggle = (sample, status) =>
    setDecisions((d) => {
      const next = { ...d };
      if (next[sample.id] === status) delete next[sample.id];
      else next[sample.id] = status;
      return next;
    });
  const markAll = (list, status) =>
    setDecisions((d) => {
      const next = { ...d };
      for (const s of list) if (s.status !== status) next[s.id] = status;
      return next;
    });
  const idsMarked = (status) => Object.keys(decisions).filter((id) => decisions[id] === status).map(Number);
  const approveIds = idsMarked("approved");
  const rejectIds = idsMarked("rejected");
  const waiting = shown.filter((s) => s.status === "pending");

  const save = async () => {
    setSaving(true);
    setError(null);
    setSavedCount(null);
    try {
      const res = await api.reviewSamples(approveIds, rejectIds, note.trim() || null);
      setDecisions({});
      setNote("");
      setSavedCount(res.updated);
      reload();
    } catch (e) {
      setError(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card accent review-detail">
      <div className="selected-word" style={concept === NONE ? { "--hue": 250 } : categoryStyle(word.category)}>
        <Bi {...wordOf(concept)} />
        <span className="spacer" />
        {word.is_emergency && "🚨"}
        {concept !== NONE && (
          <span className="tag" style={categoryStyle(word.category)}>
            {word.category.replace(/_/g, " ")}
          </span>
        )}
      </div>

      {concept !== NONE && word.source !== "builtin" && word.status !== "approved" && <WordDecision word={word} onDone={reload} />}
      {concept !== NONE && <EditWord key={version} word={word} onSaved={reload} />}

      <div className="filter-chips" role="tablist">
        {STATUS_FILTERS.map((f) => (
          <button key={f} role="tab" aria-selected={filter === f} className={filter === f ? "active" : ""} onClick={() => setFilter(f)}>
            <T k={`filter_${f}`} /> <span className="badge">{counts[f]}</span>
          </button>
        ))}
      </div>

      {approveBlocked && counts.all > 0 && (
        <div className="note warn">
          ⚠️ <T k="approveWordFirst" />
        </div>
      )}
      {savedCount !== null && (
        <div className="note ok">
          ✅ <T k="reviewSaved" vars={{ n: savedCount }} />
        </div>
      )}
      {waiting.length > 0 && (
        <div className="toolbar">
          <span className="small dim">
            <T k="markAllPending" />
          </span>
          <button className="secondary small" onClick={() => markAll(waiting, "approved")} disabled={approveBlocked}>
            ✓ <T k="approveAll" />
          </button>
          <button className="secondary small" onClick={() => markAll(waiting, "rejected")}>
            ✕ <T k="rejectAll" />
          </button>
        </div>
      )}

      {shown.length === 0 ? (
        <p className="dim">
          <T k="noRecordingsHere" />
        </p>
      ) : (
        groups.map((group) => {
          const groupWaiting = group.samples.filter((s) => s.status === "pending");
          return (
            <section key={group.key} className="trainer-group">
              <div className="trainer-head">
                <span className="avatar-sm">{group.trainer ? group.trainer.name.slice(0, 1).toUpperCase() : "📦"}</span>
                <div className="grow">
                  <b>{group.trainer ? group.trainer.name : t("importedRecordings", lang)}</b>
                  {group.trainer && <div className="small dim">{group.trainer.email}</div>}
                </div>
                <span className="count-pill">{group.samples.length}</span>
                {groupWaiting.length > 0 && (
                  <>
                    <button className="secondary small" onClick={() => markAll(groupWaiting, "approved")} disabled={approveBlocked}>
                      ✓ <T k="all" />
                    </button>
                    <button className="secondary small" onClick={() => markAll(groupWaiting, "rejected")}>
                      ✕ <T k="all" />
                    </button>
                  </>
                )}
              </div>
              <div className="recording-grid">
                {group.samples.map((sample) => (
                  <RecordingTile
                    key={sample.id}
                    sample={sample}
                    decision={decisions[sample.id]}
                    onToggle={(status) => toggle(sample, status)}
                    approveBlocked={approveBlocked}
                  />
                ))}
              </div>
            </section>
          );
        })
      )}

      <ErrorNote error={error} wordOf={wordOf} />
      {(approveIds.length > 0 || rejectIds.length > 0) && (
        <div className="save-bar">
          <b>
            <T k="decisionsSummary" vars={{ a: approveIds.length, r: rejectIds.length }} />
          </b>
          {rejectIds.length > 0 && (
            <input
              className="grow"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              maxLength={500}
              placeholder={t("rejectNotePlaceholder", lang)}
            />
          )}
          <span className="spacer" />
          <button className="secondary small" onClick={() => setDecisions({})} disabled={saving}>
            <T k="clearMarks" />
          </button>
          <button className="teal" onClick={save} disabled={saving}>
            {saving ? <span className="spinner" /> : "💾"} <T k="saveReview" />
          </button>
        </div>
      )}
    </div>
  );
}

function Trainers() {
  const { lang } = useLanguage();
  const { user: me } = useAuth();
  const [users, setUsers] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(() => api.listUsers().then(setUsers).catch(setError), []);
  useEffect(() => {
    load();
  }, [load]);

  const toggleActive = async (account) => {
    if (account.is_active && !window.confirm(t("confirmDisable", lang))) return;
    setError(null);
    try {
      await api.setUserActive(account.id, !account.is_active);
      await load();
    } catch (e) {
      setError(e);
    }
  };

  if (!users) {
    return error ? <ErrorNote error={error} /> : <div className="page-loading"><span className="spinner big" /></div>;
  }

  return (
    <div className="card accent">
      <ErrorNote error={error} />
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>
                <T k="name" />
              </th>
              <th>
                <T k="details" />
              </th>
              <th>
                <T k="recordings" />
              </th>
              <th>
                <T k="joined" />
              </th>
              <th>
                <T k="status" />
              </th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className={u.is_active ? "" : "inactive-row"}>
                <td>
                  <div className="person">
                    <span className="avatar-sm">{u.name.slice(0, 1).toUpperCase()}</span>
                    <div>
                      <b>{u.name}</b> <span className={`role-tag ${u.role}`}>{t(u.role === "admin" ? "roleAdmin" : "roleTrainer", lang)}</span>
                      <div className="small dim">{u.email}</div>
                      {u.phone && <div className="small dim">📞 {u.phone}</div>}
                    </div>
                  </div>
                </td>
                <td className="small">
                  {[u.city, u.organization].filter(Boolean).join(" · ")}
                  {u.background && (
                    <div className="dim">
                      {[
                        t(`bg_${u.background}`, lang),
                        u.signing_level && t(`level_${u.signing_level}`, lang),
                        u.sign_language && t(`lang_${u.sign_language}`, lang),
                      ]
                        .filter(Boolean)
                        .join(" · ")}
                    </div>
                  )}
                  {u.about && <div className="dim">“{u.about}”</div>}
                </td>
                <td>
                  <div className="queue-counts">
                    {["pending", "approved", "rejected", "draft"].map(
                      (status) =>
                        u.recordings[status] > 0 && (
                          <span key={status} className={`status-pill ${status}`} title={t(`status_${status}`, lang)}>
                            {STATUS_ICONS[status]} {u.recordings[status]}
                          </span>
                        ),
                    )}
                  </div>
                </td>
                <td className="small nowrap">{formatDate(u.created_at, lang)}</td>
                <td className="nowrap">
                  {u.email_verified ? (
                    <span className={`status-pill ${u.is_active ? "approved" : "rejected"}`}>{t(u.is_active ? "active" : "disabled", lang)}</span>
                  ) : (
                    <span className="status-pill pending">{t("notVerified", lang)}</span>
                  )}
                  {u.id !== me.id && (
                    <button className="secondary small row-action" onClick={() => toggleActive(u)}>
                      {t(u.is_active ? "disable" : "enable", lang)}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** Admins: review trainers' recordings and proposed words, train the model, and see who the trainers are. */
export default function Review() {
  const [params, setParams] = useSearchParams();
  const tab = params.get("tab") === "trainers" ? "trainers" : "recordings";
  const [queue, setQueue] = useState([]);
  const [queueError, setQueueError] = useState(null);
  const [selected, setSelected] = useState(null);

  const loadQueue = useCallback(
    () =>
      api
        .reviewQueue()
        .then((q) => {
          setQueue(q);
          setSelected((current) => current ?? q.find(needsReview)?.concept ?? null);
        })
        .catch(setQueueError),
    [],
  );

  useEffect(() => {
    loadQueue();
  }, [loadQueue]);

  const byConcept = useMemo(() => Object.fromEntries(queue.map((w) => [w.concept, w])), [queue]);
  const wordOf = useCallback(
    (concept) => {
      if (concept === NONE) return { tamil: STRINGS.idleSign.ta, english: STRINGS.idleSign.en };
      const w = byConcept[concept];
      return w ? { tamil: w.tamil, english: w.english } : { tamil: concept, english: concept };
    },
    [byConcept],
  );

  return (
    <div>
      <div className="page-head">
        <h2 className="page-title">
          ✅ <T k="navReview" />
        </h2>
        <p className="dim">
          <T k="reviewIntro" />
        </p>
      </div>

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "recordings"} className={tab === "recordings" ? "active" : ""} onClick={() => setParams({})}>
          🎬 <T k="tabRecordings" />
        </button>
        <button
          role="tab"
          aria-selected={tab === "trainers"}
          className={tab === "trainers" ? "active" : ""}
          onClick={() => setParams({ tab: "trainers" })}
        >
          👥 <T k="tabTrainers" />
        </button>
      </div>

      {tab === "trainers" ? (
        <Trainers />
      ) : (
        <>
          <TrainCard queue={queue} wordOf={wordOf} onTrained={loadQueue} />
          <ErrorNote error={queueError} />
          <div className="review-grid">
            <QueueList queue={queue} wordOf={wordOf} selected={selected} onSelect={setSelected} />
            {selected ? (
              <WordReview key={selected} concept={selected} wordOf={wordOf} onChanged={loadQueue} />
            ) : (
              <div className="card review-empty">
                <div className="big">📋</div>
                <T k="pickWordToReview" />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
