import { useState, useEffect } from 'react';
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
  Grid
} from '@mui/material';
import { getMetricas, getNodos } from '../services/api';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

function Metricas() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metricas, setMetricas] = useState([]);
  const [nodos, setNodos] = useState([]);
  const [nodoSeleccionado, setNodoSeleccionado] = useState('todos');
  const [dias, setDias] = useState(7);

  useEffect(() => {
    cargarNodos();
  }, []);

  useEffect(() => {
    cargarMetricas();
  }, [nodoSeleccionado, dias]);

  const cargarNodos = async () => {
    try {
      const response = await getNodos();
      setNodos(response.data);
    } catch (err) {
      console.error('Error cargando nodos:', err);
    }
  };

  const cargarMetricas = async () => {
    setLoading(true);
    try {
      const nodoId = nodoSeleccionado === 'todos' ? null : nodoSeleccionado;
      const response = await getMetricas(nodoId, dias);
      setMetricas(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar métricas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && metricas.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  // Preparar datos para el gráfico
  const datosGrafico = metricas.slice().reverse().map(m => ({
    timestamp: new Date(m.timestamp).toLocaleDateString(),
    usado: m.espacio_usado,
    libre: m.espacio_libre,
    porcentaje: m.porcentaje_uso
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Historial de Métricas
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Filtros */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Nodo</InputLabel>
            <Select
              value={nodoSeleccionado}
              label="Nodo"
              onChange={(e) => setNodoSeleccionado(e.target.value)}
            >
              <MenuItem value="todos">Todos los nodos</MenuItem>
              {nodos.map((nodo) => (
                <MenuItem key={nodo.id} value={nodo.id}>
                  {nodo.nombre}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Período</InputLabel>
            <Select
              value={dias}
              label="Período"
              onChange={(e) => setDias(e.target.value)}
            >
              <MenuItem value={1}>Últimas 24 horas</MenuItem>
              <MenuItem value={7}>Últimos 7 días</MenuItem>
              <MenuItem value={15}>Últimos 15 días</MenuItem>
              <MenuItem value={30}>Últimos 30 días</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Gráfico */}
      {datosGrafico.length > 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Evolución del uso de disco
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={datosGrafico}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="usado"
                stroke="#8884d8"
                name="Espacio Usado (GB)"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="porcentaje"
                stroke="#82ca9d"
                name="Porcentaje de Uso (%)"
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      )}

      {/* Tabla de métricas */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Fecha</TableCell>
              <TableCell>Nodo</TableCell>
              <TableCell>Disco</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell align="right">Capacidad</TableCell>
              <TableCell align="right">Usado</TableCell>
              <TableCell align="right">Libre</TableCell>
              <TableCell align="right">% Uso</TableCell>
              <TableCell align="right">IOPS</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {metricas.map((metrica) => (
              <TableRow key={metrica.id}>
                <TableCell>
                  {new Date(metrica.timestamp).toLocaleString()}
                </TableCell>
                <TableCell>
                  {nodos.find(n => n.id === metrica.nodo_id)?.nombre || `Nodo ${metrica.nodo_id}`}
                </TableCell>
                <TableCell>{metrica.nombre_disco}</TableCell>
                <TableCell>{metrica.tipo_disco}</TableCell>
                <TableCell align="right">{metrica.capacidad_total?.toFixed(1)} GB</TableCell>
                <TableCell align="right">{metrica.espacio_usado?.toFixed(1)} GB</TableCell>
                <TableCell align="right">{metrica.espacio_libre?.toFixed(1)} GB</TableCell>
                <TableCell align="right">
                  <Box sx={{ 
                    color: metrica.porcentaje_uso > 85 ? 'error.main' : 
                           metrica.porcentaje_uso > 70 ? 'warning.main' : 'success.main',
                    fontWeight: 'bold'
                  }}>
                    {metrica.porcentaje_uso?.toFixed(1)}%
                  </Box>
                </TableCell>
                <TableCell align="right">{metrica.iops}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default Metricas;