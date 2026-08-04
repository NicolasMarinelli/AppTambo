import axios from "axios";

// URL base de la API — viene de la variable de entorno de Vite
const API_URL = import.meta.env.VITE_API_URL || "https://task-verifiaer-app-production.up.railway.app";

const client = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Interceptor: agrega el token JWT a cada request automáticamente
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor: si el token expiró (401), limpia la sesión
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default client;

// Funciones de auth
export const authAPI = {
  login: (email, password) =>
    client.post("/auth/login", { email, password }),
  register: (payload) =>
    client.post("/auth/register", payload),
  me: () => client.get("/auth/me"),
};