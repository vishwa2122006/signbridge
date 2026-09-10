const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const TOKEN_KEY = "signbridge.token";

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

function readToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

let authToken = readToken();
let sessionExpiredHandler = null;

/** Remembers the login token sent with every request; null forgets it. */
export function setAuthToken(token) {
  authToken = token;
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    // storage unavailable - the login lasts until the page is reloaded
  }
}

export const getAuthToken = () => authToken;

/** Called when the backend rejects the login (expired, password changed, account disabled). */
export function onSessionExpired(handler) {
  sessionExpiredHandler = handler;
}

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
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (authToken) headers.Authorization = `Bearer ${authToken}`;
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
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
    if (res.status === 401 && detail?.code === "session_expired") {
      setAuthToken(null);
      sessionExpiredHandler?.();
    }
    throw new ApiError(describe(detail, `${res.status} ${res.statusText}`), res.status, detail);
  }
  return res.json();
}

const post = (path, body) => request(path, { method: "POST", body });

export const api = {
  health: () => request("/health"),

  // accounts
  register: (details) => post("/auth/register", details),
  verifyRegistration: (email, code) => post("/auth/register/verify", { email, code }),
  login: (email, password) => post("/auth/login", { email, password }),
  requestLoginCode: (email) => post("/auth/otp/request", { email }),
  loginWithCode: (email, code) => post("/auth/otp/verify", { email, code }),
  me: () => request("/auth/me"),
  changePassword: (currentPassword, newPassword) =>
    post("/auth/change-password", { current_password: currentPassword, new_password: newPassword }),

  listSigns: (category) => request(`/signs${category ? `?category=${encodeURIComponent(category)}` : ""}`),
  categories: () => request("/signs/categories"),
  createSign: (sign) => post("/signs", sign),
  updateSign: (signId, changes) => request(`/signs/${encodeURIComponent(signId)}`, { method: "PATCH", body: changes }),
  deleteSign: (signId) => request(`/signs/${encodeURIComponent(signId)}`, { method: "DELETE" }),

  sampleStats: () => request("/samples/stats"),
  createSample: (sample) => post("/samples", sample),
  getSample: (sampleId) => request(`/samples/${encodeURIComponent(sampleId)}`),
  deleteSample: (sampleId) => request(`/samples/${encodeURIComponent(sampleId)}`, { method: "DELETE" }),
  submitSamples: (concept) => post("/samples/submit", concept ? { concept } : {}),

  // admin
  reviewQueue: () => request("/review/words"),
  wordRecordings: (concept) => request(`/review/words/${encodeURIComponent(concept)}/samples`),
  deleteWordRecordings: (concept) =>
    request(`/review/words/${encodeURIComponent(concept)}/samples`, { method: "DELETE" }),
  reviewSamples: (approve, reject, note) => post("/review/samples", { approve, reject, note }),
  reviewWord: (signId, action, note) => post(`/review/words/${encodeURIComponent(signId)}`, { action, note }),
  listUsers: () => request("/admin/users"),
  setUserActive: (userId, isActive) =>
    request(`/admin/users/${encodeURIComponent(userId)}`, { method: "PATCH", body: { is_active: isActive } }),
  train: () => post("/train"),
  listModels: () => request("/models"),
  activateModel: (modelId) => post(`/models/${encodeURIComponent(modelId)}/activate`),
  deleteModel: (modelId) => request(`/models/${encodeURIComponent(modelId)}`, { method: "DELETE" }),

  predict: (sessionId, window, aspect) => post("/predict", { session_id: sessionId, window, aspect }),
  resetSession: (sessionId) => post(`/predict/reset/${encodeURIComponent(sessionId)}`),

  translate: (words) => post("/translate", { words }),
  textToSigns: (text) => post("/text-to-signs", { text }).then((res) => res.items),
  signDemo: (concept) => request(`/signs/${encodeURIComponent(concept)}/demo`),
};

export { API_BASE };
