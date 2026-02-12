/**
 * API Client Interface
 *
 * Defines the contract for the centralized API client that communicates
 * with the FastAPI backend (SPEC-1 and SPEC-2).
 *
 * All methods return Promises and may throw APIError on failure.
 */

import { User, Task, CreateTaskData, UpdateTaskData } from '../types'

/**
 * Authentication API methods
 */
export interface AuthAPI {
  /**
   * Register a new user account
   * @param email - User's email address
   * @param password - User's password (min 8 chars)
   * @returns Registration response with user ID
   * @throws APIError on validation failure or duplicate email
   */
  register(email: string, password: string): Promise<RegisterResponse>

  /**
   * Login with email and password
   * @param email - User's email address
   * @param password - User's password
   * @returns Login response with JWT token and user info
   * @throws APIError on invalid credentials or unverified email
   */
  login(email: string, password: string): Promise<LoginResponse>

  /**
   * Logout current user
   * Clears authentication state and notifies backend
   * @returns Success response
   * @throws APIError on server error
   */
  logout(): Promise<void>

  /**
   * Verify email with token from verification link
   * @param token - Verification token from email
   * @returns Verification response
   * @throws APIError on invalid/expired token
   */
  verifyEmail(token: string): Promise<VerifyEmailResponse>

  /**
   * Resend verification email
   * @param email - User's email address
   * @returns Success response
   * @throws APIError on rate limit or already verified
   */
  resendVerification(email: string): Promise<void>
}

/**
 * Task API methods
 * All methods require authentication (JWT token)
 */
export interface TaskAPI {
  /**
   * Get all tasks for authenticated user
   * @returns Array of tasks
   * @throws APIError on authentication failure
   */
  getTasks(): Promise<Task[]>

  /**
   * Get a specific task by ID
   * @param id - Task UUID
   * @returns Task object
   * @throws APIError on not found or unauthorized
   */
  getTask(id: string): Promise<Task>

  /**
   * Create a new task
   * @param data - Task creation data (title, description)
   * @returns Created task with ID and timestamps
   * @throws APIError on validation failure
   */
  createTask(data: CreateTaskData): Promise<Task>

  /**
   * Update an existing task
   * @param id - Task UUID
   * @param data - Task update data (partial)
   * @returns Updated task
   * @throws APIError on not found, unauthorized, or validation failure
   */
  updateTask(id: string, data: UpdateTaskData): Promise<Task>

  /**
   * Delete a task
   * @param id - Task UUID
   * @returns Success response
   * @throws APIError on not found or unauthorized
   */
  deleteTask(id: string): Promise<void>

  /**
   * Toggle task completion status
   * @param id - Task UUID
   * @returns Updated task with toggled completion status
   * @throws APIError on not found or unauthorized
   */
  toggleCompletion(id: string): Promise<Task>
}

/**
 * Complete API client interface
 */
export interface APIClient extends AuthAPI, TaskAPI {
  /**
   * Set authentication token for subsequent requests
   * @param token - JWT token string
   */
  setAuthToken(token: string): void

  /**
   * Clear authentication token
   */
  clearAuthToken(): void

  /**
   * Get current authentication token
   * @returns JWT token string or null
   */
  getAuthToken(): string | null
}

/**
 * API Response Types
 */

export interface RegisterResponse {
  message: string
  userId: string
  email: string
}

export interface LoginResponse {
  accessToken: string
  tokenType: string
  expiresIn: number
  user: {
    id: string
    email: string
  }
}

export interface VerifyEmailResponse {
  message: string
  userId: string
}

/**
 * API Error Structure
 */
export interface APIError extends Error {
  status: number
  message: string
  details?: Record<string, string[]>
}

/**
 * HTTP Methods
 */
export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

/**
 * Request Configuration
 */
export interface RequestConfig {
  method: HTTPMethod
  url: string
  data?: unknown
  params?: Record<string, string>
  headers?: Record<string, string>
  timeout?: number
}

/**
 * Response Structure
 */
export interface APIResponse<T = unknown> {
  data: T
  status: number
  statusText: string
  headers: Record<string, string>
}
