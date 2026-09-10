// On-device landmark extraction shared by every camera view. Produces the raw
// frame format documented in backend/app/ml/features.py; ml/import_videos.py
// produces the same format from video files, so keep all three in sync.
import { FilesetResolver, HandLandmarker, PoseLandmarker } from "@mediapipe/tasks-vision";

// Must match the installed @mediapipe/tasks-vision version (pinned exactly in package.json).
const TASKS_VISION_VERSION = "1.0.1";
const WASM_PATH = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${TASKS_VISION_VERSION}/wasm`;
const HAND_MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";
const POSE_MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task";

// Pose points kept per frame: nose, left/right shoulder, left/right elbow, left/right wrist.
export const POSE_INDICES = [0, 11, 12, 13, 14, 15, 16];
// Connections between the kept pose points (indices into POSE_INDICES).
export const POSE_CONNECTIONS = [[1, 2], [1, 3], [3, 5], [2, 4], [4, 6]];

// Standard 21-point MediaPipe hand topology.
export const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],          // thumb
  [0, 5], [5, 6], [6, 7], [7, 8],          // index
  [5, 9], [9, 10], [10, 11], [11, 12],     // middle
  [9, 13], [13, 14], [14, 15], [15, 16],   // ring
  [13, 17], [17, 18], [18, 19], [19, 20],  // pinky
  [0, 17],
];

let landmarkersPromise = null;
let lastTimestamp = -1;
let frameCount = 0;
let lastPose = null;

async function createTask(Task, vision, options) {
  const withDelegate = (delegate) => ({ ...options, baseOptions: { ...options.baseOptions, delegate } });
  try {
    return await Task.createFromOptions(vision, withDelegate("GPU"));
  } catch {
    return Task.createFromOptions(vision, withDelegate("CPU"));
  }
}

/** Loads the hand + pose landmarkers once and reuses them across pages. */
export function getLandmarkers() {
  if (!landmarkersPromise) {
    landmarkersPromise = (async () => {
      const vision = await FilesetResolver.forVisionTasks(WASM_PATH);
      const [hands, pose] = await Promise.all([
        createTask(HandLandmarker, vision, {
          baseOptions: { modelAssetPath: HAND_MODEL_URL },
          runningMode: "VIDEO",
          numHands: 2,
        }),
        createTask(PoseLandmarker, vision, {
          baseOptions: { modelAssetPath: POSE_MODEL_URL },
          runningMode: "VIDEO",
          numPoses: 1,
        }),
      ]);
      return { hands, pose };
    })();
    landmarkersPromise.catch(() => {
      landmarkersPromise = null; // allow a retry after e.g. a network failure
    });
  }
  return landmarkersPromise;
}

export function resetTracking() {
  frameCount = 0;
  lastPose = null;
}

const round4 = (v) => Math.round(v * 10000) / 10000;
const toPoints = (landmarks) => landmarks.map((p) => [round4(p.x), round4(p.y), round4(p.z)]);

/** Puts each detected hand in the "left" or "right" slot using MediaPipe's
 * handedness label. If both hands get the same label, position decides: in the
 * unmirrored camera image MediaPipe labels the hand on the image's right side
 * "Right". ml/import_videos.py applies the identical rule. */
export function assignHands(landmarks, handedness) {
  const hands = landmarks.slice(0, 2).map((lms, i) => ({
    lms,
    label: handedness?.[i]?.[0]?.categoryName === "Left" ? "Left" : "Right",
  }));
  if (hands.length === 2 && hands[0].label === hands[1].label) {
    const rightIdx = hands[0].lms[0].x >= hands[1].lms[0].x ? 0 : 1;
    hands[rightIdx].label = "Right";
    hands[1 - rightIdx].label = "Left";
  }
  const slots = { left: null, right: null };
  for (const hand of hands) slots[hand.label === "Left" ? "left" : "right"] = toPoints(hand.lms);
  return slots;
}

/** Runs both landmarkers on the current video frame. */
export function detectFrame({ hands, pose }, video, timestampMs) {
  // VIDEO mode requires strictly increasing timestamps.
  const ts = Math.max(Math.round(timestampMs), lastTimestamp + 1);
  lastTimestamp = ts;

  const handResult = hands.detectForVideo(video, ts);
  // The body moves far less than the fingers: pose on every other frame halves the cost.
  if (frameCount++ % 2 === 0 || !lastPose) {
    const poseLandmarks = pose.detectForVideo(video, ts).landmarks?.[0];
    lastPose = poseLandmarks ? POSE_INDICES.map((i) => poseLandmarks[i]) : null;
  }

  const handLandmarks = handResult.landmarks || [];
  const slots = assignHands(handLandmarks, handResult.handedness);
  return {
    frame: { t: ts, left: slots.left, right: slots.right, pose: lastPose ? toPoints(lastPose) : null },
    handLandmarks,
    posePoints: lastPose,
  };
}
