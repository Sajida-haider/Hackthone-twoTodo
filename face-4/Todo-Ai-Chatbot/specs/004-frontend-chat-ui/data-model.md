# Data Model: Frontend Chat UI

**Feature**: Frontend Chat UI for AI Todo Assistant
**Date**: 2026-02-10
**Perspective**: Frontend (TypeScript types and component state)

## Overview

This document defines the data structures used in the frontend chat UI. These are TypeScript types that represent the frontend's view of chat data. The backend owns the actual data models - these are client-side representations.

---

## Core Entities

### Message

Represents a single message in a conversation (user or assistant).

```typescript
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
```

**Field Descriptions**:
- `id`: Unique identifier assigned by backend
- `role`: Either 'user' or 'assistant'
- `content`: The actual message text (max 2000 chars on input)
- `created_at`: UTC timestamp in ISO 8601 format
- `tool_calls`: Optional array of MCP tool invocations (for displaying confirmations)

**Validation Rules**:
- `content` must not be empty
- `content` max length: 2000 characters (enforced on input)
- `role` must be valid MessageRole enum value

**Example**:
```typescript
const userMessage: Message = {
  id: 123,
  role: MessageRole.USER,
  content: "Add a task to buy groceries",
  created_at: "2026-02-10T10:30:00Z"
};

const assistantMessage: Message = {
  id: 124,
  role: MessageRole.ASSISTANT,
  content: "I've added the task 'Buy groceries' to your list.",
  created_at: "2026-02-10T10:30:02Z",
  tool_calls: [{
    tool: "add_task",
    parameters: { title: "Buy groceries" },
    result: "success"
  }]
};
```

---

### ToolCall

Represents an MCP tool invocation by the AI assistant.

```typescript
export interface ToolCall {
  tool: string;                  // Tool name (e.g., "add_task")
  parameters: Record<string, any>; // Tool parameters
  result: 'success' | 'error';   // Execution result
  error_message?: string;        // Optional error details
}
```

**Field Descriptions**:
- `tool`: Name of the MCP tool that was called
- `parameters`: Key-value pairs of tool parameters
- `result`: Whether the tool call succeeded or failed
- `error_message`: Human-readable error message if result is 'error'

**Example**:
```typescript
const successfulToolCall: ToolCall = {
  tool: "complete_task",
  parameters: { task_id: 5 },
  result: "success"
};

const failedToolCall: ToolCall = {
  tool: "delete_task",
  parameters: { task_id: 999 },
  result: "error",
  error_message: "Task not found"
};
```

---

### Conversation

Represents conversation metadata (minimal frontend representation).

```typescript
export interface Conversation {
  id: number;                    // Conversation ID from backend
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
  preview?: string;              // Optional: first message preview
}
```

**Field Descriptions**:
- `id`: Unique identifier assigned by backend
- `created_at`: When conversation was created
- `updated_at`: Last message timestamp
- `preview`: Optional preview text for conversation list (first 50 chars of first message)

**Usage**: Used for conversation list (P3 feature). Current conversation_id stored separately in component state.

**Example**:
```typescript
const conversation: Conversation = {
  id: 42,
  created_at: "2026-02-10T09:00:00Z",
  updated_at: "2026-02-10T10:30:02Z",
  preview: "Add a task to buy groceries"
};
```

---

## Component State Structures

### ChatState

Main state structure for the chat interface component.

```typescript
export interface ChatState {
  conversationId: number | null;  // Current conversation ID (null for new)
  messages: Message[];            // Message history
  isLoading: boolean;             // Waiting for AI response
  error: string | null;           // Error message to display
  inputValue: string;             // Current input field value
}
```

**State Transitions**:
1. **Initial State**: `conversationId: null, messages: [], isLoading: false, error: null, inputValue: ""`
2. **User Typing**: `inputValue` updates
3. **Sending Message**: `isLoading: true, error: null`
4. **Response Received**: `conversationId` set (if new), `messages` updated, `isLoading: false`
5. **Error Occurred**: `error` set, `isLoading: false`

**Example**:
```typescript
const initialState: ChatState = {
  conversationId: null,
  messages: [],
  isLoading: false,
  error: null,
  inputValue: ""
};

const activeState: ChatState = {
  conversationId: 42,
  messages: [
    { id: 123, role: MessageRole.USER, content: "Show my tasks", created_at: "..." },
    { id: 124, role: MessageRole.ASSISTANT, content: "Here are your tasks...", created_at: "..." }
  ],
  isLoading: false,
  error: null,
  inputValue: ""
};
```

---

### ConversationListState

State structure for conversation list (P3 feature).

```typescript
export interface ConversationListState {
  conversations: Conversation[];  // List of user's conversations
  isLoading: boolean;             // Loading conversation list
  error: string | null;           // Error loading list
}
```

**Usage**: Separate component for managing conversation list. Not part of MVP (P3 priority).

---

## API Request/Response Types

### ChatRequest

Request payload for sending a message to the backend.

```typescript
export interface ChatRequest {
  message: string;                // User's message
  conversation_id?: number;       // Optional: existing conversation ID
}
```

**Validation**:
- `message` must not be empty
- `message` max length: 2000 characters
- `conversation_id` optional (omit for new conversation)

**Example**:
```typescript
// New conversation
const newChatRequest: ChatRequest = {
  message: "Add a task to buy groceries"
};

// Existing conversation
const existingChatRequest: ChatRequest = {
  message: "Show my tasks",
  conversation_id: 42
};
```

---

### ChatResponse

Response payload from backend chat endpoint.

```typescript
export interface ChatResponse {
  conversation_id: number;        // Conversation ID (new or existing)
  response: string;               // AI assistant's response text
  tool_calls: ToolCall[];         // Actions performed by AI
}
```

**Field Descriptions**:
- `conversation_id`: ID to use for subsequent messages in this conversation
- `response`: The assistant's message text
- `tool_calls`: Array of MCP tool invocations (may be empty)

**Example**:
```typescript
const chatResponse: ChatResponse = {
  conversation_id: 42,
  response: "I've added the task 'Buy groceries' to your list.",
  tool_calls: [{
    tool: "add_task",
    parameters: { title: "Buy groceries" },
    result: "success"
  }]
};
```

---

### ApiError

Custom error type for API failures.

```typescript
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
```

**Usage**:
```typescript
try {
  const response = await sendMessage(message, conversationId);
} catch (error) {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      // Handle auth error
    } else if (error.status === 400) {
      // Handle validation error
    }
  }
}
```

---

## Type Guards

Utility functions for type checking.

```typescript
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
```

---

## Validation Utilities

Input validation functions.

```typescript
export function validateMessageInput(message: string): string | null {
  if (!message || message.trim().length === 0) {
    return "Message cannot be empty";
  }
  if (message.length > 2000) {
    return "Message is too long (max 2000 characters)";
  }
  return null; // Valid
}

export function sanitizeMessageInput(message: string): string {
  return message.trim();
}
```

---

## Constants

```typescript
export const MAX_MESSAGE_LENGTH = 2000;
export const MESSAGE_LOAD_LIMIT = 50; // Max messages to load at once
export const API_TIMEOUT_MS = 30000;   // 30 second timeout
export const RETRY_ATTEMPTS = 3;       // Max retry attempts for failed requests
```

---

## Relationships

```
Conversation (1) ──── (many) Message
                              │
                              └─── (0..many) ToolCall
```

**Description**:
- One Conversation contains many Messages
- Each Message may have zero or more ToolCalls
- Frontend only stores current conversation's messages in state
- Full conversation history loaded from backend on mount

---

## State Management Flow

```
User Input → Validation → API Request → Backend Processing
                                              ↓
                                        ChatResponse
                                              ↓
                                    Update Component State
                                              ↓
                                        Re-render UI
```

**Detailed Flow**:
1. User types message in input field (`inputValue` state)
2. User clicks send button
3. Validate input (length, not empty)
4. Set `isLoading: true`
5. Send API request with message and conversation_id
6. Backend processes and returns ChatResponse
7. Update state:
   - Set `conversationId` (if new conversation)
   - Append user message to `messages`
   - Append assistant response to `messages`
   - Set `isLoading: false`
   - Clear `inputValue`
8. UI re-renders with new messages

**Error Flow**:
1. API request fails
2. Catch error
3. Set `error` state with user-friendly message
4. Set `isLoading: false`
5. Display error message in UI
6. Provide retry button

---

## Notes

### Frontend vs Backend Models

**Important**: These are frontend TypeScript types, not backend database models. The backend owns the actual data models (SQLModel). These types represent the frontend's view of the data as received from the API.

**Key Differences**:
- Frontend uses `number` for IDs (backend may use different types)
- Frontend uses ISO 8601 strings for timestamps (backend uses datetime objects)
- Frontend includes UI-specific fields (e.g., `isLoading`, `error`)
- Frontend may have derived/computed fields (e.g., `preview`)

### Type Safety

All types are exported from `lib/types/chat.ts` and used throughout the application for type safety. This ensures:
- Compile-time type checking
- IntelliSense support in IDEs
- Reduced runtime errors
- Self-documenting code

### Future Enhancements

Potential additions for future versions:
- `MessageStatus` enum (sending, sent, failed)
- `Attachment` type for file uploads
- `Reaction` type for message reactions
- `EditHistory` for message editing
- `SearchResult` type for message search
