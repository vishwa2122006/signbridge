import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, getAuthToken, onSessionExpired, setAuthToken } from "./api.js";

const AuthContext = createContext({ user: null, ready: true, isAdmin: false, signIn: () => {}, signOut: () => {} });

/**
 * The logged-in trainer or admin, or null for the public. The token is kept by
 * api.js (localStorage); on page load the account is fetched with it, and a
 * login the backend rejects is dropped.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(() => !getAuthToken());

  useEffect(() => {
    onSessionExpired(() => setUser(null));
    if (!getAuthToken()) return;
    api
      .me()
      .then(setUser)
      .catch(() => {})
      .finally(() => setReady(true));
  }, []);

  const signIn = useCallback(({ token, user: account }) => {
    setAuthToken(token);
    setUser(account);
  }, []);

  const signOut = useCallback(() => {
    setAuthToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, ready, isAdmin: user?.role === "admin", signIn, signOut }),
    [user, ready, signIn, signOut],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
