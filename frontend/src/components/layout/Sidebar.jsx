import { Link, useLocation } from "react-router-dom";
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Box,
  Divider,
  Typography,
  useTheme,
} from "@mui/material";
import { alpha } from "@mui/material/styles";

import DashboardIcon from "@mui/icons-material/Dashboard";
import StorageIcon from "@mui/icons-material/Storage";
import BarChartIcon from "@mui/icons-material/BarChart";

const drawerWidth = 260;

const menuItems = [
  { text: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { text: "Nodos", icon: <StorageIcon />, path: "/nodos" },
  { text: "Métricas", icon: <BarChartIcon />, path: "/metricas" },
];

function Sidebar() {
  const location = useLocation();
  const theme = useTheme();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: drawerWidth,
          boxSizing: "border-box",
          borderRight: `1px solid ${theme.palette.divider}`,
          backgroundImage: "none",
          backdropFilter: "blur(10px)",
          backgroundColor: alpha(theme.palette.background.paper, 0.86),
        },
      }}
    >
      <Toolbar sx={{ px: 2.5 }}>
        <Box sx={{ width: "100%" }}>
          <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: -0.4 }}>
            ClusterMonitor
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Storage Cluster UI
          </Typography>
        </Box>
      </Toolbar>

      <Divider sx={{ mx: 2, opacity: 0.6 }} />

      <List sx={{ px: 1.5, py: 1.5 }}>
        {menuItems.map((item) => {
          const active = location.pathname === item.path;

          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.75 }}>
              <ListItemButton
                component={Link}
                to={item.path}
                selected={active}
                sx={{
                  borderRadius: 2,
                  px: 2,
                  py: 1.1,
                  gap: 1,
                  transition: "all .15s ease",
                  "&:hover": {
                    backgroundColor: alpha(theme.palette.primary.main, 0.10),
                    transform: "translateY(-1px)",
                  },
                  ...(active && {
                    backgroundColor: alpha(theme.palette.primary.main, 0.16),
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.22)}`,
                    "&:hover": {
                      backgroundColor: alpha(theme.palette.primary.main, 0.18),
                    },
                  }),
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 38,
                    color: active ? theme.palette.primary.main : theme.palette.text.secondary,
                  }}
                >
                  {item.icon}
                </ListItemIcon>

                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: active ? 800 : 600,
                    letterSpacing: -0.2,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* footer opcional */}
      <Box sx={{ mt: "auto", p: 2 }}>
        <Box
          sx={{
            p: 1.5,
            borderRadius: 2,
            border: `1px solid ${alpha(theme.palette.divider, 0.9)}`,
            background: alpha(theme.palette.background.paper, 0.7),
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 700 }}>
            Estado
          </Typography>
          <Typography variant="caption" color="text.secondary">
            UI lista para monitoreo
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
}

export default Sidebar;