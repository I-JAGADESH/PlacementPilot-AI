import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (
    token &&
    !config.url?.includes("/api/v1/auth/token") &&
    !config.url?.includes("/api/v1/auth/login")
  ) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const isAuthRequest =
        error.config?.url?.includes("/api/v1/auth/login") ||
        error.config?.url?.includes("/api/v1/auth/register") ||
        error.config?.url?.includes("/api/v1/auth/token");

      if (!isAuthRequest) {
        localStorage.removeItem("access_token");
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
