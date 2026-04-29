import axios, { AxiosError } from 'axios';
import { API_BASE_URL } from './config';

export interface AppError {
  message: string;
  status: number;
  detail?: unknown;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Crucial for sending HttpOnly cookies with requests
});

// Helper: read a cookie value by name
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

// Request interceptor: attach CSRF token to all mutating requests
apiClient.interceptors.request.use((config) => {
  const method = config.method?.toUpperCase();
  if (method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['x-csrf-token'] = csrfToken;
    }
  }
  return config;
});

// Response interceptor for global error handling and 401 redirects
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // On 401 response, dispatch event so AuthContext can log user out
    if (error.response?.status === 401) {
      window.dispatchEvent(new Event('auth:unauthorized'));
    }

    // Normalize error into AppError
    const data = error.response?.data as any;

    let message = 'An unexpected error occurred';
    if (data?.detail) {
        // FastAPI sometimes returns detail as a string, sometimes as an array of objects
        message = typeof data.detail === 'string' ? data.detail : 'Validation error';
    } else if (error.message) {
        message = error.message;
    }

    const appError: AppError = {
      message,
      status: error.response?.status || 500,
      detail: data?.detail || null,
    };

    return Promise.reject(appError);
  }
);

export default apiClient;