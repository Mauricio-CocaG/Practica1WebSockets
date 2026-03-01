import axios from 'axios';

// Usar la IP de tu servidor
const SERVER_IP = '192.168.100.6';  // 👈 TU IP
const API_URL = `http://${SERVER_IP}:3000/api`;

console.log('📡 Conectando a API:', API_URL);

const API = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Dashboard
export const getDashboardResumen = async () => {
  try {
    const response = await API.get('/dashboard/resumen');
    return response;
  } catch (error) {
    console.error('Error en getDashboardResumen:', error.message);
    throw error;
  }
};

// Nodos
export const getNodos = async () => {
  try {
    const response = await API.get('/nodos');
    return response;
  } catch (error) {
    console.error('Error en getNodos:', error.message);
    throw error;
  }
};

// Métricas
export const getMetricas = async (nodoId = null, dias = 7) => {
  try {
    let url = '/metricas';
    const params = new URLSearchParams();
    if (nodoId) params.append('nodo_id', nodoId);
    if (dias) params.append('dias', dias);
    if (params.toString()) url += `?${params.toString()}`;
    
    const response = await API.get(url);
    return response;
  } catch (error) {
    console.error('Error en getMetricas:', error.message);
    throw error;
  }
};

export default API;