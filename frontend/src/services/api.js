import axios from 'axios';

// Usa el proxy de Vite (/api -> http://localhost:3000)
const API_URL = '/api';

const API = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para logging de respuestas (útil para debug)
API.interceptors.response.use(
  response => {
    console.log(`✅ [${response.config.method.toUpperCase()}] ${response.config.url}:`, response.status);
    return response;
  },
  error => {
    console.error(`❌ Error en ${error.config?.url}:`, error.message);
    return Promise.reject(error);
  }
);

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
    
    // Normalizar respuesta para asegurar que siempre devolvemos un array
    let nodosData = [];
    if (response.data && Array.isArray(response.data)) {
      nodosData = response.data;
    } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
      nodosData = response.data.data;
    } else if (response.data && response.data.nodos && Array.isArray(response.data.nodos)) {
      nodosData = response.data.nodos;
    } else {
      console.warn('Formato inesperado en getNodos:', response.data);
      nodosData = [];
    }
    
    return { ...response, data: nodosData };
  } catch (error) {
    console.error('Error en getNodos:', error.message);
    throw error;
  }
};

// Métricas - VERSIÓN MEJORADA
export const getMetricas = async (nodoId = null, dias = 7) => {
  try {
    let url = '/metricas';
    const params = new URLSearchParams();
    if (nodoId) params.append('nodo_id', nodoId);
    if (dias) params.append('dias', dias);
    if (params.toString()) url += `?${params.toString()}`;
    
    const response = await API.get(url);
    
    // NORMALIZAR LA RESPUESTA PARA GARANTIZAR QUE SIEMPRE SEA UN ARRAY
    let metricasData = [];
    
    // Log para debug
    console.log('📊 Respuesta de métricas (raw):', response.data);
    
    if (response.data && Array.isArray(response.data)) {
      // Caso 1: Respuesta es un array directamente
      metricasData = response.data;
    } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
      // Caso 2: Respuesta es { data: [...] }
      metricasData = response.data.data;
    } else if (response.data && response.data.metricas && Array.isArray(response.data.metricas)) {
      // Caso 3: Respuesta es { metricas: [...] }
      metricasData = response.data.metricas;
    } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
      // Caso 4: Respuesta es { results: [...] }
      metricasData = response.data.results;
    } else {
      console.warn('⚠ Formato inesperado en getMetricas:', response.data);
      // Intentar extraer algo si es un objeto
      if (response.data && typeof response.data === 'object') {
        // Buscar cualquier propiedad que sea array
        for (let key in response.data) {
          if (Array.isArray(response.data[key])) {
            metricasData = response.data[key];
            console.log(`✅ Usando propiedad '${key}' como array de métricas`);
            break;
          }
        }
      }
    }
    
    console.log(`📊 Métricas procesadas: ${metricasData.length} registros`);
    
    // Devolver la respuesta con la data normalizada
    return { 
      ...response, 
      data: metricasData,
      originalData: response.data // Opcional: mantener original por si acaso
    };
    
  } catch (error) {
    console.error('❌ Error en getMetricas:', error.message);
    // En caso de error, devolver un array vacío en lugar de propagar el error
    // (esto evita que la UI se rompa)
    return { 
      data: [], 
      status: error.response?.status || 500,
      error: error.message 
    };
  }
};

export default API;