import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  // Do not attach an old token to the login request.
  if (
    token &&
    !config.url?.includes("/api/v1/auth/token") &&
    !config.url?.includes("/api/v1/auth/login")
  ) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;
