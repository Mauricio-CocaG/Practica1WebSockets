import { Box, AppBar, Toolbar, Typography, CssBaseline, IconButton, Tooltip } from "@mui/material";
import { useContext } from "react";
import Sidebar from "./Sidebar";
import { ColorModeContext } from "../../themeContext.jsx";

import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";

const drawerWidth = 240;

function Layout({ children }) {
  const { mode, toggleColorMode } = useContext(ColorModeContext);

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />

      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backdropFilter: "blur(8px)",
        }}
      >
        <Toolbar>
          {/* Título */}
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Panel de Control - Storage Cluster
          </Typography>

          {/* Botón Dark / Light */}
          <Tooltip title={mode === "dark" ? "Modo claro" : "Modo oscuro"}>
            <IconButton color="inherit" onClick={toggleColorMode}>
              {mode === "dark" ? (
                <LightModeOutlinedIcon />
              ) : (
                <DarkModeOutlinedIcon />
              )}
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Sidebar />

      {/* Contenido principal */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: "64px",
        }}
      >
        {children}
      </Box>
    </Box>
  );
}

export default Layout;