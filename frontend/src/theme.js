import { createTheme, alpha } from "@mui/material/styles";

const getDesignTokens = (mode) => {
  const isDark = mode === "dark";

  return createTheme({
    palette: {
      mode,
      background: {
        default: isDark ? "#0b1220" : "#f6f8fc",
        paper: isDark ? "#0f1a2c" : "#ffffff",
      },
      primary: { main: "#4aa3ff" },
      secondary: { main: "#8b5cf6" },
      success: { main: "#22c55e" },
      warning: { main: "#f59e0b" },
      error: { main: "#ef4444" },
      text: {
        primary: isDark ? "#e5e7eb" : "#0f172a",
        secondary: isDark ? alpha("#e5e7eb", 0.72) : alpha("#0f172a", 0.72),
      },
      divider: isDark ? alpha("#e5e7eb", 0.10) : alpha("#0f172a", 0.10),
    },
    shape: { borderRadius: 14 },
    typography: {
      fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial",
      h4: { fontWeight: 800, letterSpacing: -0.6 },
      h6: { fontWeight: 700, letterSpacing: -0.2 },
      body1: { fontSize: 14 },
      body2: { fontSize: 13 },
      button: { textTransform: "none", fontWeight: 700 },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundImage: isDark
              ? "radial-gradient(1200px 800px at 15% 0%, rgba(74,163,255,.14), transparent 55%)," +
                "radial-gradient(1000px 700px at 85% 10%, rgba(139,92,246,.14), transparent 50%)"
              : "radial-gradient(1200px 800px at 15% 0%, rgba(74,163,255,.18), transparent 55%)," +
                "radial-gradient(1000px 700px at 85% 10%, rgba(139,92,246,.16), transparent 50%)",
            backgroundAttachment: "fixed",
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            border: `1px solid ${
              isDark ? alpha("#e5e7eb", 0.08) : alpha("#0f172a", 0.08)
            }`,
            boxShadow: isDark
              ? "0 12px 40px rgba(0,0,0,.35)"
              : "0 12px 30px rgba(15, 23, 42, .10)",
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            border: `1px solid ${
              isDark ? alpha("#e5e7eb", 0.08) : alpha("#0f172a", 0.08)
            }`,
            boxShadow: isDark
              ? "0 14px 50px rgba(0,0,0,.35)"
              : "0 16px 40px rgba(15, 23, 42, .10)",
            backdropFilter: "blur(8px)",
          },
        },
      },
      MuiButton: {
        styleOverrides: { root: { borderRadius: 12 } },
      },
      MuiTableContainer: {
        styleOverrides: {
          root: {
            borderRadius: 14,
            border: `1px solid ${
              isDark ? alpha("#e5e7eb", 0.08) : alpha("#0f172a", 0.08)
            }`,
          },
        },
      },
    },
  });
};

export default getDesignTokens;