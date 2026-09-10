import React, { useEffect, useRef, useState } from "react";
import { T } from "./Bilingual.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { t } from "../i18n.js";
import { HAND_CONNECTIONS, POSE_CONNECTIONS, detectFrame, getLandmarkers, resetTracking } from "../mediapipe.js";

// Live window before the model's length is known; the translator then uses the
// model's longest word (max_window_ms), since words can be recorded 1.5 to 6 s long.
export const DEFAULT_WINDOW_MS = 1500;
const EMIT_INTERVAL_MS = 250;

function drawOverlay(canvas, video, handLandmarks, posePoints) {
  if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
  }
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.lineCap = "round";
  const line = (p1, p2) => {
    ctx.beginPath();
    ctx.moveTo(p1.x * canvas.width, p1.y * canvas.height);
    ctx.lineTo(p2.x * canvas.width, p2.y * canvas.height);
    ctx.stroke();
  };

  if (posePoints) {
    ctx.strokeStyle = "rgba(139, 92, 246, 0.7)";
    ctx.lineWidth = 6;
    for (const [a, b] of POSE_CONNECTIONS) line(posePoints[a], posePoints[b]);
  }

  ctx.strokeStyle = "#2ee6c5";
  ctx.fillStyle = "#ff4f9a";
  ctx.lineWidth = 3;
  for (const landmarks of handLandmarks) {
    for (const [a, b] of HAND_CONNECTIONS) line(landmarks[a], landmarks[b]);
    for (const lm of landmarks) {
      ctx.beginPath();
      ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 4, 0, 2 * Math.PI);
      ctx.fill();
    }
  }
}

/**
 * Webcam + on-device hand/body tracking. Video never leaves the browser: only
 * landmark coordinates are passed to the callbacks.
 *   onFrame(frame, aspect)    every processed frame
 *   onWindow(frames, aspect)  every 250 ms with the last `windowMs` of frames
 * The picture is mirrored on screen like a selfie view; the landmark data is not.
 */
export default function CameraFeed({ active, onFrame, onWindow, windowMs = DEFAULT_WINDOW_MS, children }) {
  const { lang } = useLanguage();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const callbacksRef = useRef({ onFrame, onWindow, windowMs });
  const [state, setState] = useState("loading"); // loading | running | error
  const [error, setError] = useState(null);

  useEffect(() => {
    callbacksRef.current = { onFrame, onWindow, windowMs };
  }, [onFrame, onWindow, windowMs]);

  useEffect(() => {
    if (!active) return undefined;
    const canvas = canvasRef.current;
    let cancelled = false;
    let stream = null;
    let raf = 0;
    let lastEmit = -Infinity;
    let lastVideoTime = -1;
    const buffer = [];

    const loop = (landmarkers) => {
      if (cancelled) return;
      const video = videoRef.current;
      if (video && video.readyState >= 2 && video.currentTime !== lastVideoTime) {
        lastVideoTime = video.currentTime;
        const aspect = video.videoWidth / video.videoHeight || 4 / 3;
        const { frame, handLandmarks, posePoints } = detectFrame(landmarkers, video, performance.now());
        if (canvas) drawOverlay(canvas, video, handLandmarks, posePoints);

        callbacksRef.current.onFrame?.(frame, aspect);
        buffer.push(frame);
        const { windowMs: keepMs } = callbacksRef.current;
        while (frame.t - buffer[0].t > keepMs) buffer.shift();
        // start predicting once the shortest words fit; longer ones are scored when enough is seen
        const readyMs = Math.min(keepMs, DEFAULT_WINDOW_MS) * 0.8;
        if (frame.t - lastEmit >= EMIT_INTERVAL_MS && frame.t - buffer[0].t >= readyMs) {
          lastEmit = frame.t;
          callbacksRef.current.onWindow?.(buffer.slice(), aspect);
        }
      }
      raf = requestAnimationFrame(() => loop(landmarkers));
    };

    (async () => {
      setState("loading");
      setError(null);
      try {
        const landmarkers = await getLandmarkers();
        if (cancelled) return;
        const media = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: "user" },
          audio: false,
        });
        if (cancelled) {
          media.getTracks().forEach((track) => track.stop());
          return;
        }
        stream = media;
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        if (cancelled) return;
        resetTracking();
        setState("running");
        loop(landmarkers);
      } catch (e) {
        if (!cancelled) {
          setError(e?.message || String(e));
          setState("error");
        }
      }
    })();

    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      stream?.getTracks().forEach((track) => track.stop());
      canvas?.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
    };
  }, [active]);

  const status = active ? state : "off";
  return (
    <div className={`camera-wrap mirrored ${status}`}>
      <video ref={videoRef} playsInline muted className={status === "running" ? "" : "invisible"} />
      <canvas ref={canvasRef} className="overlay" />
      {status === "running" && <span className="live-badge">{t("live", lang)}</span>}
      {status !== "running" && (
        <div className="camera-placeholder">
          {status === "off" && (
            <>
              <div className="placeholder-icon">📷</div>
              <T k="cameraOff" />
            </>
          )}
          {status === "loading" && (
            <>
              <div className="spinner big" />
              <T k="cameraLoading" />
            </>
          )}
          {status === "error" && (
            <span className="error-text">
              ⚠️ <T k="cameraError" />: {error}
            </span>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
