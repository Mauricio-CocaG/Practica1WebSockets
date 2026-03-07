import { useState, useEffect, useMemo } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Paper,
  Chip,
  Stack,
  Tooltip as MuiTooltip,
  IconButton,
  Divider,
  useTheme,
} from "@mui/material";
import { alpha } from "@mui/material/styles";

import RefreshIcon from "@mui/icons-material/Refresh";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import DnsIcon from "@mui/icons-material/Dns";
import SignalWifiStatusbar4BarIcon from "@mui/icons-material/SignalWifiStatusbar4Bar";
import SignalWifiStatusbarConnectedNoInternet4Icon from "@mui/icons-material/SignalWifiStatusbarConnectedNoInternet4";

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from "recharts";

import { getDashboardResumen } from "../services/api";

const COLORS = ["#4aa3ff", "#22c55e", "#f59e0b", "#ef4444"];

function formatGB(value) {
  if (value == null || Number.isNaN(value)) return "0.0 GB";
  const n = Number(value);
  return `${n.toFixed(1)} GB`;
}

function prettyName(raw) {
  if (!raw) return "Nodo";
  const s = String(raw).trim();
  const m = s.match(/(regional|nodo|node)\s*[-_#:]?\s*(\d+)/i);
  if (m) return `${m[1][0].toUpperCase() + m[1].slice(1).toLowerCase()} ${m[2]}`;
  const ip = s.match(/\b\d{1,3}(\.\d{1,3}){3}\b/);
  if (ip) return ip[0];
  return s;
}

function clampPct(n) {
  const v = Number(n || 0);
  return Math.min(100, Math.max(0, v));
}

function Dashboard() {
  const theme = useTheme();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState({ cluster: {}, nodos: [] });

  useEffect(() => {
    cargarDatos();
    const intervalo = setInterval(cargarDatos, 30000);
    return () => clearInterval(intervalo);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cargarDatos = async () => {
    try {
      setRefreshing(true);
      const response = await getDashboardResumen();
      setData(response.data);
      setError(null);
    } catch (err) {
      setError("Error al cargar datos del dashboard");
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const clusterData = data.cluster || {};
  const nodos = Array.isArray(data.nodos) ? data.nodos : [];

  const pieData = useMemo(
    () => [
      { name: "Usado", value: clusterData.espacio_usado_gb || 0 },
      { name: "Libre", value: clusterData.espacio_libre_gb || 0 },
    ],
    [clusterData]
  );

  // ✅ Gráfico vertical SIN nombres: usamos solo un id numérico en X
  const barData = useMemo(() => {
    return nodos.map((n, idx) => ({
      idx,
      fullName: prettyName(n.nombre),
      uso: clampPct(n.porcentaje_uso),
      estado: n.estado || "Desconocido",
    }));
  }, [nodos]);

  const tooltipBg =
    theme.palette.mode === "dark" ? "rgba(15,26,44,0.96)" : "rgba(255,255,255,0.98)";
  const tooltipBorder =
    theme.palette.mode === "dark" ? "rgba(229,231,235,0.14)" : "rgba(15,23,42,0.14)";

  const axisColor = theme.palette.text.secondary;
  const gridColor =
    theme.palette.mode === "dark" ? "rgba(229,231,235,0.08)" : "rgba(15,23,42,0.08)";

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
            Dashboard del Cluster
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Resumen de capacidad, utilización y estado de nodos (auto-refresh 30s)
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
            <IconButton onClick={cargarDatos}>
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

      {/* KPI Cards */}
      <Grid container spacing={2} sx={{ mb: 2.5 }}>
        {[
          {
            title: "Total nodos",
            value: clusterData.total_nodos || nodos.length || 0,
            sub: `Activos: ${clusterData.nodos_activos ?? nodos.filter((n) => n.estado === "Activo").length}`,
            icon: <DnsIcon fontSize="small" />,
          },
          {
            title: "Capacidad total",
            value: `${(clusterData.capacidad_total_gb || 0).toFixed(1)} GB`,
            sub: "Capacidad agregada",
            icon: <StorageRoundedIcon fontSize="small" />,
          },
          {
            title: "Uso global",
            value: `${(clusterData.porcentaje_utilizacion_global || 0).toFixed(1)}%`,
            sub: "Utilización del cluster",
            icon: <StorageRoundedIcon fontSize="small" />,
          },
          {
            title: "Disponibilidad",
            value: `${(clusterData.disponibilidad_porcentaje || 0).toFixed(2)}%`,
            sub: "Nodos activos / total",
            icon: <SignalWifiStatusbar4BarIcon fontSize="small" />,
          },
        ].map((kpi) => (
          <Grid key={kpi.title} item xs={12} sm={6} md={3}>
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
                      {kpi.title}
                    </Typography>
                    <Typography variant="h4" sx={{ mt: 0.5 }}>
                      {kpi.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {kpi.sub}
                    </Typography>
                  </Box>

                  <Box
                    sx={{
                      width: 38,
                      height: 38,
                      borderRadius: 2,
                      display: "grid",
                      placeItems: "center",
                      bgcolor:
                        theme.palette.mode === "dark"
                          ? "rgba(74,163,255,0.14)"
                          : "rgba(74,163,255,0.10)",
                      border: `1px solid ${theme.palette.divider}`,
                    }}
                  >
                    {kpi.icon}
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts */}
      <Grid container spacing={2}>
        {/* Pie */}
        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 2.25 }}>
            <Typography variant="h6" sx={{ fontWeight: 800 }} gutterBottom>
              Distribución de almacenamiento
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
              Usado vs Libre (GB)
            </Typography>

            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="52%"
                  innerRadius={62}
                  outerRadius={110}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>

                <RechartsTooltip
                  contentStyle={{
                    background: tooltipBg,
                    border: `1px solid ${tooltipBorder}`,
                    borderRadius: 12,
                    color: theme.palette.text.primary,
                  }}
                  itemStyle={{ color: theme.palette.text.primary }}
                  labelStyle={{ color: theme.palette.text.secondary }}
                  formatter={(val, name) => [formatGB(val), name]}
                />
              </PieChart>
            </ResponsiveContainer>

            <Divider sx={{ mt: 2, mb: 1.5 }} />
            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 0.5 }}>
              <Chip label={`Usado: ${formatGB(clusterData.espacio_usado_gb)}`} size="small" variant="outlined" />
              <Chip label={`Libre: ${formatGB(clusterData.espacio_libre_gb)}`} size="small" variant="outlined" />
            </Stack>
          </Paper>
        </Grid>

        {/* ✅ Uso por nodo: vertical, limpio, sin nombres */}
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 2.25 }}>
            <Typography variant="h6" sx={{ fontWeight: 800 }} gutterBottom>
              Uso por nodo
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
              Porcentaje de utilización (%) — nombres solo en hover
            </Typography>

            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={barData}
                margin={{ top: 20, right: 20, left: 0, bottom: 10 }}
                barCategoryGap={34} // ✅ espacio entre barras
                barGap={8}
              >
                <CartesianGrid stroke={gridColor} strokeDasharray="4 4" />
                {/* ✅ ocultar ticks y labels del eje X */}
                <XAxis dataKey="idx" tick={false} axisLine={false} />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: axisColor, fontSize: 12 }}
                  tickFormatter={(v) => `${v}%`}
                />

                <RechartsTooltip
                  cursor={{
                    fill: theme.palette.mode === "dark" ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.04)",
                  }}
                  contentStyle={{
                    background: tooltipBg,
                    border: `1px solid ${tooltipBorder}`,
                    borderRadius: 12,
                    color: theme.palette.text.primary,
                  }}
                  itemStyle={{ color: theme.palette.text.primary }}
                  labelStyle={{ color: theme.palette.text.secondary }}
                  labelFormatter={(_label, payload) => {
                    const p = payload?.[0]?.payload;
                    return p ? `${p.fullName}` : "Nodo";
                  }}
                  formatter={(val, _name, payload) => {
                    const estado = payload?.payload?.estado || "—";
                    return [`${Number(val).toFixed(1)}%`, `Uso • ${estado}`];
                  }}
                />

                <Bar
                  dataKey="uso"
                  fill={theme.palette.primary.main}
                  radius={[10, 10, 0, 0]}
                  barSize={34} // ✅ barras grandes
                />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Nodo cards iguales */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ fontWeight: 800, mb: 1 }}>
          Nodos (estado)
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Tarjetas uniformes (mismo tamaño) + hover destacado
        </Typography>

        <Grid container spacing={2}>
          {nodos.map((nodo) => {
            const uso = clampPct(nodo.porcentaje_uso);
            const estado = nodo.estado || "Desconocido";
            const activo = estado === "Activo";

            const colorUso =
              uso >= 90 ? theme.palette.error.main : uso >= 75 ? theme.palette.warning.main : theme.palette.primary.main;

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
                      <Typography variant="caption" sx={{ display: "block", opacity: 0.95 }}>
                        IP: {nodo.ip_address}
                      </Typography>
                      <Typography variant="caption" sx={{ display: "block", opacity: 0.95 }}>
                        Disco: {nodo.tipo_disco || "Desconocido"}
                      </Typography>
                      <Typography variant="caption" sx={{ display: "block", opacity: 0.95 }}>
                        Capacidad: {formatGB(nodo.capacidad_total)}
                      </Typography>
                      <Typography variant="caption" sx={{ display: "block", opacity: 0.95 }}>
                        Usado: {formatGB(nodo.espacio_usado)} ({uso.toFixed(1)}%)
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
                        boxShadow:
                          theme.palette.mode === "dark"
                            ? "0 18px 60px rgba(0,0,0,.55)"
                            : "0 18px 50px rgba(15,23,42,.18)",
                        "& .MuiTooltip-arrow": { color: tooltipBg },
                      },
                    },
                  }}
                >
                  <Card
                    sx={{
                      height: 230, // ✅ todas iguales
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                      cursor: "default",
                      position: "relative",
                      overflow: "hidden",
                      transition:
                        "transform .18s ease, box-shadow .18s ease, border-color .18s ease, filter .18s ease",
                      border: `1px solid ${alpha(theme.palette.primary.main, 0.10)}`,
                      "&:hover": {
                        transform: "translateY(-5px)",
                        borderColor: alpha(theme.palette.primary.main, 0.45),
                        boxShadow:
                          theme.palette.mode === "dark"
                            ? "0 22px 70px rgba(0,0,0,.60)"
                            : "0 22px 60px rgba(15,23,42,.18)",
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
                        <Stack direction="row" spacing={1.25} alignItems="center" sx={{ minWidth: 0 }}>
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
                            <StorageRoundedIcon fontSize="small" />
                          </Box>

                          <Box sx={{ minWidth: 0 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 900 }} noWrap>
                              {prettyName(nodo.nombre)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" noWrap>
                              {nodo.ip_address}
                            </Typography>
                          </Box>
                        </Stack>

                        <Stack direction="row" spacing={1} alignItems="center">
                          {activo ? (
                            <SignalWifiStatusbar4BarIcon fontSize="small" color="success" />
                          ) : (
                            <SignalWifiStatusbarConnectedNoInternet4Icon fontSize="small" color="error" />
                          )}
                          <Chip
                            label={activo ? "Activo" : "No reporta"}
                            color={activo ? "success" : "error"}
                            size="small"
                            variant="outlined"
                          />
                        </Stack>
                      </Stack>

                      <Divider sx={{ my: 1.25 }} />

                      <Stack spacing={0.75}>
                        <Stack direction="row" justifyContent="space-between">
                          <Typography variant="body2" color="text.secondary">
                            Capacidad
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 800 }}>
                            {formatGB(nodo.capacidad_total)}
                          </Typography>
                        </Stack>

                        <Stack direction="row" justifyContent="space-between">
                          <Typography variant="body2" color="text.secondary">
                            Usado
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 800 }}>
                            {formatGB(nodo.espacio_usado)}
                          </Typography>
                        </Stack>

                        <Box sx={{ mt: 0.75 }}>
                          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                            <Typography variant="body2" color="text.secondary">
                              Uso
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 900 }}>
                              {uso.toFixed(1)}%
                            </Typography>
                          </Stack>

                          <Box
                            sx={{
                              height: 11,
                              borderRadius: 999,
                              bgcolor:
                                theme.palette.mode === "dark"
                                  ? "rgba(255,255,255,0.08)"
                                  : "rgba(0,0,0,0.06)",
                              overflow: "hidden",
                              border: `1px solid ${theme.palette.divider}`,
                            }}
                          >
                            <Box
                              sx={{
                                height: "100%",
                                width: `${uso}%`,
                                bgcolor: colorUso,
                                borderRadius: 999,
                                transition: "width .25s ease",
                              }}
                            />
                          </Box>

                          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.6, display: "block" }}>
                            Disco: {nodo.tipo_disco || "Desconocido"}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </MuiTooltip>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    </Box>
  );
}

export default Dashboard;