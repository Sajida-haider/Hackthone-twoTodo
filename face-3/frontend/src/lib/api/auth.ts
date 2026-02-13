/**
 * Authentication API client.
 */
import { apiClient } from './client';

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  message: string;
  user_id: string;
  email: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
  };
}

export interface VerifyEmailResponse {
  message: string;
  user_id: string;
}

export interface ResendVerificationRequest {
  email: string;
}

export interface ResendVerificationResponse {
  message: string;
}

export interface LogoutResponse {
  message: string;
}

/**
 * Authentication API methods.
 */
export const authApi = {
  /**
   * Register a new user.
   */
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    return apiClient.post<RegisterResponse>('/api/v1/auth/register', data);
  },

  /**
   * Verify email with token.
   */
  verifyEmail: async (token: string): Promise<VerifyEmailResponse> => {
    return apiClient.get<VerifyEmailResponse>(`/api/v1/auth/verify-email?token=${token}`);
  },

  /**
   * Resend verification email.
   */
  resendVerification: async (data: ResendVerificationRequest): Promise<ResendVerificationResponse> => {
    return apiClient.post<ResendVerificationResponse>('/api/v1/auth/resend-verification', data);
  },

  /**
   * Login user.
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return apiClient.post<LoginResponse>('/api/v1/auth/login', data);
  },

  /**
   * Logout user.
   */
  logout: async (): Promise<LogoutResponse> => {
    return apiClient.post<LogoutResponse>('/api/v1/auth/logout');
  },
};
