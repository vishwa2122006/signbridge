import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { T } from "../components/Bilingual.jsx";
import { useAuth } from "../AuthContext.jsx";

const EXAMPLES = [
  { sign: "👋", tamil: "வணக்கம்", english: "Hello" },
  { sign: "🥛", tamil: "எனக்கு தண்ணீர் வேண்டும்.", english: "I want water." },
  { sign: "🤕", tamil: "எனக்கு வயிற்றில் வலி உள்ளது.", english: "I have stomach pain." },
  { sign: "🙏", tamil: "நன்றி", english: "Thank you" },
];

const STEPS = [
  { to: "/teach", icon: "🎓", title: "step1Title", body: "step1Body", hue: 38 },
  { to: "/translate", icon: "🤟", title: "step2Title", body: "step2Body", hue: 170 },
  { to: "/conversation", icon: "💬", title: "step3Title", body: "step3Body", hue: 330 },
];

const FEATURES = [
  { icon: "🔒", key: "privacyNote", hue: 265 },
  { icon: "📴", key: "offlineNote", hue: 200 },
  { icon: "➕", key: "customNote", hue: 140 },
];

export default function Home() {
  const { user } = useAuth();
  const [index, setIndex] = useState(0);
  // the public is invited to become a trainer instead of going to the (login-only) Teach page
  const steps = user
    ? STEPS
    : [{ ...STEPS[0], to: "/register", title: "becomeTrainerTitle", body: "becomeTrainerBody" }, ...STEPS.slice(1)];

  useEffect(() => {
    const id = setInterval(() => setIndex((i) => (i + 1) % EXAMPLES.length), 2800);
    return () => clearInterval(id);
  }, []);

  const example = EXAMPLES[index];

  return (
    <div>
      <section className="card hero">
        <span className="hero-badge">
          ✨ <T k="heroBadge" />
        </span>
        <h2 className="grad-text">
          <T k="homeTitle" />
        </h2>
        <p className="dim hero-body">
          <T k="homeBody" />
        </p>

        <div className="demo" aria-live="polite">
          <span className="demo-sign float" key={`sign-${index}`}>
            {example.sign}
          </span>
          <span className="demo-arrow">➜</span>
          <div className="demo-bubble" key={`text-${index}`}>
            <div className="demo-ta">{example.tamil}</div>
            <div className="demo-en">{example.english}</div>
          </div>
        </div>

        <Link to="/translate">
          <button className="large">
            📷 <T k="startTranslating" />
          </button>
        </Link>
      </section>

      <div className="grid cols-3">
        {steps.map((step, i) => (
          <Link key={step.to} to={step.to} className="card step-card" style={{ "--hue": step.hue }}>
            <span className="step-num">{i + 1}</span>
            <div className="step-icon">{step.icon}</div>
            <h3>
              <T k={step.title} />
            </h3>
            <p className="dim flush">
              <T k={step.body} />
            </p>
          </Link>
        ))}
      </div>

      <div className="feature-row">
        {FEATURES.map((feature) => (
          <div key={feature.key} className="feature" style={{ "--hue": feature.hue }}>
            <span className="feature-icon">{feature.icon}</span>
            <T k={feature.key} />
          </div>
        ))}
      </div>
    </div>
  );
}
