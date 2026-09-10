import React, { useEffect, useState } from "react";
import { Bi, T } from "./Bilingual.jsx";
import BilingualOutput from "./BilingualOutput.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { t } from "../i18n.js";
import { speakBilingual } from "../speech.js";

const CHIP_HUES = [170, 265, 330, 38, 200, 140];

/** Recognized words as chips plus the sentence the backend's rule templates
 * form from them, kept up to date as words are added or removed. With
 * `onSend`, a Send button sits at the bottom (disabled until there is a sentence).
 * The sentence is spoken in `speakLang` ("ta" | "en", e.g. the listener's language),
 * or following the display language when it isn't given. */
export default function SentenceBuilder({ words, onUndo, onClear, onSend, speakLang, className = "" }) {
  const { lang } = useLanguage();
  const [sentence, setSentence] = useState(null);
  const [noTamilVoice, setNoTamilVoice] = useState(false);
  const key = words.map((w) => w.concept).join(" ");

  useEffect(() => {
    if (!key) return undefined;
    let stale = false;
    api
      .translate(key.split(" "))
      .then((s) => !stale && setSentence(s))
      .catch(() => !stale && setSentence(null));
    return () => {
      stale = true;
    };
  }, [key]);

  const current = key ? sentence : null;

  const speak = async () => {
    const { missing } = await speakBilingual(current, speakLang || lang);
    setNoTamilVoice(missing.includes("ta"));
  };
  const speakTitle = speakLang ? `${t("speak", lang)} · ${speakLang === "ta" ? "தமிழ்" : "English"}` : t("speak", lang);

  return (
    <div className={`card accent sentence-card ${className}`}>
      <div className="toolbar">
        <h3 className="flush">
          ✍️ <T k="signedWords" />
        </h3>
        {words.length > 0 && <span className="count-badge">{words.length}</span>}
        <span className="spacer" />
        <button
          className="secondary icon-btn"
          onClick={onUndo}
          disabled={!words.length}
          title={t("undo", lang)}
          aria-label={t("undo", lang)}
        >
          ↩
        </button>
        <button
          className="secondary icon-btn"
          onClick={onClear}
          disabled={!words.length}
          title={t("clear", lang)}
          aria-label={t("clear", lang)}
        >
          ✕
        </button>
      </div>

      <div className="sentence-body">
        {words.length === 0 ? (
          <p className="dim">
            <T k="noWordsYet" />
          </p>
        ) : (
          <div className="chips">
            {words.map((w, i) => (
              <span
                key={`${i}-${w.concept}`}
                className={`chip${w.is_emergency ? " emergency" : ""}`}
                style={w.is_emergency ? undefined : { "--hue": CHIP_HUES[i % CHIP_HUES.length] }}
              >
                <Bi tamil={w.tamil} english={w.english} />
              </span>
            ))}
          </div>
        )}

        {current && (
          <div className="sentence-box">
            <BilingualOutput
              tamil={current.tamil}
              english={current.english}
              onSpeak={onSend ? undefined : speak}
            />
          </div>
        )}
        {noTamilVoice && (
          <div className="note warn small">
            🔇 <T k="noTamilVoice" />
          </div>
        )}
      </div>

      {onSend && (
        <div className="sentence-actions">
          <button
            className="secondary icon-btn"
            onClick={speak}
            disabled={!current}
            title={speakTitle}
            aria-label={speakTitle}
          >
            🔊
          </button>
          <button className="teal send-btn" onClick={() => onSend(current)} disabled={!current}>
            ➤ <T k="send" />
          </button>
        </div>
      )}
    </div>
  );
}
