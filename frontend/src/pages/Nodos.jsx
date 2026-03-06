import { useEffect, useMemo, useState } from "react";
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  Stack,
  Chip,
  IconButton,
  Tooltip as MuiTooltip,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  useTheme,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import DnsIcon from "@mui/icons-material/Dns";
import RouterIcon from "@mui/icons-material/Router";
import SignalWifiStatusbar4BarIcon from "@mui/icons-material/SignalWifiStatusbar4Bar";
import SignalWifiStatusbarConnectedNoInternet4Icon from "@mui/icons-material/SignalWifiStatusbarConnectedNoInternet4";
import { alpha } from "@mui/material/styles";

import { getNodos } from "../services/api";

function sanitizeNodoName(raw) {
  if (!raw) return "Nodo";
  const s = String(raw).trim();
  const m = s.match(/(regional|nodo|node)\s*[-_#:]?\s*(\d+)/i);
  if (m) return `${m[1][0].toUpperCase() + m[1].slice(1).toLowerCase()} ${m[2]}`;
  return s.length > 22 ? `${s.slice(0, 22)}…` : s;
}

function formatDateTime(value) {
  if (!value) return "Nunca";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return "—";
  }
}

function formatDate(value) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleDateString();
  } catch {
    return "—";
  }
}

function Nodos() {
  const theme = useTheme();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [nodos, setNodos] = useState([]);

  // ✅ FASE 12: filtro por estado
  const [estadoFiltro, setEstadoFiltro] = useState("TODOS");

  useEffect(() => {
    cargarNodos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cargarNodos = async () => {
    try {
      setRefreshing(true);
      const response = await getNodos();
      setNodos(Array.isArray(response.data) ? response.data : []);
      setError(null);
    } catch (err) {
      setError("Error al cargar nodos");
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const total = nodos.length;
  const activos = nodos.filter((n) => n.estado === "Activo").length;
  const inactivos = total - activos;

  const nodosFiltrados = useMemo(() => {
    if (estadoFiltro === "TODOS") return nodos;
    if (estadoFiltro === "ACTIVO") return nodos.filter((n) => n.estado === "Activo");
    if (estadoFiltro === "NO_REPORTA") return nodos.filter((n) => n.estado !== "Activo");
    return nodos;
  }, [nodos, estadoFiltro]);

  const tooltipBg =
    theme.palette.mode === "dark" ? "rgba(15,26,44,0.94)" : "rgba(255,255,255,0.98)";
  const tooltipBorder =
    theme.palette.mode === "dark" ? "rgba(229,231,235,0.14)" : "rgba(15,23,42,0.14)";

  // estilos hover pro
  const cardBorder = `1px solid ${alpha(theme.palette.primary.main, 0.10)}`;
  const cardHoverBorder = alpha(theme.palette.primary.main, 0.45);
  const cardShadow =
    theme.palette.mode === "dark"
      ? "0 22px 70px rgba(0,0,0,.60)"
      : "0 22px 60px rgba(15,23,42,.18)";

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="420px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          alignItems: { xs: "flex-start", sm: "center" },
          justifyContent: "space-between",
          flexDirection: { xs: "column", sm: "row" },
          gap: 1.5,
          mb: 2,
        }}
      >
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800 }}>
            Gestión de Nodos
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Lista y estado de nodos registrados en el cluster
          </Typography>
        </Box>

        <Stack direction="row" spacing={1} alignItems="center">
          <Chip
            label={refreshing ? "Actualizando..." : "En vivo"}
            color={refreshing ? "warning" : "success"}
            size="small"
            variant="outlined"
          />
          <MuiTooltip title="Actualizar ahora">
            <IconButton onClick={cargarNodos}>
              <RefreshIcon />
            </IconButton>
          </MuiTooltip>
        </Stack>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* KPI cards */}
      <Grid container spacing={2} sx={{ mb: 2.5 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="flex-start"
                spacing={3}
              >
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Total nodos
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 0.5 }}>
                    {total}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    width: 38,
                    height: 38,
                    borderRadius: 2,
                    display: "grid",
                    placeItems: "center",
                    border: `1px solid ${theme.palette.divider}`,
                    bgcolor:
                      theme.palette.mode === "dark"
                        ? "rgba(74,163,255,0.14)"
                        : "rgba(74,163,255,0.10)",
                  }}
                >
                  <DnsIcon fontSize="small" />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="flex-start"
                spacing={3}
              >
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Nodos activos
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 0.5, color: "success.main" }}>
                    {activos}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    width: 38,
                    height: 38,
                    borderRadius: 2,
                    display: "grid",
                    placeItems: "center",
                    border: `1px solid ${theme.palette.divider}`,
                    bgcolor: alpha(theme.palette.success.main, theme.palette.mode === "dark" ? 0.18 : 0.12),
                  }}
                >
                  <SignalWifiStatusbar4BarIcon fontSize="small" />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="flex-start"
                spacing={3}
              >
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Nodos no reporta
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 0.5, color: "error.main" }}>
                    {inactivos}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    width: 38,
                    height: 38,
                    borderRadius: 2,
                    display: "grid",
                    placeItems: "center",
                    border: `1px solid ${theme.palette.divider}`,
                    bgcolor: alpha(theme.palette.error.main, theme.palette.mode === "dark" ? 0.18 : 0.12),
                  }}
                >
                  <SignalWifiStatusbarConnectedNoInternet4Icon fontSize="small" />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filtro (FASE 12) */}
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={1.5}
        alignItems={{ xs: "stretch", sm: "center" }}
        justifyContent="space-between"
        sx={{ mb: 2 }}
      >
        <FormControl size="small" sx={{ minWidth: 220 }}>
          <InputLabel>Estado</InputLabel>
          <Select value={estadoFiltro} label="Estado" onChange={(e) => setEstadoFiltro(e.target.value)}>
            <MenuItem value="TODOS">Todos</MenuItem>
            <MenuItem value="ACTIVO">Activo</MenuItem>
            <MenuItem value="NO_REPORTA">No Reporta</MenuItem>
          </Select>
        </FormControl>

        <Chip label={`Mostrando: ${nodosFiltrados.length}`} size="small" variant="outlined" />
      </Stack>

      {/* Cards por nodo */}
      <Grid container spacing={2}>
        {nodosFiltrados.map((nodo) => {
          const activo = nodo.estado === "Activo";

          return (
            <Grid key={nodo.id} item xs={12} sm={6} md={4} lg={3}>
              <MuiTooltip
                arrow
                placement="top"
                title={
                  <Box sx={{ p: 0.5 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 900 }}>
                      {nodo.nombre}
                    </Typography>
                    <Typography variant="caption" sx={{ display: "block", opacity: 0.9 }}>
                      IP: {nodo.ip_address}
                    </Typography>
                    <Typography variant="caption" sx={{ display: "block", opacity: 0.9 }}>
                      Puerto: {nodo.puerto ?? "—"}
                    </Typography>
                    <Typography variant="caption" sx={{ display: "block", opacity: 0.9 }}>
                      Última conexión: {formatDateTime(nodo.ultima_conexion)}
                    </Typography>
                    <Typography variant="caption" sx={{ display: "block", opacity: 0.9 }}>
                      Registro: {formatDate(nodo.fecha_registro)}
                    </Typography>
                  </Box>
                }
                componentsProps={{
                  tooltip: {
                    sx: {
                      bgcolor: tooltipBg,
                      color: theme.palette.text.primary,
                      border: `1px solid ${tooltipBorder}`,
                      borderRadius: 2,
                      boxShadow: cardShadow,
                      "& .MuiTooltip-arrow": { color: tooltipBg },
                    },
                  },
                }}
              >
                <Card
                  sx={{
                    height: 205, // ✅ todas iguales
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    position: "relative",
                    overflow: "hidden",
                    border: cardBorder,
                    transition:
                      "transform .18s ease, box-shadow .18s ease, border-color .18s ease, filter .18s ease",
                    "&:hover": {
                      transform: "translateY(-5px)",
                      borderColor: cardHoverBorder,
                      boxShadow: cardShadow,
                      filter: "brightness(1.03)",
                    },
                    "&::before": {
                      content: '""',
                      position: "absolute",
                      inset: -2,
                      background:
                        theme.palette.mode === "dark"
                          ? "radial-gradient(700px 160px at 20% 0%, rgba(74,163,255,.28), transparent 60%)"
                          : "radial-gradient(700px 160px at 20% 0%, rgba(74,163,255,.22), transparent 60%)",
                      opacity: 0,
                      transition: "opacity .18s ease",
                      pointerEvents: "none",
                    },
                    "&:hover::before": { opacity: 1 },
                  }}
                >
                  <CardContent sx={{ pb: "16px !important" }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
                      <Stack direction="row" spacing={1.2} alignItems="center" sx={{ minWidth: 0 }}>
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: 2,
                            display: "grid",
                            placeItems: "center",
                            border: `1px solid ${theme.palette.divider}`,
                            bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === "dark" ? 0.16 : 0.10),
                            flexShrink: 0,
                          }}
                        >
                          <RouterIcon fontSize="small" />
                        </Box>

                        <Box sx={{ minWidth: 0 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 900 }} noWrap>
                            {sanitizeNodoName(nodo.nombre)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {nodo.ip_address}
                          </Typography>
                        </Box>
                      </Stack>

                      <Chip
                        label={activo ? "Activo" : "No Reporta"}
                        color={activo ? "success" : "error"}
                        size="small"
                        variant="outlined"
                      />
                    </Stack>

                    <Divider sx={{ my: 1.25 }} />

                    <Stack spacing={0.6}>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">
                          Puerto
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 800 }}>
                          {nodo.puerto ?? "—"}
                        </Typography>
                      </Stack>

                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">
                          Últ. conexión
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 800 }}>
                          {nodo.ultima_conexion ? "Sí" : "Nunca"}
                        </Typography>
                      </Stack>

                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                        Registro: {formatDate(nodo.fecha_registro)}
                      </Typography>
                    </Stack>
                  </CardContent>
                </Card>
              </MuiTooltip>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}

export default Nodos;