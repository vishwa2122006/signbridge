// Drawing recorded signs (hand and body points) on a canvas, shared by
// components/SignPlayer.jsx and components/ClipPlayer.jsx.
import { HAND_CONNECTIONS } from "./mediapipe.js";

const MAX_HAND_GAP = 4; // frames a briefly lost hand is carried forward
const PALM = [0, 1, 5, 9, 13, 17];
const FINGERTIPS = [4, 8, 12, 16, 20];
const HAND_COLORS = { right: "#2ee6c5", left: "#ff4f9a" };

function fillGaps(frames) {
  const out = frames.map((frame) => ({ ...frame }));
  for (const key of ["left", "right"]) {
    let last = null;
    let gap = 0;
    for (const frame of out) {
      if (frame[key]) {
        last = frame[key];
        gap = 0;
      } else if (last && gap < MAX_HAND_GAP) {
        frame[key] = last;
        gap += 1;
      }
    }
  }
  let pose = out.find((frame) => frame.pose)?.pose ?? null;
  for (const frame of out) {
    if (frame.pose) pose = frame.pose;
    else frame.pose = pose;
  }
  return out;
}

/** Frames plus a fixed framing box, so the figure doesn't jump around while signing. */
export function prepareClip(demo) {
  const aspect = demo.aspect || 4 / 3;
  const frames = fillGaps(demo.frames);
  const box = { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity };
  const add = (x, y) => {
    const X = Math.min(1.3, Math.max(-0.3, x)) * aspect;
    const Y = Math.min(1.15, Math.max(-0.3, y));
    box.minX = Math.min(box.minX, X);
    box.maxX = Math.max(box.maxX, X);
    box.minY = Math.min(box.minY, Y);
    box.maxY = Math.max(box.maxY, Y);
  };
  for (const frame of frames) {
    for (const key of ["left", "right"]) frame[key]?.forEach(([x, y]) => add(x, y));
    if (frame.pose) {
      frame.pose.slice(1, 5).forEach(([x, y]) => add(x, y)); // shoulders and elbows
      const [nose, ls, rs] = frame.pose;
      const shoulder = Math.hypot((ls[0] - rs[0]) * aspect, ls[1] - rs[1]);
      add(nose[0], nose[1] - shoulder * 0.45); // top of the head
    }
  }
  if (!Number.isFinite(box.minX)) Object.assign(box, { minX: 0, maxX: aspect, minY: 0, maxY: 1 });
  const t0 = frames[0]?.t ?? 0;
  return { frames, aspect, box, t0, duration: Math.max(1, (frames.at(-1)?.t ?? 0) - t0) };
}

export function frameAt(clip, elapsed) {
  const { frames, t0 } = clip;
  const target = t0 + elapsed;
  let i = 0;
  while (i < frames.length - 1 && frames[i + 1].t <= target) i++;
  const a = frames[i];
  const b = frames[Math.min(i + 1, frames.length - 1)];
  const k = b.t > a.t ? Math.min(1, Math.max(0, (target - a.t) / (b.t - a.t))) : 0;
  const mix = (p, q) => (p && q && p.length === q.length ? p.map(([x, y], j) => [x + (q[j][0] - x) * k, y + (q[j][1] - y) * k]) : p);
  return { left: mix(a.left, b.left), right: mix(a.right, b.right), pose: mix(a.pose, b.pose) };
}

export function drawFrame(canvas, clip, frame) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (!width || !height) return;
  const dpr = window.devicePixelRatio || 1;
  if (canvas.width !== Math.round(width * dpr) || canvas.height !== Math.round(height * dpr)) {
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
  }
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  const { box, aspect } = clip;
  const boxW = box.maxX - box.minX || 1;
  const boxH = box.maxY - box.minY || 1;
  const scale = Math.min((width * 0.86) / boxW, (height * 0.82) / boxH);
  const ox = (width - boxW * scale) / 2 - box.minX * scale;
  const oy = (height - boxH * scale) / 2 - box.minY * scale;
  const toCanvas = ([x, y]) => [x * aspect * scale + ox, y * scale + oy];
  const line = (a, b) => {
    ctx.beginPath();
    ctx.moveTo(a[0], a[1]);
    ctx.lineTo(b[0], b[1]);
    ctx.stroke();
  };

  const hands = {};
  for (const key of ["left", "right"]) if (frame[key]) hands[key] = frame[key].map(toCanvas);

  if (frame.pose) {
    const [nose, ls, rs, le, re, lw, rw] = frame.pose.map(toCanvas);
    const shoulder = Math.hypot(ls[0] - rs[0], ls[1] - rs[1]) || 60;
    const drop = shoulder * 1.25;

    // torso
    ctx.fillStyle = "rgba(139, 92, 246, 0.16)";
    ctx.beginPath();
    ctx.moveTo(ls[0], ls[1]);
    ctx.lineTo(rs[0], rs[1]);
    ctx.lineTo(rs[0] + (ls[0] - rs[0]) * 0.12, rs[1] + drop);
    ctx.lineTo(ls[0] - (ls[0] - rs[0]) * 0.12, ls[1] + drop);
    ctx.closePath();
    ctx.fill();

    // head and neck
    const radius = shoulder * 0.3;
    const head = [nose[0], nose[1] - radius * 0.15];
    ctx.strokeStyle = "rgba(189, 182, 222, 0.6)";
    ctx.lineWidth = Math.max(2, shoulder * 0.05);
    line([(ls[0] + rs[0]) / 2, (ls[1] + rs[1]) / 2], [head[0], head[1] + radius]);
    ctx.fillStyle = "rgba(255, 255, 255, 0.07)";
    ctx.beginPath();
    ctx.arc(head[0], head[1], radius, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();

    // arms end at whichever tracked hand is nearest the body's wrist
    const handWrists = Object.values(hands).map((pts) => pts[0]);
    const armEnd = (wrist) => {
      let best = wrist;
      let bestDistance = shoulder * 0.9;
      for (const w of handWrists) {
        const d = Math.hypot(w[0] - wrist[0], w[1] - wrist[1]);
        if (d < bestDistance) [best, bestDistance] = [w, d];
      }
      return best;
    };
    ctx.strokeStyle = "rgba(139, 92, 246, 0.85)";
    ctx.lineWidth = Math.min(16, Math.max(4, shoulder * 0.14));
    line(ls, rs);
    for (const [s, e, w] of [[ls, le, lw], [rs, re, rw]]) {
      line(s, e);
      line(e, armEnd(w));
    }
  }

  for (const [key, pts] of Object.entries(hands)) {
    const color = HAND_COLORS[key];
    const size = Math.hypot(pts[9][0] - pts[0][0], pts[9][1] - pts[0][1]);
    const lw = Math.min(7, Math.max(2, size * 0.1));

    ctx.fillStyle = `${color}33`;
    ctx.beginPath();
    PALM.forEach((i, n) => (n ? ctx.lineTo(pts[i][0], pts[i][1]) : ctx.moveTo(pts[i][0], pts[i][1])));
    ctx.closePath();
    ctx.fill();

    ctx.shadowColor = color;
    ctx.shadowBlur = 12;
    ctx.strokeStyle = color;
    ctx.lineWidth = lw;
    for (const [a, b] of HAND_CONNECTIONS) line(pts[a], pts[b]);
    ctx.shadowBlur = 0;

    ctx.fillStyle = "#ffffff";
    for (const p of pts) {
      ctx.beginPath();
      ctx.arc(p[0], p[1], lw * 0.5, 0, 2 * Math.PI);
      ctx.fill();
    }
    ctx.fillStyle = color;
    for (const i of FINGERTIPS) {
      ctx.beginPath();
      ctx.arc(pts[i][0], pts[i][1], lw * 0.95, 0, 2 * Math.PI);
      ctx.fill();
    }
  }
}
