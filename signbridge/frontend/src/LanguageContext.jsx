import React, { createContext, useContext, useState } from "react";

const LanguageContext = createContext({ lang: "both", setLang: () => {} });

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState("both"); // "ta" | "en" | "both"
  return (
    <LanguageContext.Provider value={{ lang, setLang }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
