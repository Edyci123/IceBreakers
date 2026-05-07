import apiClient from '../../lib/apiClient';
import type { AuthUser, LoginRequest, RegisterRequest } from './types';

export const authApi = {
  async getCsrfToken(): Promise<void> {
    await apiClient.get('/auth/csrf');
  },

  async register(data: RegisterRequest): Promise<void> {
    await apiClient.post('/auth/register', data);
  },

  async login(data: LoginRequest): Promise<void> {
    // The backend uses HttpOnly cookies, so we don't return or store a token here.
    await apiClient.post('/auth/login', data);
  },

  async getCurrentUser(): Promise<AuthUser> {
    const response = await apiClient.get<AuthUser>('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    // Note: Logout requires CSRF token verification on the backend according to the router
    // This assumes the browser will include the csrf_token cookie automatically or the apiClient needs to handle it.
    await apiClient.post('/auth/logout');
  }
};