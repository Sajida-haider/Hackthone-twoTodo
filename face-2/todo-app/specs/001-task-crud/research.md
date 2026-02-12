# Research: Task CRUD Implementation

**Feature**: Task CRUD (001-task-crud)
**Date**: 2026-02-08
**Phase**: Phase 0 - Research & Technology Validation

## Research Objectives

This document captures research findings for implementing the Task CRUD feature with FastAPI backend, Next.js frontend, and JWT-based authentication.

---

## 1. JWT Validation in FastAPI

### Decision
Use `python-jose[cryptography]` library for JWT token validation in FastAPI with dependency injection pattern.

### Rationale
- Industry-standard library for JWT operations in Python
- Supports multiple algorithms (HS256, RS256)
- Integrates well with FastAPI's dependency injection system
- Provides clear error handling for expired/invalid tokens

### Implementation Pattern

```python
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """Extract and validate user ID from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Best Practices
- Always validate token signature and expiration
- Extract user_id from "sub" claim (standard JWT claim)
- Use dependency injection to make endpoints testable
- Return 401 for invalid/expired tokens
- Never trust user_id from request body/query params

### Alternatives Considered
- **PyJWT**: Similar functionality but python-jose has better FastAPI integration
- **Authlib**: More comprehensive but overkill for simple JWT validation

---

## 2. SQLModel with PostgreSQL

### Decision
Use SQLModel with UUID primary keys, proper indexes on foreign keys, and automatic timestamp management.

### Rationale
- SQLModel combines Pydantic validation with SQLAlchemy ORM
- Type-safe database operations
- Automatic SQL generation prevents injection attacks
- Native UUID support in PostgreSQL
- Excellent integration with FastAPI (same author)

### Implementation Pattern

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="pending")
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: "User" = Relationship(back_populates="tasks")
```

### Best Practices
- Use UUID for primary keys (distributed system support)
- Add indexes on foreign keys (user_id)
- Use Field() for validation (max_length, min_length)
- Store timestamps in UTC
- Use default_factory for dynamic defaults
- Define relationships for easier querying

### Database Indexes
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

### Alternatives Considered
- **Raw SQLAlchemy**: More verbose, less type safety
- **Django ORM**: Not compatible with FastAPI async patterns
- **Tortoise ORM**: Good async support but less mature than SQLModel

---

## 3. Better Auth Integration

### Decision
Better Auth issues JWT tokens with standard claims. Backend validates tokens using shared secret from BETTER_AUTH_SECRET environment variable.

### Rationale
- Better Auth handles authentication complexity (password hashing, session management)
- Issues standard JWT tokens with "sub" claim containing user_id
- Tokens stored in httpOnly cookies for security
- Backend only needs to validate signature and extract user_id

### JWT Token Structure
```json
{
  "sub": "user-uuid-here",
  "iat": 1234567890,
  "exp": 1234571490,
  "email": "user@example.com"
}
```

### Integration Points
1. **Frontend**: Better Auth manages login/signup, stores token in httpOnly cookie
2. **API Client**: Extracts token from cookie, adds to Authorization header
3. **Backend**: Validates token signature, extracts user_id from "sub" claim

### Best Practices
- Use same secret key (BETTER_AUTH_SECRET) for signing and validation
- Extract user_id from "sub" claim (standard JWT practice)
- Validate token on every protected endpoint
- Handle token expiration gracefully (401 response)

### Alternatives Considered
- **Custom JWT implementation**: Reinventing the wheel, error-prone
- **Session-based auth**: Doesn't scale well, requires server-side storage
- **OAuth2 with external provider**: Overkill for Phase II requirements

---

## 4. Next.js API Client Patterns

### Decision
Create centralized API client with automatic JWT token injection and error handling.

### Rationale
- Single source of truth for API communication
- Automatic token attachment to all requests
- Consistent error handling across application
- Easy to add logging, retry logic, or other cross-cutting concerns

### Implementation Pattern

```typescript
// lib/api/client.ts
class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async getToken(): Promise<string | null> {
    // Extract token from Better Auth session
    // Implementation depends on Better Auth setup
    return null; // Placeholder
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = await this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Redirect to login
        window.location.href = '/login';
      }
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
```

### Task-Specific API Methods

```typescript
// lib/api/tasks.ts
import { apiClient } from './client';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export const taskApi = {
  create: (data: { title: string; description?: string; due_date?: string }) =>
    apiClient.request<Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  list: () =>
    apiClient.request<Task[]>('/api/tasks'),

  get: (id: string) =>
    apiClient.request<Task>(`/api/tasks/${id}`),

  update: (id: string, data: Partial<Task>) =>
    apiClient.request<Task>(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiClient.request<void>(`/api/tasks/${id}`, {
      method: 'DELETE',
    }),
};
```

### Best Practices
- Centralize all API calls through single client
- Automatically attach authentication token
- Handle common errors (401, 403, 500) consistently
- Use TypeScript interfaces for type safety
- Separate API methods by domain (tasks, users, etc.)

### Alternatives Considered
- **Axios**: Additional dependency, fetch API is sufficient
- **React Query**: Good for caching but adds complexity for MVP
- **SWR**: Similar to React Query, can add later if needed

---

## 5. Error Handling Patterns

### Decision
Use consistent error response format across backend and frontend with appropriate HTTP status codes.

### Rationale
- Predictable error structure makes frontend error handling easier
- HTTP status codes provide semantic meaning
- Detailed error messages help debugging
- Security: Don't reveal sensitive information in errors

### Backend Error Response Format

```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    code: str

# Usage examples
raise HTTPException(
    status_code=400,
    detail="Title cannot be empty",
    headers={"X-Error-Code": "INVALID_TITLE"}
)

raise HTTPException(
    status_code=404,
    detail="Task not found",
    headers={"X-Error-Code": "TASK_NOT_FOUND"}
)

raise HTTPException(
    status_code=401,
    detail="Invalid or expired token",
    headers={"X-Error-Code": "INVALID_TOKEN"}
)
```

### HTTP Status Code Usage

| Status | Use Case | Example |
|--------|----------|---------|
| 200 | Successful GET/PATCH | Task retrieved/updated |
| 201 | Successful POST | Task created |
| 204 | Successful DELETE | Task deleted (no content) |
| 400 | Validation error | Empty title, invalid status |
| 401 | Authentication error | Missing/invalid JWT token |
| 403 | Authorization error | Accessing another user's task |
| 404 | Resource not found | Task ID doesn't exist |
| 500 | Server error | Database connection failure |

### Frontend Error Handling

```typescript
try {
  const task = await taskApi.create({ title: 'New task' });
  // Success handling
} catch (error) {
  if (error.status === 401) {
    // Redirect to login
    router.push('/login');
  } else if (error.status === 400) {
    // Show validation error
    setError(error.message);
  } else {
    // Generic error
    setError('Something went wrong. Please try again.');
  }
}
```

### Security Considerations
- **404 vs 403**: Return 404 for tasks that don't exist OR don't belong to user (don't reveal existence)
- **Error messages**: Don't include sensitive data (other users' info, internal paths)
- **Validation errors**: Be specific but don't expose system internals

### Best Practices
- Use appropriate HTTP status codes
- Provide clear, actionable error messages
- Log errors server-side for debugging
- Don't expose stack traces in production
- Handle errors gracefully in UI (show user-friendly messages)

### Alternatives Considered
- **Custom error codes**: HTTP status codes are sufficient and standard
- **Detailed error objects**: Keep it simple for MVP, can enhance later

---

## Technology Stack Summary

### Backend
- **Framework**: FastAPI 0.104+
- **ORM**: SQLModel 0.0.14+
- **Database Driver**: psycopg2-binary 2.9+
- **JWT**: python-jose[cryptography] 3.3+
- **Testing**: pytest 7.4+, pytest-asyncio 0.21+

### Frontend
- **Framework**: Next.js 16+
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3+
- **Authentication**: Better Auth (JWT enabled)
- **Testing**: Jest, React Testing Library

### Database
- **System**: Neon Serverless PostgreSQL
- **Version**: PostgreSQL 15+
- **Connection**: Via DATABASE_URL environment variable

---

## Implementation Readiness

All research objectives have been completed. Key findings:

✅ **JWT Validation**: python-jose with dependency injection pattern
✅ **SQLModel**: UUID primary keys, proper indexes, automatic timestamps
✅ **Better Auth**: Standard JWT tokens with "sub" claim for user_id
✅ **API Client**: Centralized client with automatic token injection
✅ **Error Handling**: Consistent HTTP status codes and error format

**Status**: Ready to proceed to Phase 1 (Design & Contracts)

---

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- python-jose Documentation: https://python-jose.readthedocs.io/
- JWT Best Practices: https://tools.ietf.org/html/rfc8725
- Next.js Documentation: https://nextjs.org/docs
- Better Auth Documentation: https://www.better-auth.com/docs
