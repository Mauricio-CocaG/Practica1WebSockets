import { useState, useEffect, useMemo } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  Stack,
  IconButton,
  Fade,
  Grow
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import { alpha, useTheme } from "@mui/material/styles";

import { getMetricas, getNodos } from "../services/api";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

function Metricas() {
  const theme = useTheme();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [error, setError] = useState(null);
  const [metricas, setMetricas] = useState([]);
  const [nodos, setNodos] = useState([]);

  const [nodoSeleccionado, setNodoSeleccionado] = useState("todos");
  const [dias, setDias] = useState(7);

  // para “re-animar” el chart cuando cambias filtros
  const chartKey = useMemo(() => `${nodoSeleccionado}-${dias}`, [nodoSeleccionado, dias]);

  useEffect(() => {
    cargarNodos();
  }, []);

  useEffect(() => {
    cargarMetricas();
  }, [nodoSeleccionado, dias]);

  const cargarNodos = async () => {
    try {
      const response = await getNodos();
      if (Array.isArray(response.data)) setNodos(response.data);
      else if (Array.isArray(response.data?.data)) setNodos(response.data.data);
      else setNodos([]);
    } catch (err) {
      console.error("Error cargando nodos:", err);
      setNodos([]);
    }
  };

  const cargarMetricas = async () => {
    setError(null);

    if (metricas.length > 0) setRefreshing(true);
    else setLoading(true);

    try {
      let response;

      // ✅ “Todos los nodos” = NO mandar nodo_id
      if (nodoSeleccionado === "todos") response = await getMetricas(undefined, dias);
      else response = await getMetricas(nodoSeleccionado, dias);

      let datosMetricas = [];
      if (Array.isArray(response.data)) datosMetricas = response.data;
      else if (Array.isArray(response.data?.data)) datosMetricas = response.data.data;
      else if (Array.isArray(response.data?.metricas)) datosMetricas = response.data.metricas;

      setMetricas(datosMetricas);
    } catch (err) {
      console.error(err);
      setError("Error al cargar métricas");
      setMetricas([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading && metricas.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="420px">
        <CircularProgress />
      </Box>
    );
  }

  const gridColor =
    theme.palette.mode === "dark"
      ? "rgba(229,231,235,0.08)"
      : "rgba(15,23,42,0.08)";

  const tooltipBg =
    theme.palette.mode === "dark"
      ? "rgba(15,26,44,0.94)"
      : "rgba(255,255,255,0.98)";

  const datosGrafico =
    metricas.length > 0
      ? metricas
          .slice()
          .reverse()
          .map((m) => {
            const fecha = m.timestamp ? new Date(m.timestamp) : null;

            // ✅ 24h = hora, resto = fecha
            const label =
              fecha
                ? dias === 1
                  ? fecha.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                  : fecha.toLocaleDateString()
                : "Sin fecha";

            return {
              timestamp: label,
              usado: m.espacio_usado || 0,
              porcentaje: m.porcentaje_uso || 0
            };
          })
      : [];

  return (
    <Fade in timeout={250}>
      <Box>
        {/* Header */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            flexDirection: { xs: "column", sm: "row" },
            gap: 1.5,
            mb: 2
          }}
        >
          <Box>
            <Typography variant="h4" fontWeight={800}>
              Historial de Métricas
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Evolución del uso de disco por nodo
            </Typography>
          </Box>

          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              size="small"
              variant="outlined"
              color={refreshing ? "warning" : "success"}
              label={refreshing ? "Actualizando..." : "Listo"}
            />
            <IconButton onClick={cargarMetricas} title="Actualizar">
              <RefreshIcon />
            </IconButton>
          </Stack>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Filtros */}
        <Grid container spacing={2} sx={{ mb: 2.5 }}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Nodo</InputLabel>
              <Select
                value={nodoSeleccionado}
                label="Nodo"
                onChange={(e) => setNodoSeleccionado(e.target.value)}
              >
                <MenuItem value="todos">Todos los nodos</MenuItem>
                {nodos.map((n) => (
                  <MenuItem key={n.id} value={n.id}>
                    {n.nombre || `Nodo ${n.id}`}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Período</InputLabel>
              <Select value={dias} label="Período" onChange={(e) => setDias(e.target.value)}>
                <MenuItem value={1}>Últimas 24 horas</MenuItem>
                <MenuItem value={7}>Últimos 7 días</MenuItem>
                <MenuItem value={15}>Últimos 15 días</MenuItem>
                <MenuItem value={30}>Últimos 30 días</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Gráfico con animación (Grow + Recharts animation) */}
        <Grow in timeout={280}>
          <Paper sx={{ p: 2, mb: 3, borderRadius: 3, position: "relative", overflow: "hidden" }}>
            <Typography variant="h6" fontWeight={900}>
              Evolución del uso de disco
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {nodoSeleccionado === "todos" ? "Todos los nodos" : `Nodo ${nodoSeleccionado}`} ·{" "}
              {dias === 1 ? "24h" : `${dias} días`}
            </Typography>

            {/* Overlay mientras refresca */}
            {refreshing && (
              <Box
                sx={{
                  position: "absolute",
                  inset: 0,
                  zIndex: 2,
                  display: "grid",
                  placeItems: "center",
                  bgcolor: alpha(theme.palette.background.paper, theme.palette.mode === "dark" ? 0.35 : 0.55),
                  backdropFilter: "blur(2px)"
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <CircularProgress size={18} />
                  <Typography variant="body2" fontWeight={700}>
                    Actualizando…
                  </Typography>
                </Stack>
              </Box>
            )}

            {datosGrafico.length > 0 ? (
              <Box sx={{ height: 380 }}>
                <ResponsiveContainer width="100%" height="100%" key={chartKey}>
                  <LineChart data={datosGrafico}>
                    <CartesianGrid stroke={gridColor} strokeDasharray="4 4" />
                    <XAxis
                      dataKey="timestamp"
                      minTickGap={20}
                      interval="preserveStartEnd"
                      tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                    />
                    <YAxis yAxisId="left" tick={{ fill: theme.palette.text.secondary, fontSize: 12 }} />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                    />

                    <RTooltip
                      contentStyle={{
                        background: tooltipBg,
                        border: "none",
                        borderRadius: 10,
                        color: theme.palette.text.primary
                      }}
                      itemStyle={{ color: theme.palette.text.primary }}
                      labelStyle={{ color: theme.palette.text.secondary }}
                    />
                    <Legend />

                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="usado"
                      stroke="#4aa3ff"
                      strokeWidth={2.4}
                      dot={false}
                      isAnimationActive
                      animationDuration={700}
                      name="Usado (GB)"
                    />

                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="porcentaje"
                      stroke="#22c55e"
                      strokeWidth={2.4}
                      dot={false}
                      isAnimationActive
                      animationDuration={700}
                      name="% Uso"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            ) : (
              <Paper sx={{ p: 4, textAlign: "center", mt: 2 }}>
                <Typography>No hay datos de métricas para mostrar</Typography>
              </Paper>
            )}
          </Paper>
        </Grow>

        {/* Tabla (hover + solo scrollbar derecho) */}
        {metricas.length > 0 ? (
          <TableContainer
            component={Paper}
            sx={{
              maxHeight: 520,
              overflowY: "auto",
              overflowX: "hidden",
              borderRadius: 3,

              "&::-webkit-scrollbar": { width: 10, height: 0 },
              "&::-webkit-scrollbar-track": { background: "transparent" },
              "&::-webkit-scrollbar-thumb": {
                backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.18 : 0.20),
                borderRadius: 12,
                border: "3px solid transparent",
                backgroundClip: "content-box"
              },
              "&::-webkit-scrollbar-thumb:hover": {
                backgroundColor: alpha(theme.palette.text.primary, theme.palette.mode === "dark" ? 0.28 : 0.30)
              },

              scrollbarWidth: "thin",
              scrollbarColor: `${alpha(theme.palette.text.primary, 0.25)} transparent`
            }}
          >
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  {["Fecha","Nodo","Disco","Tipo","Capacidad","Usado","Libre","% Uso","IOPS"].map((h) => (
                    <TableCell key={h} sx={{ fontWeight: 900 }}>
                      {h}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>

              <TableBody>
                {metricas.map((m, i) => (
                  <TableRow
                    key={m.id}
                    hover
                    sx={{
                      cursor: "pointer",
                      bgcolor: i % 2 === 0 ? "transparent" : "action.hover",
                      transition: "all .12s ease",
                      "&:hover": { bgcolor: "action.selected", transform: "scale(1.002)" }
                    }}
                  >
                    <TableCell>{m.timestamp ? new Date(m.timestamp).toLocaleString() : "N/A"}</TableCell>
                    <TableCell>{nodos.find((n) => n.id === m.nodo_id)?.nombre || `Nodo ${m.nodo_id}`}</TableCell>
                    <TableCell>{m.nombre_disco || "N/A"}</TableCell>
                    <TableCell>{m.tipo_disco || "N/A"}</TableCell>
                    <TableCell align="right">{m.capacidad_total?.toFixed(1) || 0} GB</TableCell>
                    <TableCell align="right">{m.espacio_usado?.toFixed(1) || 0} GB</TableCell>
                    <TableCell align="right">{m.espacio_libre?.toFixed(1) || 0} GB</TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        fontWeight: 800,
                        color:
                          m.porcentaje_uso > 85
                            ? "error.main"
                            : m.porcentaje_uso > 70
                            ? "warning.main"
                            : "success.main"
                      }}
                    >
                      {m.porcentaje_uso?.toFixed(1) || 0}%
                    </TableCell>
                    <TableCell align="right">{m.iops || 0}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Paper sx={{ p: 4, textAlign: "center" }}>
            <Typography>No hay métricas disponibles</Typography>
          </Paper>
        )}
      </Box>
    </Fade>
  );
}

export default Metricas;