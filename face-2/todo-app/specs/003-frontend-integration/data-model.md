# Data Model: Frontend Integration

**Feature**: Frontend Integration (SPEC-3)
**Date**: 2026-02-08
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the frontend data models, state structures, and type definitions for the frontend integration. These models represent how data flows through the React application and how state is managed.

## Frontend State Models

### 1. AuthState

**Purpose**: Global authentication state managed by AuthProvider context

**Structure**:
```typescript
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}
```

**Fields**:
- `user`: Current authenticated user information (null if not authenticated)
- `token`: JWT token string (null if not authenticated)
- `isAuthenticated`: Boolean flag indicating authentication status
- `isLoading`: Boolean flag indicating auth operation in progress
- `error`: Error message from auth operations (null if no error)

**Persistence**:
- Token stored in localStorage with key `auth_token`
- State rehydrated on app initialization
- Cleared completely on logout

**State Transitions**:
```
Initial → Loading → Authenticated
Initial → Loading → Unauthenticated (with error)
Authenticated → Loading → Unauthenticated (logout)
Authenticated → Unauthenticated (token expiration)
```

### 2. TaskState

**Purpose**: Task list state for dashboard page

**Structure**:
```typescript
interface TaskState {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  selectedTask: Task | null
}
```

**Fields**:
- `tasks`: Array of task objects belonging to authenticated user
- `isLoading`: Boolean flag indicating task operation in progress
- `error`: Error message from task operations (null if no error)
- `selectedTask`: Currently selected task for edit/delete (null if none)

**Operations**:
- `fetchTasks()`: Load all tasks from API
- `createTask(data)`: Create new task
- `updateTask(id, data)`: Update existing task
- `deleteTask(id)`: Delete task
- `toggleCompletion(id)`: Toggle task completion status

**State Management**:
- Local state (useState) in dashboard component
- No global state needed (tasks only used in dashboard)
- Refetch after mutations to ensure consistency

### 3. FormState

**Purpose**: Generic form state for all forms (registration, login, task creation/editing)

**Structure**:
```typescript
interface FormState<T> {
  values: T
  errors: Record<keyof T, string>
  touched: Record<keyof T, boolean>
  isSubmitting: boolean
  isValid: boolean
}
```

**Fields**:
- `values`: Form field values (generic type T)
- `errors`: Validation error messages keyed by field name
- `touched`: Boolean flags indicating which fields have been interacted with
- `isSubmitting`: Boolean flag indicating form submission in progress
- `isValid`: Boolean flag indicating overall form validity

**Validation**:
- Zod schemas define validation rules
- Validation runs onBlur for each field
- All fields validated on submit
- Errors displayed inline next to fields

**Managed By**: React Hook Form library

### 4. ToastState

**Purpose**: User feedback notifications for success/error messages

**Structure**:
```typescript
interface ToastState {
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
  isVisible: boolean
  duration: number
}
```

**Fields**:
- `message`: Text content of the notification
- `type`: Visual style and icon (success, error, info, warning)
- `isVisible`: Boolean flag controlling visibility
- `duration`: Auto-dismiss duration in milliseconds (default: 3000)

**Behavior**:
- Appears at top-right of screen
- Auto-dismisses after duration
- Can be manually dismissed by clicking close button
- Multiple toasts stack vertically

**Managed By**: Custom useToast hook with context

## Type Definitions

### User Types

```typescript
/**
 * Authenticated user information
 */
interface User {
  id: string              // UUID from backend
  email: string           // User's email address
  isVerified: boolean     // Email verification status
}

/**
 * User registration data
 */
interface RegisterData {
  email: string
  password: string
}

/**
 * User login credentials
 */
interface LoginData {
  email: string
  password: string
}
```

### Task Types

```typescript
/**
 * Task entity from backend
 */
interface Task {
  id: string                    // UUID from backend
  title: string                 // Task title (max 200 chars)
  description: string           // Task description (max 2000 chars)
  isCompleted: boolean          // Completion status
  userId: string                // Owner user ID (for reference)
  createdAt: string             // ISO 8601 timestamp
  updatedAt: string             // ISO 8601 timestamp
}

/**
 * Data for creating a new task
 */
interface CreateTaskData {
  title: string
  description: string
}

/**
 * Data for updating an existing task
 */
interface UpdateTaskData {
  title?: string
  description?: string
  isCompleted?: boolean
}

/**
 * Task display state (UI-specific)
 */
interface TaskDisplayState {
  task: Task
  isEditing: boolean
  isDeleting: boolean
  isSaving: boolean
  error: string | null
}
```

### API Response Types

```typescript
/**
 * Standard API error response
 */
interface APIError {
  status: number                          // HTTP status code
  message: string                         // Error message
  details?: Record<string, string[]>      // Validation errors by field
}

/**
 * Registration response
 */
interface RegisterResponse {
  message: string
  userId: string
  email: string
}

/**
 * Login response
 */
interface LoginResponse {
  accessToken: string
  tokenType: string
  expiresIn: number
  user: {
    id: string
    email: string
  }
}

/**
 * Email verification response
 */
interface VerifyEmailResponse {
  message: string
  userId: string
}

/**
 * Generic success response
 */
interface SuccessResponse {
  message: string
}
```

### Form Validation Types

```typescript
/**
 * Validation error structure
 */
interface ValidationError {
  field: string
  message: string
}

/**
 * Form submission result
 */
type FormSubmitResult<T> =
  | { success: true; data: T }
  | { success: false; errors: ValidationError[] }
```

## State Flow Diagrams

### Authentication Flow

```
[App Start]
    ↓
[Check localStorage for token]
    ↓
[Token exists?] → No → [Unauthenticated State]
    ↓ Yes
[Validate token with backend]
    ↓
[Valid?] → No → [Clear token, Unauthenticated State]
    ↓ Yes
[Authenticated State]
```

### Task Operations Flow

```
[User Action (create/update/delete)]
    ↓
[Set isLoading = true]
    ↓
[Call API with JWT token]
    ↓
[Success?] → No → [Set error, Show toast]
    ↓ Yes
[Update local state]
    ↓
[Refetch tasks from API]
    ↓
[Set isLoading = false]
    ↓
[Show success toast]
```

### Form Validation Flow

```
[User types in field]
    ↓
[Field loses focus (onBlur)]
    ↓
[Run Zod validation for field]
    ↓
[Valid?] → No → [Set field error, Show inline message]
    ↓ Yes
[Clear field error]
    ↓
[User submits form]
    ↓
[Validate all fields]
    ↓
[All valid?] → No → [Show all errors, Focus first error]
    ↓ Yes
[Set isSubmitting = true]
    ↓
[Call API]
    ↓
[Handle response]
```

## Data Validation Rules

### Email Validation

```typescript
const emailSchema = z.string()
  .min(1, 'Email is required')
  .email('Invalid email address')
  .max(255, 'Email too long')
```

### Password Validation

```typescript
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password too long')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
```

### Task Title Validation

```typescript
const titleSchema = z.string()
  .min(1, 'Title is required')
  .max(200, 'Title must be 200 characters or less')
  .trim()
```

### Task Description Validation

```typescript
const descriptionSchema = z.string()
  .max(2000, 'Description must be 2000 characters or less')
  .trim()
```

## State Persistence

### localStorage Keys

```typescript
const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  THEME: 'theme_preference',  // Future: dark mode
} as const
```

### Persistence Strategy

**What to Persist**:
- JWT token (required for session persistence)
- User email (for display in header)
- User ID (for reference)

**What NOT to Persist**:
- Task list (always fetch fresh from API)
- Form state (cleared on navigation)
- Error messages (temporary)
- Loading states (temporary)

**Persistence Timing**:
- Save to localStorage immediately after successful login
- Clear from localStorage immediately on logout
- Rehydrate on app initialization

## Error Handling

### Error Types

```typescript
enum ErrorType {
  VALIDATION = 'validation',      // Client-side validation error
  AUTHENTICATION = 'auth',        // 401 Unauthorized
  AUTHORIZATION = 'forbidden',    // 403 Forbidden
  NOT_FOUND = 'not_found',       // 404 Not Found
  SERVER = 'server',             // 500 Server Error
  NETWORK = 'network',           // Network failure
  UNKNOWN = 'unknown',           // Unexpected error
}
```

### Error Messages

```typescript
const ERROR_MESSAGES = {
  [ErrorType.VALIDATION]: 'Please check your input and try again',
  [ErrorType.AUTHENTICATION]: 'Your session has expired. Please log in again.',
  [ErrorType.AUTHORIZATION]: 'You do not have permission to perform this action',
  [ErrorType.NOT_FOUND]: 'The requested resource was not found',
  [ErrorType.SERVER]: 'Something went wrong on our end. Please try again later.',
  [ErrorType.NETWORK]: 'Network error. Please check your connection and try again.',
  [ErrorType.UNKNOWN]: 'An unexpected error occurred. Please try again.',
}
```

## Performance Considerations

### State Updates

**Optimization Strategies**:
- Use React.memo for expensive components
- Memoize computed values with useMemo
- Debounce form validation (300ms)
- Batch state updates when possible
- Avoid unnecessary re-renders

**Example**:
```typescript
// Memoize filtered tasks
const completedTasks = useMemo(
  () => tasks.filter(task => task.isCompleted),
  [tasks]
)
```

### Data Fetching

**Optimization Strategies**:
- Fetch tasks only when dashboard mounts
- Refetch after mutations (create, update, delete)
- Show stale data while refetching (optimistic UI)
- Cancel in-flight requests on unmount
- Implement request deduplication

## Type Safety

### TypeScript Configuration

**Strict Mode Enabled**:
- `strict: true`
- `noImplicitAny: true`
- `strictNullChecks: true`
- `strictFunctionTypes: true`

**Benefits**:
- Catch errors at compile time
- Better IDE autocomplete
- Self-documenting code
- Easier refactoring

### Type Guards

```typescript
/**
 * Type guard for API errors
 */
function isAPIError(error: unknown): error is APIError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'status' in error &&
    'message' in error
  )
}

/**
 * Type guard for validation errors
 */
function hasValidationErrors(error: APIError): error is APIError & { details: Record<string, string[]> } {
  return 'details' in error && typeof error.details === 'object'
}
```

## Summary

This data model provides:
- Clear state structure for all frontend data
- Type-safe interfaces for all entities
- Validation rules for all user input
- Error handling patterns
- Performance optimization strategies
- State persistence approach

All models align with backend APIs (SPEC-1 and SPEC-2) and constitution requirements.
