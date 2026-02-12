# Implementation Plan: Task CRUD

**Branch**: `001-task-crud` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-task-crud/spec.md`

## Summary

This plan implements the Task CRUD feature, enabling authenticated users to create, read, update, and delete their own tasks. The feature enforces strict user isolation where each task belongs to exactly one user, and users can only access their own tasks. The implementation follows a full-stack architecture with Next.js frontend, FastAPI backend, and PostgreSQL database, with JWT-based authentication for all operations.

**Primary Requirement**: Implement complete task lifecycle management (Create → View → Update → Delete) with user isolation and authentication.

**Technical Approach**: RESTful API with FastAPI backend using SQLModel ORM for database operations, Next.js App Router frontend with centralized API client, and JWT token validation for all protected endpoints.

## Technical Context

**Language/Version**:
- Backend: Python 3.10+
- Frontend: TypeScript with Next.js 16+

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, python-jose (JWT), psycopg2-binary (PostgreSQL driver)
- Frontend: Next.js, React, Tailwind CSS, Better Auth

**Storage**: Neon Serverless PostgreSQL (accessed via DATABASE_URL environment variable)

**Testing**:
- Backend: pytest with pytest-asyncio for async tests
- Frontend: React Testing Library, Jest
- API: Contract tests for all endpoints

**Target Platform**:
- Backend: Linux/Windows server (containerized deployment)
- Frontend: Web browsers (Chrome, Firefox, Safari, Edge)

**Project Type**: Web application (frontend + backend monorepo)

**Performance Goals**:
- Task creation: < 5 seconds end-to-end
- Task list retrieval: < 2 seconds
- Task updates: < 3 seconds
- Support 100 concurrent users without degradation

**Constraints**:
- All operations require valid JWT authentication
- User isolation enforced at database query level
- Task titles: 1-200 characters
- Task descriptions: 0-2000 characters
- UUID format for all IDs
- Permanent deletion (no soft delete)

**Scale/Scope**:
- Initial target: 100 concurrent users
- Expected task volume: ~50 tasks per user average
- No pagination in MVP (may add later)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance

✅ **I. Spec-First Development**: Specification created and validated before planning
✅ **II. Phase Awareness**: Feature scope limited to Phase II (task management, no AI/chatbot)
✅ **III. Separation of Concerns**: Clear frontend/backend/database separation maintained
✅ **IV. Authentication Flow**: Better Auth handles frontend auth, JWT tokens issued on login
✅ **V. Authorization Enforcement**: All backend endpoints require JWT validation
✅ **VI. User Isolation**: User ID extracted from JWT token, all queries filtered by user_id
✅ **VII. Shared Secret Management**: BETTER_AUTH_SECRET environment variable for JWT operations
✅ **VIII. RESTful API Standards**: All endpoints prefixed with /api/, follow REST conventions
✅ **IX. Task Ownership Enforcement**: Ownership verified on every operation
✅ **X. Database Technology**: Neon PostgreSQL via DATABASE_URL
✅ **XI. ORM Requirements**: SQLModel for all database operations
✅ **XII. Schema Compliance**: Schema will be documented in data-model.md
✅ **XIII. Next.js App Router**: Frontend uses App Router with Server Components
✅ **XIV. API Client Centralization**: Single API client with automatic JWT attachment
✅ **XV. Responsive Design**: Tailwind CSS for all styling
✅ **XVI. Specification Organization**: Proper structure in /specs/001-task-crud/
✅ **XVII. Spec Referencing**: Using @specs/001-task-crud/spec.md notation
✅ **XVIII. Spec Updates**: Spec is source of truth
✅ **XIX. Agent-Based Workflow**: Using specialized agents for implementation
✅ **XX. Implementation Process**: Following Specify → Plan → Tasks → Implement workflow
✅ **XXIII. Testing Requirements**: pytest and React Testing Library planned
✅ **XXV. Security Practices**: Input validation, JWT validation, user isolation enforced

### Gate Status: **PASS** ✅

All constitution principles are satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-crud/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── create-task.yaml
│   ├── list-tasks.yaml
│   ├── get-task.yaml
│   ├── update-task.yaml
│   └── delete-task.yaml
├── checklists/
│   └── requirements.md  # Spec validation (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry
│   ├── config.py                # Configuration and environment variables
│   ├── database.py              # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model (reference only, defined elsewhere)
│   │   └── task.py              # Task SQLModel definition
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py              # Pydantic schemas (TaskCreate, TaskUpdate, TaskRead)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependencies (get_current_user, get_db)
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── tasks.py         # Task CRUD endpoints
│   └── core/
│       ├── __init__.py
│       └── security.py          # JWT validation utilities
└── tests/
    ├── __init__.py
    ├── conftest.py              # Pytest fixtures
    ├── test_task_crud.py        # Task CRUD endpoint tests
    └── test_task_isolation.py  # User isolation tests

frontend/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   └── tasks/
│   │   │       ├── page.tsx     # Task list page
│   │   │       └── [id]/
│   │   │           └── page.tsx # Task detail page
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Home page
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx     # Task list component
│   │   │   ├── TaskItem.tsx     # Individual task component
│   │   │   ├── TaskForm.tsx     # Create/edit task form
│   │   │   └── DeleteTaskButton.tsx
│   │   └── ui/
│   │       └── Button.tsx       # Reusable UI components
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts        # Centralized API client
│   │   │   └── tasks.ts         # Task API methods
│   │   └── types/
│   │       └── task.ts          # TypeScript task types
│   └── hooks/
│       └── useTasks.ts          # Custom hook for task operations
└── tests/
    └── components/
        └── tasks/
            └── TaskList.test.tsx
```

**Structure Decision**: Web application structure selected based on constitution requirements (Principle III: Separation of Concerns). Backend and frontend are completely separated, with backend exposing RESTful API and frontend consuming it through centralized API client. This enables independent development, testing, and deployment of each layer.

## Complexity Tracking

No constitution violations. This section is not applicable.

---

## Phase 0: Research & Technology Validation

### Research Objectives

1. **JWT Validation in FastAPI**: Verify best practices for JWT token validation with python-jose
2. **SQLModel with PostgreSQL**: Confirm UUID primary key support and relationship patterns
3. **Better Auth Integration**: Understand JWT token format and payload structure
4. **Next.js API Client**: Research patterns for centralized API client with automatic token injection
5. **Error Handling Patterns**: Establish consistent error response format across frontend and backend

### Research Findings

*(To be documented in research.md)*

---

## Phase 1: Design & Contracts

### Data Model Design

*(To be documented in data-model.md)*

**Key Entities**:
- Task (with user_id foreign key)
- User (reference only, defined in authentication feature)

**Relationships**:
- One User → Many Tasks
- Task → One User (owner)

### API Contracts

*(To be documented in contracts/ directory)*

**Endpoints**:
1. POST /api/tasks - Create task
2. GET /api/tasks - List user's tasks
3. GET /api/tasks/{id} - Get single task
4. PATCH /api/tasks/{id} - Update task
5. DELETE /api/tasks/{id} - Delete task

### Quickstart Guide

*(To be documented in quickstart.md)*

**Setup Steps**:
1. Environment configuration
2. Database setup
3. Backend startup
4. Frontend startup
5. Testing the feature

---

## Implementation Sequence

### Phase 0: Research (Current Phase)
- Research JWT validation patterns
- Research SQLModel best practices
- Research Next.js API client patterns
- Document findings in research.md

### Phase 1: Design (Next Phase)
- Create data-model.md with Task entity definition
- Generate API contracts in contracts/ directory
- Create quickstart.md with setup instructions
- Update agent context files

### Phase 2: Task Breakdown (After Phase 1)
- Run /sp.tasks to generate implementation tasks
- Tasks will be organized by user story priority (P1, P2, P3)

### Phase 3: Implementation (After Phase 2)
- Execute tasks following /sp.implement workflow
- Backend: Database models, API endpoints, JWT validation
- Frontend: UI components, API client, task management pages
- Testing: Unit tests, integration tests, contract tests

---

## Security Implementation Plan

### Backend Security
1. **JWT Validation**: Validate token signature and expiration on every request
2. **User Extraction**: Extract user_id from validated JWT payload
3. **Query Filtering**: Add WHERE user_id = {authenticated_user_id} to all queries
4. **Input Validation**: Use Pydantic schemas to validate all request bodies
5. **Error Messages**: Return generic errors that don't reveal task existence for other users

### Frontend Security
1. **Token Storage**: Store JWT in httpOnly cookies (handled by Better Auth)
2. **Token Injection**: Automatically attach token to all API requests
3. **Error Handling**: Handle 401/403 errors and redirect to login
4. **Input Sanitization**: Validate user input before sending to backend

---

## Testing Strategy

### Backend Tests
- **Unit Tests**: Test individual functions (validation, user extraction)
- **Integration Tests**: Test complete request/response cycles
- **Contract Tests**: Verify API contracts match OpenAPI specifications
- **Isolation Tests**: Verify users cannot access other users' tasks

### Frontend Tests
- **Component Tests**: Test UI components in isolation
- **Integration Tests**: Test complete user flows
- **API Client Tests**: Mock API responses and test error handling

### Test Coverage Goals
- Backend: Minimum 80% code coverage
- Frontend: Minimum 80% code coverage for business logic
- 100% coverage for security-critical code (JWT validation, user isolation)

---

## Deployment Considerations

### Environment Variables
- **Backend**: DATABASE_URL, BETTER_AUTH_SECRET
- **Frontend**: NEXT_PUBLIC_API_URL

### Database Migrations
- Use Alembic for database schema migrations
- Initial migration creates tasks table with indexes

### Monitoring
- Log all authentication failures
- Log all authorization failures (attempted access to other users' tasks)
- Monitor API response times against success criteria

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| JWT secret mismatch between frontend/backend | High - Authentication fails | Use shared BETTER_AUTH_SECRET environment variable, validate in setup |
| User isolation bypass | Critical - Data breach | Implement defense in depth: validate at API layer, enforce at query level, test thoroughly |
| Performance degradation with large task lists | Medium - Poor UX | Add database indexes on user_id and created_at, consider pagination in future |
| Token expiration during operation | Low - User inconvenience | Implement token refresh mechanism, handle 401 errors gracefully |

---

## Next Steps

1. ✅ Complete Phase 0: Create research.md
2. ✅ Complete Phase 1: Create data-model.md, contracts/, quickstart.md
3. ⏳ Run /sp.tasks to generate implementation tasks
4. ⏳ Execute implementation following task breakdown
5. ⏳ Create PHR for planning session
