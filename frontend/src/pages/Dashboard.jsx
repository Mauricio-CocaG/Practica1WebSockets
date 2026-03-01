import { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { getDashboardResumen } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({ cluster: {}, nodos: [] });

  useEffect(() => {
    cargarDatos();
    const intervalo = setInterval(cargarDatos, 30000); // Refresh cada 30s
    return () => clearInterval(intervalo);
  }, []);

  const cargarDatos = async () => {
    try {
      const response = await getDashboardResumen();
      setData(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar datos del dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const clusterData = data.cluster;
  const pieData = [
    { name: 'Usado', value: clusterData.espacio_usado_gb || 0 },
    { name: 'Libre', value: clusterData.espacio_libre_gb || 0 }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard del Cluster
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Tarjetas de resumen */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Nodos
              </Typography>
              <Typography variant="h4">
                {clusterData.total_nodos || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Activos: {clusterData.nodos_activos || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Capacidad Total
              </Typography>
              <Typography variant="h4">
                {clusterData.capacidad_total_gb?.toFixed(2) || 0} GB
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Uso Global
              </Typography>
              <Typography variant="h4">
                {clusterData.porcentaje_utilizacion_global?.toFixed(1) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Disponibilidad
              </Typography>
              <Typography variant="h4">
                {clusterData.disponibilidad_porcentaje?.toFixed(2) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Gráficos */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Distribución de Almacenamiento
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Uso por Nodo
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={data.nodos.map(n => ({
                  name: n.nombre?.split(' ')[1] || n.nombre,
                  uso: n.porcentaje_uso || 0
                }))}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="uso" fill="#8884d8" name="% Uso" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Tabla de nodos */}
      <Paper sx={{ mt: 3, p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Estado de Nodos
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nodo</TableCell>
                <TableCell>IP</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell align="right">Capacidad</TableCell>
                <TableCell align="right">Usado</TableCell>
                <TableCell align="right">% Uso</TableCell>
                <TableCell>Tipo Disco</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.nodos.map((nodo) => (
                <TableRow key={nodo.id}>
                  <TableCell>{nodo.nombre}</TableCell>
                  <TableCell>{nodo.ip_address}</TableCell>
                  <TableCell>
                    <Chip
                      label={nodo.estado}
                      color={nodo.estado === 'Activo' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">{nodo.capacidad_total?.toFixed(1)} GB</TableCell>
                  <TableCell align="right">{nodo.espacio_usado?.toFixed(1)} GB</TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                      <Box
                        sx={{
                          width: 50,
                          height: 10,
                          bgcolor: '#eee',
                          borderRadius: 1,
                          mr: 1
                        }}
                      >
                        <Box
                          sx={{
                            width: `${nodo.porcentaje_uso || 0}%`,
                            height: '100%',
                            bgcolor: nodo.porcentaje_uso > 85 ? 'error.main' : 'primary.main',
                            borderRadius: 1
                          }}
                        />
                      </Box>
                      {nodo.porcentaje_uso?.toFixed(1)}%
                    </Box>
                  </TableCell>
                  <TableCell>{nodo.tipo_disco}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}

export default Dashboard;