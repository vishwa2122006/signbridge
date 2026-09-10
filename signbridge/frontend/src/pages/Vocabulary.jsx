import React, { useCallback, useEffect, useMemo, useState } from "react";
import { T } from "../components/Bilingual.jsx";
import ErrorNote from "../components/ErrorNote.jsx";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";
import { categoryStyle } from "../colors.js";
import { t } from "../i18n.js";

export default function Vocabulary() {
  const { lang } = useLanguage();
  const [signs, setSigns] = useState([]);
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [error, setError] = useState(null);

  const load = useCallback(() => api.listSigns().then(setSigns).catch(setError), []);

  useEffect(() => {
    load();
    api.categories().then(setCategories).catch(() => {});
  }, [load]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return signs.filter(
      (s) => (!category || s.category === category) && (!q || s.english.toLowerCase().includes(q) || s.tamil.includes(q)),
    );
  }, [signs, search, category]);

  const tiles = [
    { key: "totalWords", hue: 265, value: signs.length },
    { key: "trained", hue: 150, value: signs.filter((s) => s.trained).length },
    { key: "customWords", hue: 38, value: signs.filter((s) => s.source === "custom").length },
    { key: "totalSamples", hue: 330, value: signs.reduce((n, s) => n + s.samples, 0) },
  ];

  const remove = async (sign) => {
    if (!window.confirm(t("confirmDeleteWord", lang))) return;
    try {
      await api.deleteSign(sign.sign_id);
      await load();
    } catch (e) {
      setError(e);
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2 className="page-title">
          📚 <T k="navVocabulary" />
        </h2>
        <p className="dim">
          <T k="vocabIntro" />
        </p>
      </div>

      <div className="metrics">
        {tiles.map((tile) => (
          <div key={tile.key} className="metric-tile" style={{ "--hue": tile.hue }}>
            <div className="metric">{tile.value}</div>
            <div className="small">
              <T k={tile.key} />
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="toolbar">
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("searchWords", lang)}
            className="grow"
          />
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">{t("allCategories", lang)}</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <ErrorNote error={error} />

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>
                  <T k="tamil" />
                </th>
                <th>
                  <T k="english" />
                </th>
                <th>
                  <T k="category" />
                </th>
                <th>
                  <T k="samples" />
                </th>
                <th>
                  <T k="status" />
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.sign_id}>
                  <td className="word-ta">{s.tamil}</td>
                  <td>
                    {s.english} {s.is_emergency === "yes" && "🚨"}
                  </td>
                  <td className="nowrap">
                    <span className="tag" style={categoryStyle(s.category)}>
                      {s.category.replace(/_/g, " ")}
                    </span>
                    {s.source === "custom" && <span className="pill custom">{t("custom", lang)}</span>}
                  </td>
                  <td>{s.samples > 0 ? <span className="count-pill">{s.samples}</span> : <span className="dim">0</span>}</td>
                  <td className="nowrap">
                    <span className={`pill ${s.trained ? "trained" : "untrained"}`}>
                      {s.trained ? `✓ ${t("trained", lang)}` : t("notTrained", lang)}
                    </span>
                    {s.source === "custom" && (
                      <button className="secondary small row-action" onClick={() => remove(s)}>
                        🗑 <T k="delete" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
