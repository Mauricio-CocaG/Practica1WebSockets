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
  Chip,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import { getNodos } from '../services/api';

function Nodos() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nodos, setNodos] = useState([]);

  useEffect(() => {
    cargarNodos();
  }, []);

  const cargarNodos = async () => {
    try {
      const response = await getNodos();
      setNodos(response.data);
      setError(null);
    } catch (err) {
      setError('Error al cargar nodos');
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Gestión de Nodos
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Resumen de nodos */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Nodos
              </Typography>
              <Typography variant="h4">
                {nodos.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Nodos Activos
              </Typography>
              <Typography variant="h4" color="success.main">
                {nodos.filter(n => n.estado === 'Activo').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Nodos Inactivos
              </Typography>
              <Typography variant="h4" color="error.main">
                {nodos.filter(n => n.estado !== 'Activo').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Nombre</TableCell>
              <TableCell>IP Address</TableCell>
              <TableCell>Puerto</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Última Conexión</TableCell>
              <TableCell>Fecha Registro</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {nodos.map((nodo) => (
              <TableRow key={nodo.id}>
                <TableCell>{nodo.id}</TableCell>
                <TableCell>{nodo.nombre}</TableCell>
                <TableCell>{nodo.ip_address}</TableCell>
                <TableCell>{nodo.puerto}</TableCell>
                <TableCell>
                  <Chip
                    label={nodo.estado}
                    color={nodo.estado === 'Activo' ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {nodo.ultima_conexion ? new Date(nodo.ultima_conexion).toLocaleString() : 'Nunca'}
                </TableCell>
                <TableCell>
                  {new Date(nodo.fecha_registro).toLocaleDateString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default Nodos;