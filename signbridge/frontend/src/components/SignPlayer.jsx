import React, { useEffect, useMemo, useRef, useState } from "react";
import { Bi, T } from "./Bilingual.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { t } from "../i18n.js";
import { drawFrame, frameAt, prepareClip } from "../signClip.js";

const HOLD_MS = 450; // pause on the last frame of each word before the next one

// One request per word per session.
const demoCache = new Map();
function loadDemo(concept) {
  if (!demoCache.has(concept)) {
    demoCache.set(
      concept,
      api.signDemo(concept).catch((error) => {
        demoCache.delete(concept);
        throw error;
      }),
    );
  }
  return demoCache.get(concept);
}

/**
 * Shows a hearing person's message to the signer as hand signs: each word that
 * has recordings is replayed from its most typical recording (hand and body
 * points, never video), one after another with a caption. Words without a
 * recording are listed as faded chips.
 */
export default function SignPlayer({ items }) {
  const { lang } = useLanguage();
  const canvasRef = useRef(null);
  const progressRef = useRef(null);
  const [demos, setDemos] = useState(null); // concept -> demo (null if it failed); null while loading
  const [active, setActive] = useState(-1);
  const [run, setRun] = useState(0);
  const [slow, setSlow] = useState(false);

  const concepts = useMemo(
    () => [...new Set(items.filter((item) => item.has_sign).map((item) => item.concept))],
    [items],
  );

  useEffect(() => {
    let cancelled = false;
    Promise.all(concepts.map((c) => loadDemo(c).then((demo) => [c, demo], () => [c, null]))).then((pairs) => {
      if (!cancelled) setDemos(Object.fromEntries(pairs));
    });
    return () => {
      cancelled = true;
    };
  }, [concepts]);

  const clips = useMemo(() => {
    if (!demos) return [];
    return items
      .map((item, index) => (item.has_sign && demos[item.concept] ? { index, ...prepareClip(demos[item.concept]) } : null))
      .filter(Boolean);
  }, [items, demos]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !clips.length) return undefined;
    const speed = slow ? 0.5 : 1;
    let raf = 0;
    let clipIndex = 0;
    let start = performance.now();
    let shown = null;

    const tick = (now) => {
      let clip = clips[clipIndex];
      let elapsed = (now - start) * speed;
      if (elapsed > clip.duration + HOLD_MS) {
        if (clipIndex === clips.length - 1) {
          drawFrame(canvas, clip, frameAt(clip, clip.duration));
          if (progressRef.current) progressRef.current.style.width = "100%";
          setActive(-1);
          return;
        }
        clipIndex += 1;
        start = now;
        clip = clips[clipIndex];
        elapsed = 0;
      }
      if (shown !== clip.index) {
        shown = clip.index;
        setActive(clip.index);
      }
      drawFrame(canvas, clip, frameAt(clip, Math.min(elapsed, clip.duration)));
      if (progressRef.current) {
        const within = Math.min(1, elapsed / (clip.duration + HOLD_MS));
        progressRef.current.style.width = `${((clipIndex + within) / clips.length) * 100}%`;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [clips, run, slow]);

  const loading = demos === null && concepts.length > 0;
  const activeItem = active >= 0 ? items[active] : null;

  return (
    <div className="sign-player">
      {(loading || clips.length > 0) && (
        <div className="sign-stage">
          <canvas ref={canvasRef} className="sign-canvas" role="img" aria-label={t("inSigns", lang)} />
          <span className="sign-badge" title={t("signsFromRecordings", lang)}>
            🤟 {t("inSigns", lang)}
          </span>
          {clips.length > 0 && (
            <div className="sign-tools">
              <button
                className="secondary icon-btn"
                onClick={() => setRun((r) => r + 1)}
                title={t("replay", lang)}
                aria-label={t("replay", lang)}
              >
                ↻
              </button>
              <button
                className={`secondary icon-btn${slow ? " toggled" : ""}`}
                aria-pressed={slow}
                onClick={() => setSlow((s) => !s)}
                title={t("slow", lang)}
                aria-label={t("slow", lang)}
              >
                🐢
              </button>
            </div>
          )}
          {loading && (
            <div className="sign-stage-overlay">
              <span className="spinner big" />
            </div>
          )}
          {activeItem && (
            <div className="sign-caption-wrap">
              <div className="sign-caption" key={active}>
                <Bi tamil={activeItem.tamil} english={activeItem.english} />
              </div>
            </div>
          )}
          <div className="sign-progress">
            <span ref={progressRef} />
          </div>
        </div>
      )}

      {demos && clips.length === 0 && (
        <div className="bubble-note">
          🤟 <T k="noSignsRecorded" />
        </div>
      )}

      <div className="chips sign-words">
        {items.map((item, i) =>
          item.concept ? (
            <span
              key={i}
              className={`chip small${i === active ? " active" : ""}${item.has_sign ? "" : " unsigned"}`}
              title={item.has_sign ? undefined : t("notSigned", lang)}
            >
              <Bi tamil={item.tamil} english={item.english} />
            </span>
          ) : (
            <span key={i} className="chip small unsigned" title={t("notSigned", lang)}>
              {item.text}
            </span>
          ),
        )}
      </div>
    </div>
  );
}
