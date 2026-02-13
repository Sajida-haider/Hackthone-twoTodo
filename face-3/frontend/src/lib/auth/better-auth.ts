/**
 * Better Auth configuration for frontend authentication.
 */

export const betterAuthConfig = {
  baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3000',
  secret: process.env.BETTER_AUTH_SECRET || 'your-super-secret-key-min-32-chars',
};

/**
 * Get stored JWT token from localStorage.
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Store JWT token in localStorage.
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('auth_token', token);
}

/**
 * Remove JWT token from localStorage.
 */
export function removeToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('auth_token');
}

/**
 * Check if user is authenticated (has valid token).
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}
