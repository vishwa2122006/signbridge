const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function j(res) {
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  health: () => fetch(`${API_BASE}/health`).then(j),

  listSigns: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetch(`${API_BASE}/signs${qs ? "?" + qs : ""}`).then(j);
  },

  getSign: (signId) => fetch(`${API_BASE}/sign/${signId}`).then(j),

  demoPrioritySigns: () => fetch(`${API_BASE}/signs/demo-priority`).then(j),

  predict: (sessionId, window) =>
    fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, window }),
    }).then(j),

  predictSimulate: (sessionId, signId) =>
    fetch(`${API_BASE}/predict/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, sign_id: signId }),
    }).then(j),

  resetSession: (sessionId) =>
    fetch(`${API_BASE}/predict/reset/${sessionId}`, { method: "POST" }).then(j),

  translateTemplate: (conceptSlugs) =>
    fetch(`${API_BASE}/translate-template`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ concept_slugs: conceptSlugs }),
    }).then(j),

  submitFeedback: (payload) =>
    fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(j),

  registerDatasetSample: (payload) =>
    fetch(`${API_BASE}/dataset/sample`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(j),
};

export { API_BASE };
