// Chat-related TypeScript types for Frontend Chat UI
// Based on specs/004-frontend-chat-ui/data-model.md

// ============================================================================
// Core Entities
// ============================================================================

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
}

export interface Message {
  id: number;                    // Message ID from backend
  role: MessageRole;             // Who sent the message
  content: string;               // Message text content
  created_at: string;            // ISO 8601 timestamp
  tool_calls?: ToolCall[];       // Optional: actions performed by AI
}

export interface ToolCall {
  tool: string;                  // Tool name (e.g., "add_task")
  parameters: Record<string, any>; // Tool parameters
  result: 'success' | 'error';   // Execution result
  error_message?: string;        // Optional error details
}

export interface Conversation {
  id: number;                    // Conversation ID from backend
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
  preview?: string;              // Optional: first message preview
}

// ============================================================================
// Component State Structures
// ============================================================================

export interface ChatState {
  conversationId: number | null;  // Current conversation ID (null for new)
  messages: Message[];            // Message history
  isLoading: boolean;             // Waiting for AI response
  error: string | null;           // Error message to display
  inputValue: string;             // Current input field value
}

export interface ConversationListState {
  conversations: Conversation[];  // List of user's conversations
  isLoading: boolean;             // Loading conversation list
  error: string | null;           // Error loading list
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface ChatRequest {
  message: string;                // User's message
  conversation_id?: number;       // Optional: existing conversation ID
}

export interface ChatResponse {
  conversation_id: number;        // Conversation ID (new or existing)
  response: string;               // AI assistant's response text
  tool_calls: ToolCall[];         // Actions performed by AI
}

// ============================================================================
// Error Types
// ============================================================================

export class ApiError extends Error {
  status: number;                 // HTTP status code
  details?: any;                  // Optional error details from backend

  constructor(status: number, message: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

// ============================================================================
// Type Guards
// ============================================================================

export function isMessage(obj: any): obj is Message {
  return (
    typeof obj === 'object' &&
    typeof obj.id === 'number' &&
    typeof obj.role === 'string' &&
    typeof obj.content === 'string' &&
    typeof obj.created_at === 'string'
  );
}

export function isMessageRole(value: string): value is MessageRole {
  return value === MessageRole.USER || value === MessageRole.ASSISTANT;
}

export function isChatResponse(obj: any): obj is ChatResponse {
  return (
    typeof obj === 'object' &&
    typeof obj.conversation_id === 'number' &&
    typeof obj.response === 'string' &&
    Array.isArray(obj.tool_calls)
  );
}

// ============================================================================
// Validation Utilities
// ============================================================================

export function validateMessageInput(message: string): string | null {
  if (!message || message.trim().length === 0) {
    return "Message cannot be empty";
  }
  if (message.length > MAX_MESSAGE_LENGTH) {
    return `Message is too long (max ${MAX_MESSAGE_LENGTH} characters)`;
  }
  return null; // Valid
}

export function sanitizeMessageInput(message: string): string {
  return message.trim();
}

// ============================================================================
// Constants
// ============================================================================

export const MAX_MESSAGE_LENGTH = 2000;
export const MESSAGE_LOAD_LIMIT = 50; // Max messages to load at once
export const API_TIMEOUT_MS = 30000;   // 30 second timeout
export const RETRY_ATTEMPTS = 3;       // Max retry attempts for failed requests
