/**
 * Centralized API client for backend communication using Axios.
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getToken, removeToken } from '../auth/better-auth';
import { APIErrorClass } from '@/types/api';

class ApiClient {
  private axiosInstance: AxiosInstance;

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

    // Create Axios instance with base configuration
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    // Request interceptor: attach JWT token
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = getToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor: handle errors
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          const { status, data } = error.response;

          // 401 Unauthorized: Token invalid or expired
          if (status === 401) {
            removeToken();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
          }

          // 403 Forbidden: Access denied
          if (status === 403) {
            throw new APIErrorClass(
              'Access forbidden',
              'FORBIDDEN',
              403,
              data as Record<string, any>
            );
          }

          // 404 Not Found
          if (status === 404) {
            throw new APIErrorClass(
              'Resource not found',
              'NOT_FOUND',
              404,
              data as Record<string, any>
            );
          }

          // 500 Internal Server Error
          if (status === 500) {
            throw new APIErrorClass(
              'Internal server error',
              'SERVER_ERROR',
              500,
              data as Record<string, any>
            );
          }

          // Other errors
          const errorData = data as any;
          throw new APIErrorClass(
            errorData?.detail || errorData?.message || 'API request failed',
            errorData?.code || 'API_ERROR',
            status,
            errorData
          );
        }

        // Network error
        if (error.request) {
          throw new APIErrorClass(
            'Network error. Please check your connection.',
            'NETWORK_ERROR',
            0
          );
        }

        // Other errors
        throw new APIErrorClass(
          error.message || 'An unexpected error occurred',
          'UNKNOWN_ERROR'
        );
      }
    );
  }

  /**
   * GET request helper.
   */
  async get<T>(endpoint: string): Promise<T> {
    const response = await this.axiosInstance.get<T>(endpoint);
    return response.data;
  }

  /**
   * POST request helper.
   */
  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.axiosInstance.post<T>(endpoint, data);
    return response.data;
  }

  /**
   * PATCH request helper.
   */
  async patch<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await this.axiosInstance.patch<T>(endpoint, data);
    return response.data;
  }

  /**
   * DELETE request helper.
   */
  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.axiosInstance.delete<T>(endpoint);
    return response.data;
  }

  /**
   * Direct access to axios instance for custom requests.
   */
  get instance(): AxiosInstance {
    return this.axiosInstance;
  }
}

export const apiClient = new ApiClient();
