const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

/** An error from the backend. `detail` is FastAPI's error detail: a string, a list of
 * validation problems, or `{ code, message, ... }` for errors the UI explains itself
 * (see components/ErrorNote.jsx). `message` is always readable text, never raw JSON. */
export class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

/** Stand-in error for "the backend can't be reached", e.g. when a health check fails. */
export const OFFLINE_ERROR = new ApiError("Backend not reachable", 0, { code: "offline" });

function describe(detail, fallback) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((problem) => [problem.loc?.filter((part) => part !== "body").join(" › "), problem.msg].filter(Boolean).join(": "))
      .join("; ");
  }
  return detail?.message || fallback;
}

async function request(path, { method = "GET", body } = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("Backend not reachable", 0, { code: "offline" });
  }
  if (!res.ok) {
    const text = await res.text();
    let detail = text;
    try {
      detail = JSON.parse(text).detail ?? text;
    } catch {
      // plain-text body (e.g. "Internal Server Error")
    }
    throw new ApiError(describe(detail, `${res.status} ${res.statusText}`), res.status, detail);
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),

  listSigns: (category) => request(`/signs${category ? `?category=${encodeURIComponent(category)}` : ""}`),
  categories: () => request("/signs/categories"),
  createSign: (sign) => request("/signs", { method: "POST", body: sign }),
  deleteSign: (signId) => request(`/signs/${encodeURIComponent(signId)}`, { method: "DELETE" }),

  sampleStats: () => request("/samples/stats"),
  createSample: (sample) => request("/samples", { method: "POST", body: sample }),
  deleteSample: (sampleId) => request(`/samples/${encodeURIComponent(sampleId)}`, { method: "DELETE" }),

  train: () => request("/train", { method: "POST" }),

  predict: (sessionId, window, aspect) =>
    request("/predict", { method: "POST", body: { session_id: sessionId, window, aspect } }),
  resetSession: (sessionId) => request(`/predict/reset/${encodeURIComponent(sessionId)}`, { method: "POST" }),

  translate: (words) => request("/translate", { method: "POST", body: { words } }),
};

export { API_BASE };
