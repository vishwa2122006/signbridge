import React from "react";

// Floating outline hands: horizontal position, size (px), seconds per trip, start offset, tilt.
const HANDS = [
  { left: "5%", size: 72, duration: 26, delay: 0, tilt: -12, hue: 170 },
  { left: "17%", size: 46, duration: 33, delay: -14, tilt: 10, hue: 265 },
  { left: "31%", size: 58, duration: 29, delay: -7, tilt: -4, hue: 330 },
  { left: "48%", size: 40, duration: 36, delay: -22, tilt: 16, hue: 38 },
  { left: "63%", size: 66, duration: 27, delay: -3, tilt: -18, hue: 200 },
  { left: "78%", size: 50, duration: 31, delay: -17, tilt: 8, hue: 300 },
  { left: "91%", size: 42, duration: 38, delay: -27, tilt: -8, hue: 150 },
];

/** Decorative, motion-only layer behind every page: drifting color glows, a slowly
 * moving dot grid and line-art hands (the app icon's hand) floating upward.
 * Everything here is aria-hidden and stops when the OS asks for reduced motion. */
export default function AnimatedBackground() {
  return (
    <div className="bg-scene" aria-hidden="true">
      <svg className="bg-defs" width="0" height="0">
        <defs>
          <g id="sb-hand-shapes">
            <rect x="11.755" y="31.5" width="59.49" height="13" rx="6.5" transform="rotate(-108.83 41.5 38)" />
            <rect x="35.27" y="33.5" width="56.46" height="13" rx="6.5" transform="rotate(-66.97 63.5 40)" />
            <rect x="48.9" y="59.5" width="40.2" height="13" rx="6.5" transform="rotate(-36.03 69 66)" />
            <path d="M28 48 H60 A6 6 0 0 1 66 54 V72 A16 16 0 0 1 50 88 H42 A18 18 0 0 1 24 70 V52 A4 4 0 0 1 28 48 Z" />
            <rect x="20" y="46" width="13" height="22" rx="6.5" />
            <rect x="31" y="44" width="13" height="24" rx="6.5" />
          </g>
          {/* white = visible: a thick outline of the whole hand minus its inside */}
          <mask id="sb-hand-outline" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">
            <g transform="translate(50 51) scale(0.84) translate(-53.25 -48.75)">
              <use href="#sb-hand-shapes" fill="#fff" stroke="#fff" strokeWidth="9" strokeLinejoin="round" />
              <use href="#sb-hand-shapes" fill="#000" />
              <rect x="20" y="46" width="13" height="22" rx="6.5" fill="#000" stroke="#fff" strokeWidth="4.5" />
              <rect x="31" y="44" width="13" height="24" rx="6.5" fill="#000" stroke="#fff" strokeWidth="4.5" />
            </g>
          </mask>
        </defs>
      </svg>

      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />
      <div className="blob blob-4" />
      <div className="bg-dots" />

      {HANDS.map((hand) => (
        <svg
          key={hand.left}
          className="floating-hand"
          viewBox="0 0 100 100"
          style={{
            left: hand.left,
            width: hand.size,
            height: hand.size,
            color: `hsl(${hand.hue} 95% 72%)`,
            "--tilt": `${hand.tilt}deg`,
            animationDuration: `${hand.duration}s`,
            animationDelay: `${hand.delay}s`,
          }}
        >
          <rect width="100" height="100" fill="currentColor" mask="url(#sb-hand-outline)" />
        </svg>
      ))}
    </div>
  );
}
