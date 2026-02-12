/**
 * Authentication TypeScript types.
 */

export interface User {
  id: string;
  email: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
}

export interface AuthError {
  message: string;
  code?: string;
}
