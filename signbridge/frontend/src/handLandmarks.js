// Standard 21-point MediaPipe Hand landmark topology (same indexing used by
// the Python `mediapipe.solutions.hands` used in ml/extract_landmarks.py,
// so the feature vector layout matches exactly between training and
// live browser inference).
export const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],          // thumb
  [0, 5], [5, 6], [6, 7], [7, 8],          // index
  [5, 9], [9, 10], [10, 11], [11, 12],     // middle
  [9, 13], [13, 14], [14, 15], [15, 16],   // ring
  [13, 17], [17, 18], [18, 19], [19, 20],  // pinky
  [0, 17],
];

export const NUM_LANDMARKS = 21;
export const COORDS = 3;
export const MAX_HANDS = 2;
export const NUM_FEATURES = NUM_LANDMARKS * COORDS * MAX_HANDS; // 126

/** Converts a HandLandmarker result (result.landmarks: Array<Array<{x,y,z}>>)
 * into the same flat 126-length feature vector the Python training pipeline
 * produces: hand_idx * 63 + landmark_idx * 3 + coord, zero-filled for any
 * missing hand. Order of hands as MediaPipe returns them is used directly -
 * this matches how extract_landmarks.py enumerates results.multi_hand_landmarks. */
export function landmarksToFeatureVector(handsLandmarks) {
  const features = new Array(NUM_FEATURES).fill(0);
  const hands = (handsLandmarks || []).slice(0, MAX_HANDS);
  hands.forEach((landmarks, handIdx) => {
    const base = handIdx * NUM_LANDMARKS * COORDS;
    landmarks.forEach((lm, i) => {
      const offset = base + i * COORDS;
      features[offset] = lm.x;
      features[offset + 1] = lm.y;
      features[offset + 2] = lm.z;
    });
  });
  return features;
}
