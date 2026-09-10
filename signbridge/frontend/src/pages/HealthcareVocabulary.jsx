import React, { useEffect, useState } from "react";
import { useLanguage } from "../LanguageContext.jsx";
import { api } from "../api.js";

export default function HealthcareVocabulary() {
  const { lang } = useLanguage();
  const [signs, setSigns] = useState([]);
  const [category, setCategory] = useState("");

  useEffect(() => {
    api.listSigns(category ? { category } : {}).then(setSigns).catch(() => setSigns([]));
  }, [category]);

  const categories = ["EMERGENCY", "BASIC_NEEDS", "SYMPTOMS", "BODY_PARTS", "MEDICAL_ACTIONS",
    "PATIENT_INFO", "TIME_HISTORY", "MEDICATION", "COMMUNICATION"];

  return (
    <div>
      <div className="card">
        <p>
          {lang !== "en"
            ? "இது ஒரு வேட்பாளர் கருத்துருவாக்கம். ஒவ்வொரு நிரலுக்கும் அதன் சரிபார்ப்பு நிலை காட்டப்படுகிறது — பெரும்பாலானவை இன்னும் 'சரிபார்க்கப்படாதவை' என்பதைக் கவனிக்கவும்."
            : "This is a candidate ontology. Every row shows its validation status — note that most are still 'unverified'. See DATASET_SOURCES.md for what that means and what's needed before a concept can be used in live recognition."}
        </p>
        <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ padding: "0.5em", borderRadius: "8px" }}>
          <option value="">{lang !== "en" ? "அனைத்து பிரிவுகளும்" : "All categories"}</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>{lang !== "en" ? "தமிழ்" : "Tamil"}</th>
              <th>English</th>
              <th>{lang !== "en" ? "பிரிவு" : "Category"}</th>
              <th>{lang !== "en" ? "நிலை" : "Status"}</th>
            </tr>
          </thead>
          <tbody>
            {signs.map((s) => (
              <tr key={s.sign_id}>
                <td>{s.tamil}</td>
                <td>{s.english}</td>
                <td style={{ fontSize: "0.85rem", color: "var(--text-dim)" }}>{s.healthcare_category}</td>
                <td><span className={`pill ${s.validation_status}`}>{s.validation_status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
