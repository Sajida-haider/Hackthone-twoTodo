/**
 * API error types and interfaces.
 */

export interface APIError {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, any>;
}

export class APIErrorClass extends Error implements APIError {
  code?: string;
  status?: number;
  details?: Record<string, any>;

  constructor(message: string, code?: string, status?: number, details?: Record<string, any>) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export interface APIResponse<T> {
  data: T;
  message?: string;
}
