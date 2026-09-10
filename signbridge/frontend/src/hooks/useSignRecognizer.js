import { useCallback, useRef, useState } from "react";
import { api } from "../api.js";

/** Live recognition state for one camera view: sends each landmark window to
 * /predict (never more than one request at a time) and collects each newly
 * recognized word into `words`. */
export function useSignRecognizer() {
  const [sessionId] = useState(() => `s_${Math.random().toString(36).slice(2)}`);
  const inFlight = useRef(false);
  const [result, setResult] = useState(null);
  const [words, setWords] = useState([]);
  const [error, setError] = useState(null);

  const onWindow = useCallback(async (frames, aspect) => {
    if (inFlight.current) return; // drop windows while the backend is busy instead of queueing them
    inFlight.current = true;
    try {
      const res = await api.predict(sessionId, frames, aspect);
      setResult(res);
      setError(null);
      if (res.status === "RECOGNIZED" && res.new_word) {
        setWords((w) => [
          ...w,
          { concept: res.accepted_concept, english: res.english, tamil: res.tamil, is_emergency: res.is_emergency },
        ]);
      }
    } catch (e) {
      setError(e);
    } finally {
      inFlight.current = false;
    }
  }, [sessionId]);

  const addWord = useCallback((word) => setWords((w) => [...w, word]), []);
  const undo = useCallback(() => setWords((w) => w.slice(0, -1)), []);
  const clear = useCallback(() => setWords([]), []);
  const reset = useCallback(async () => {
    await api.resetSession(sessionId).catch(() => {});
    setResult(null);
    setWords([]);
  }, [sessionId]);

  return { result, words, error, onWindow, addWord, undo, clear, reset };
}
