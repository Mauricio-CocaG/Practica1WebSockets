import React, { createContext, useMemo, useState, useEffect } from "react";
import { ThemeProvider, CssBaseline } from "@mui/material";
import getDesignTokens from "./theme";

export const ColorModeContext = createContext({
  mode: "dark",
  toggleColorMode: () => {},
});

export function AppThemeProvider({ children }) {
  const [mode, setMode] = useState("dark");

  useEffect(() => {
    const saved = localStorage.getItem("ui-mode");
    if (saved === "light" || saved === "dark") setMode(saved);
  }, []);

  const colorMode = useMemo(
    () => ({
      mode,
      toggleColorMode: () => {
        setMode((prev) => {
          const next = prev === "dark" ? "light" : "dark";
          localStorage.setItem("ui-mode", next);
          return next;
        });
      },
    }),
    [mode]
  );

  const theme = useMemo(() => getDesignTokens(mode), [mode]);

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}