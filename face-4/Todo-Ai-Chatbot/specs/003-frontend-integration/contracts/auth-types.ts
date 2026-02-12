/**
 * Authentication Type Definitions
 *
 * Type definitions for authentication-related data structures
 * used throughout the frontend application.
 */

/**
 * User entity
 */
export interface User {
  id: string              // UUID from backend
  email: string           // User's email address
  isVerified: boolean     // Email verification status
}

/**
 * Authentication state
 */
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

/**
 * Registration form data
 */
export interface RegisterFormData {
  email: string
  password: string
  confirmPassword: string  // Frontend only, not sent to API
}

/**
 * Login form data
 */
export interface LoginFormData {
  email: string
  password: string
  rememberMe?: boolean     // Frontend only, affects token persistence
}

/**
 * Auth context value
 */
export interface AuthContextValue {
  // State
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (email: string, password: string) => Promise<void>
  verifyEmail: (token: string) => Promise<void>
  resendVerification: (email: string) => Promise<void>
  clearError: () => void
}

/**
 * Auth event types for logging/analytics
 */
export enum AuthEventType {
  LOGIN_SUCCESS = 'login_success',
  LOGIN_FAILURE = 'login_failure',
  LOGOUT = 'logout',
  REGISTER_SUCCESS = 'register_success',
  REGISTER_FAILURE = 'register_failure',
  VERIFY_SUCCESS = 'verify_success',
  VERIFY_FAILURE = 'verify_failure',
  TOKEN_EXPIRED = 'token_expired',
  TOKEN_REFRESH = 'token_refresh',
}

/**
 * Auth event data
 */
export interface AuthEvent {
  type: AuthEventType
  timestamp: Date
  userId?: string
  error?: string
}

/**
 * Password strength levels
 */
export enum PasswordStrength {
  WEAK = 'weak',
  FAIR = 'fair',
  GOOD = 'good',
  STRONG = 'strong',
}

/**
 * Password validation result
 */
export interface PasswordValidation {
  isValid: boolean
  strength: PasswordStrength
  feedback: string[]
}
