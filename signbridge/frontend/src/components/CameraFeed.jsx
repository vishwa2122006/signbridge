import React, { useEffect, useRef, useState, useCallback } from "react";
import { HAND_CONNECTIONS, landmarksToFeatureVector } from "../handLandmarks.js";

const WASM_PATH =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";

const SEQ_LEN = 30;
const PREDICT_INTERVAL_MS = 250; // how often we send the current window to the backend

/**
 * Privacy-by-design: video frames never leave the browser. MediaPipe runs
 * entirely client-side (WASM), and only the extracted numeric landmark
 * coordinates are sent to the backend for classification. No video is
 * uploaded or stored unless the user is explicitly in Dataset Collection
 * Mode (a separate, clearly-labeled page) and has given consent.
 */
export default function CameraFeed({ active, onWindowReady, onHandState }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const landmarkerRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(null);
  const bufferRef = useRef([]);
  const lastPredictSentRef = useRef(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const drawOverlay = useCallback((handsLandmarks, videoWidth, videoHeight) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    canvas.width = videoWidth;
    canvas.height = videoHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#4fd1c5";
    ctx.fillStyle = "#63b3ed";

    for (const landmarks of handsLandmarks || []) {
      for (const [a, b] of HAND_CONNECTIONS) {
        const p1 = landmarks[a], p2 = landmarks[b];
        ctx.beginPath();
        ctx.moveTo(p1.x * canvas.width, p1.y * canvas.height);
        ctx.lineTo(p2.x * canvas.width, p2.y * canvas.height);
        ctx.stroke();
      }
      for (const lm of landmarks) {
        ctx.beginPath();
        ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 4, 0, 2 * Math.PI);
        ctx.fill();
      }
    }
  }, []);

  useEffect(() => {
    if (!active) return;
    let cancelled = false;

    async function setup() {
      setLoading(true);
      setError(null);
      try {
        const { HandLandmarker, FilesetResolver } = await import("@mediapipe/tasks-vision");
        const vision = await FilesetResolver.forVisionTasks(WASM_PATH);
        const landmarker = await HandLandmarker.createFromOptions(vision, {
          baseOptions: { modelAssetPath: MODEL_URL, delegate: "GPU" },
          runningMode: "VIDEO",
          numHands: 2,
        });
        if (cancelled) return;
        landmarkerRef.current = landmarker;

        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
        if (cancelled) return;
        streamRef.current = stream;
        const video = videoRef.current;
        video.srcObject = stream;
        await video.play();

        setLoading(false);
        loop();
      } catch (e) {
        if (!cancelled) {
          setError(e.message || String(e));
          setLoading(false);
        }
      }
    }

    function loop() {
      const video = videoRef.current;
      const landmarker = landmarkerRef.current;
      if (!video || !landmarker || video.readyState < 2) {
        rafRef.current = requestAnimationFrame(loop);
        return;
      }
      const result = landmarker.detectForVideo(video, performance.now());
      const handsLandmarks = result.landmarks || [];
      const handDetected = handsLandmarks.length > 0;

      drawOverlay(handsLandmarks, video.videoWidth, video.videoHeight);
      onHandState?.(handDetected, handsLandmarks.length);

      const features = landmarksToFeatureVector(handsLandmarks);
      bufferRef.current.push({ hand_detected: handDetected, num_hands: handsLandmarks.length, features });
      if (bufferRef.current.length > SEQ_LEN) bufferRef.current.shift();

      const now = performance.now();
      if (bufferRef.current.length === SEQ_LEN && now - lastPredictSentRef.current > PREDICT_INTERVAL_MS) {
        lastPredictSentRef.current = now;
        onWindowReady?.([...bufferRef.current]);
      }

      rafRef.current = requestAnimationFrame(loop);
    }

    setup();

    return () => {
      cancelled = true;
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop());
      if (landmarkerRef.current) landmarkerRef.current.close?.();
      bufferRef.current = [];
    };
  }, [active, drawOverlay, onWindowReady, onHandState]);

  return (
    <div className="camera-wrap">
      <video ref={videoRef} playsInline muted style={{ width: "100%", display: active ? "block" : "none" }} />
      <canvas ref={canvasRef} className="overlay" />
      {loading && <p>Loading camera + hand-tracking model...</p>}
      {error && <p style={{ color: "var(--danger)" }}>Camera error: {error}</p>}
      {!active && <p>Camera is off.</p>}
    </div>
  );
}
