/**
 * Authentication API client.
 */

import { getToken } from '@/lib/auth/better-auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://sajida85-face-2todo.hf.space';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
  };
}

interface RegisterResponse {
  message: string;
  user: {
    id: string;
    email: string;
  };
}

interface VerifyEmailResponse {
  message: string;
}

interface ResendVerificationRequest {
  email: string;
}

interface ResendVerificationResponse {
  message: string;
}

/**
 * Login user with email and password.
 */
async function login(credentials: LoginRequest): Promise<LoginResponse> {
  console.log('authApi.login: Sending request to', `${API_URL}/api/v1/auth/login`);

  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: credentials.email,
      password: credentials.password,
    }),
  });

  console.log('authApi.login: Response status:', response.status);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    console.error('authApi.login: Error response:', error);
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();
  console.log('authApi.login: Success response:', data);
  return data;
}

/**
 * Register a new user.
 */
async function register(credentials: RegisterRequest): Promise<RegisterResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

/**
 * Logout the current user.
 */
async function logout(): Promise<void> {
  const token = getToken();
  if (!token) return;

  try {
    await fetch(`${API_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.error('Logout request failed:', error);
    // Continue with local logout even if API call fails
  }
}

/**
 * Verify email with token from email link.
 */
async function verifyEmail(token: string): Promise<VerifyEmailResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/verify-email?token=${token}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Email verification failed' }));
    throw new Error(error.detail || 'Email verification failed');
  }

  return response.json();
}

/**
 * Resend verification email.
 */
async function resendVerification(data: ResendVerificationRequest): Promise<ResendVerificationResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/resend-verification`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to resend verification email' }));
    throw new Error(error.detail || 'Failed to resend verification email');
  }

  return response.json();
}

export const authApi = {
  login,
  register,
  logout,
  verifyEmail,
  resendVerification,
};
