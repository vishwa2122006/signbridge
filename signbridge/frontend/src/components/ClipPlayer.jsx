import React, { useEffect, useRef, useState } from "react";
import { drawFrame, frameAt, prepareClip } from "../signClip.js";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { t } from "../i18n.js";

const LOOP_PAUSE_MS = 400;

// One request per recording per session.
const clipCache = new Map();
function loadClip(sampleId) {
  if (!clipCache.has(sampleId)) {
    clipCache.set(
      sampleId,
      api
        .getSample(sampleId)
        .then(prepareClip)
        .catch((error) => {
          clipCache.delete(sampleId);
          throw error;
        }),
    );
  }
  return clipCache.get(sampleId);
}

/** Replays one recording (hand and body points) on a loop. It's loaded on the first press of play. */
export default function ClipPlayer({ sampleId }) {
  const { lang } = useLanguage();
  const canvasRef = useRef(null);
  const [clip, setClip] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);

  const toggle = async () => {
    if (playing) return setPlaying(false);
    if (!clip) {
      setLoading(true);
      setFailed(false);
      try {
        setClip(await loadClip(sampleId));
      } catch {
        setFailed(true);
        return;
      } finally {
        setLoading(false);
      }
    }
    setPlaying(true);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !clip) return undefined;
    if (!playing) {
      drawFrame(canvas, clip, frameAt(clip, 0));
      return undefined;
    }
    let raf = 0;
    const start = performance.now();
    const tick = (now) => {
      const elapsed = (now - start) % (clip.duration + LOOP_PAUSE_MS);
      drawFrame(canvas, clip, frameAt(clip, Math.min(elapsed, clip.duration)));
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [clip, playing]);

  const label = t(playing ? "pause" : "play", lang);
  return (
    <div className="clip-player">
      <canvas ref={canvasRef} className="clip-canvas" role="img" aria-label={t("recordingPreview", lang)} />
      {!clip && !loading && (
        <span className="clip-placeholder" aria-hidden="true">
          🤟
        </span>
      )}
      {loading && (
        <span className="clip-overlay">
          <span className="spinner" />
        </span>
      )}
      <button type="button" className="secondary icon-btn clip-play" onClick={toggle} title={label} aria-label={label}>
        {failed ? "⚠️" : playing ? "⏸" : "▶"}
      </button>
    </div>
  );
}
