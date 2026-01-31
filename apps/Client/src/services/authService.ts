import apiClient from '@/api/clients';
import type { AuthResponse, LoginCredentials, RegisterData, User } from '@/types/auth';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    console.log('INFO [authService]: Attempting login for:', credentials.email);
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    console.log('INFO [authService]: Login successful');
    return response.data;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    console.log('INFO [authService]: Attempting registration for:', data.email);
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    console.log('INFO [authService]: Registration successful');
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    console.log('INFO [authService]: Fetching current user');
    const response = await apiClient.get<User>('/auth/me');
    console.log('INFO [authService]: Current user fetched');
    return response.data;
  },
};
