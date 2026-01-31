import React, { createContext, useState, useEffect, useCallback } from 'react';
import type { User, LoginCredentials, AuthContextType } from '@/types/auth';
import { authService } from '@/services/authService';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!token && !!user;

  // Validate token on mount
  useEffect(() => {
    const validateToken = async () => {
      console.log('INFO [AuthContext]: Validating stored token');

      if (!token) {
        console.log('INFO [AuthContext]: No token found');
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        console.log('INFO [AuthContext]: Token valid, user loaded');
      } catch (error) {
        console.error('ERROR [AuthContext]: Token validation failed:', error);
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    validateToken();
  }, [token]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    console.log('INFO [AuthContext]: Login attempt');
    const response = await authService.login(credentials);

    localStorage.setItem('token', response.access_token);
    setToken(response.access_token);
    setUser(response.user);
    console.log('INFO [AuthContext]: Login successful');
  }, []);

  const logout = useCallback(() => {
    console.log('INFO [AuthContext]: Logging out');
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  }, []);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
