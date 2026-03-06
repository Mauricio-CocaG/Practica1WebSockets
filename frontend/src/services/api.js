import axios from "axios";

// ✅ URL desde .env de Vite
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:3000/api";

console.log("📡 Conectando a API:", API_URL);

const API = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para logging de respuestas
API.interceptors.response.use(
  (response) => {
    console.log(
      `✅ [${response.config.method.toUpperCase()}] ${response.config.url}:`,
      response.status
    );
    return response;
  },
  (error) => {
    console.error(`❌ Error en ${error.config?.url}:`, error.message);
    return Promise.reject(error);
  }
);

// Dashboard
export const getDashboardResumen = async () => {
  const response = await API.get("/dashboard/resumen");
  return response;
};

// Nodos
export const getNodos = async () => {
  const response = await API.get("/nodos");

  let nodosData = [];
  if (Array.isArray(response.data)) {
    nodosData = response.data;
  } else if (response.data?.data && Array.isArray(response.data.data)) {
    nodosData = response.data.data;
  } else if (response.data?.nodos && Array.isArray(response.data.nodos)) {
    nodosData = response.data.nodos;
  } else {
    console.warn("Formato inesperado en getNodos:", response.data);
  }

  return { ...response, data: nodosData };
};

// Métricas
export const getMetricas = async (nodoId = null, dias = 7) => {
  try {
    let url = "/metricas";
    const params = new URLSearchParams();
    if (nodoId) params.append("nodo_id", nodoId);
    if (dias) params.append("dias", dias);
    if (params.toString()) url += `?${params.toString()}`;

    const response = await API.get(url);

    let metricasData = [];
    console.log("📊 Respuesta de métricas (raw):", response.data);

    if (Array.isArray(response.data)) {
      metricasData = response.data;
    } else if (Array.isArray(response.data?.data)) {
      metricasData = response.data.data;
    } else if (Array.isArray(response.data?.metricas)) {
      metricasData = response.data.metricas;
    } else if (Array.isArray(response.data?.results)) {
      metricasData = response.data.results;
    } else {
      console.warn("⚠ Formato inesperado en getMetricas:", response.data);
      if (response.data && typeof response.data === "object") {
        for (const key in response.data) {
          if (Array.isArray(response.data[key])) {
            metricasData = response.data[key];
            console.log(`✅ Usando propiedad '${key}' como array de métricas`);
            break;
          }
        }
      }
    }

    console.log(`📊 Métricas procesadas: ${metricasData.length} registros`);

    return {
      ...response,
      data: metricasData,
      originalData: response.data,
    };
  } catch (error) {
    console.error("❌ Error en getMetricas:", error.message);
    return {
      data: [],
      status: error.response?.status || 500,
      error: error.message,
    };
  }
};

export default API;