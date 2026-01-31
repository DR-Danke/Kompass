import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

console.log('INFO [apiClient]: Initializing API client with base URL:', API_URL);

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - adds auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(`INFO [apiClient]: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: AxiosError) => {
    console.error('ERROR [apiClient]: Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - handles auth errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`INFO [apiClient]: Response ${response.status} from ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error(`ERROR [apiClient]: Response error:`, error.response?.status, error.message);

    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');

      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
