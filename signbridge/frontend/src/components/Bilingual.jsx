import React from "react";
import { useLanguage } from "../LanguageContext.jsx";
import { STRINGS, format } from "../i18n.js";

/** Tamil and/or English following the language toggle; "both" stacks Tamil over English. */
export function Bi({ tamil, english, className = "" }) {
  const { lang } = useLanguage();
  if (lang === "en") return english ?? tamil ?? null;
  if (lang === "ta") return tamil ?? english ?? null;
  return (
    <span className={`bi ${className}`}>
      <span className="bi-ta">{tamil}</span>
      <span className="bi-en">{english}</span>
    </span>
  );
}

/** A UI string from i18n.js by key, with optional {placeholder} values. */
export function T({ k, vars, className }) {
  const entry = STRINGS[k];
  if (!entry) return k;
  return <Bi tamil={format(entry.ta, vars)} english={format(entry.en, vars)} className={className} />;
}
