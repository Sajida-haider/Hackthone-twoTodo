'use client';

/**
 * AuthProvider component for managing authentication state.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { getToken, setToken, removeToken, isAuthenticated } from '@/lib/auth/better-auth';
import type { AuthContextType, User } from '@/types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = () => {
      const storedToken = getToken();
      if (storedToken) {
        setTokenState(storedToken);
        // TODO: Fetch user profile with token
        // For now, just mark as authenticated
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      console.log('AuthProvider: Starting login...', email);
      const response = await authApi.login({ email, password });
      console.log('AuthProvider: Login response received:', response);

      setToken(response.access_token);
      setTokenState(response.access_token);
      setUser({
        id: response.user.id,
        email: response.user.email,
        is_verified: true,
        is_active: true,
        created_at: new Date().toISOString(),
      });

      console.log('AuthProvider: Redirecting to /tasks');
      router.push('/tasks');
    } catch (error) {
      console.error('AuthProvider: Login error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Log error but continue with logout
      console.error('Logout error:', error);
    } finally {
      removeToken();
      setTokenState(null);
      setUser(null);
      router.push('/login');
    }
  };

  const register = async (email: string, password: string) => {
    try {
      await authApi.register({ email, password });
      // Registration successful - user needs to verify email
      router.push('/login?registered=true');
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: isAuthenticated(),
    isLoading,
    login,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context.
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
