import React from "react";
import { Bi, T } from "./Bilingual.jsx";

const CV_METHOD_KEYS = { "signer-held-out": "cvSignerHeldOut", stratified: "cvStratified" };

const percent = (v) => (typeof v === "number" ? `${Math.round(v * 100)}%` : "—");

function TrainingWarnings({ report, wordOf }) {
  if (!report.warning_codes) {
    // model trained by an older version: English text only
    return (report.warnings || []).map((w) => (
      <div key={w} className="note warn">
        ⚠️ {w}
      </div>
    ));
  }
  return report.warning_codes.map((w) => (
    <div key={w.code} className="note warn">
      ⚠️ {w.code === "few_signers" && <T k="warnFewSigners" vars={{ n: w.signers }} />}
      {w.code === "no_idle" && <T k="warnNoIdle" />}
      {w.code === "no_cv" && <T k="warnNoCv" />}
      {w.code === "mixed_lengths" && (
        <>
          <T k="warnMixedLengths" />
          <span className="chips inline">
            {w.words.map((concept) => (
              <span key={concept} className="chip low">
                <Bi {...wordOf(concept)} />
              </span>
            ))}
          </span>
        </>
      )}
      {w.code === "skipped" && (
        <>
          <T k="warnSkipped" vars={{ min: w.min_samples }} />
          <span className="chips inline">
            {w.words.map((concept) => (
              <span key={concept} className="chip low">
                <Bi {...wordOf(concept)} />
              </span>
            ))}
          </span>
        </>
      )}
    </div>
  ));
}

/** Accuracy, warnings and per-word scores from the last training run (POST /train or /health's model). */
export default function TrainingReport({ report, wordOf }) {
  const tiles = [
    { hue: 170, value: percent(report.cv_accuracy), label: "cvAccuracy", sub: CV_METHOD_KEYS[report.cv_method] },
    { hue: 38, value: percent(report.accepted_rate), label: "acceptedRate", note: `≥ ${percent(report.confidence_threshold)}` },
    { hue: 330, value: percent(report.precision_at_threshold), label: "precisionAtThreshold" },
    { hue: 265, value: `${report.num_samples} / ${report.num_signers}`, label: "samplesSigners" },
  ];
  return (
    <div className="report">
      <div className="toolbar">
        <h3 className="flush">
          📊 <T k="lastTraining" />
        </h3>
        <span className="dim small">{report.trained_at?.replace("T", " ")}</span>
      </div>
      <div className="metrics">
        {tiles.map((tile) => (
          <div key={tile.label} className="metric-tile" style={{ "--hue": tile.hue }}>
            <div className="metric">{tile.value}</div>
            <div className="small">
              <T k={tile.label} />
            </div>
            {tile.sub && (
              <div className="dim small">
                <T k={tile.sub} />
              </div>
            )}
            {tile.note && <div className="dim small">{tile.note}</div>}
          </div>
        ))}
      </div>
      <TrainingWarnings report={report} wordOf={wordOf} />
      {report.per_word?.length > 0 && (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>
                  <T k="word" />
                </th>
                <th>F1</th>
                <th>
                  <T k="samples" />
                </th>
              </tr>
            </thead>
            <tbody>
              {report.per_word.map((w) => (
                <tr key={w.concept}>
                  <td>
                    <Bi {...wordOf(w.concept)} />
                  </td>
                  <td>
                    <div className="score">
                      <div className={`bar${w.f1 < 0.7 ? " low" : ""}`}>
                        <span style={{ width: `${Math.round(w.f1 * 100)}%` }} />
                      </div>
                      {percent(w.f1)}
                    </div>
                  </td>
                  <td>{w.samples}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
