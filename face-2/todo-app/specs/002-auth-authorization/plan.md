# Implementation Plan: Authentication & Authorization

**Branch**: `002-auth-authorization` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-auth-authorization/spec.md`

## Summary

Implement a complete authentication and authorization system with JWT tokens, email verification, and user isolation. Users register with email/password, verify their email within 24 hours, login to receive JWT tokens, and access protected resources. The system enforces account lockout after 5 failed login attempts and logs all authentication events for security auditing.

**Technical Approach**:
- Backend: FastAPI with SQLModel ORM for user/token management, JWT validation middleware
- Frontend: Next.js with Better Auth for authentication UI and token management
- Email: SMTP service for verification emails with 24-hour expiring tokens
- Security: bcrypt password hashing, HS256 JWT signing, user isolation at database query level

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, python-jose[cryptography], passlib[bcrypt], python-multipart, email-validator
- Frontend: Next.js 16+, Better Auth, TypeScript, Tailwind CSS
- Email: NEEDS CLARIFICATION (SMTP service provider - SendGrid, AWS SES, or local SMTP)

**Storage**: Neon Serverless PostgreSQL (via DATABASE_URL environment variable)
**Testing**: pytest with pytest-asyncio (backend), React Testing Library (frontend)
**Target Platform**: Web application (Linux server for backend, browser for frontend)
**Project Type**: Web (frontend + backend separation)

**Performance Goals**:
- Registration: <1 minute completion time
- Email delivery: <30 seconds
- Login: <3 seconds token issuance
- Token validation: <50ms latency overhead
- Concurrent requests: 1,000 without degradation

**Constraints**:
- JWT tokens expire in 15 minutes
- Verification tokens expire in 24 hours
- Account lockout: 5 failed attempts → 15 minute lock
- 100% password hashing compliance (no plaintext)
- Generic error messages (prevent user enumeration)

**Scale/Scope**:
- Multi-user application (1,000+ concurrent users)
- 4 user stories (P1-P4)
- 20 functional requirements
- 4 key entities (User, Verification Token, Auth Token, Auth Event)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-First Development (Principle I)
- Specification complete and approved: `specs/002-auth-authorization/spec.md`
- All requirements documented before implementation

### ✅ Phase Awareness (Principle II)
- Feature is within Phase II scope (authentication for web application)
- No AI/chatbot features included

### ✅ Separation of Concerns (Principle III)
- Frontend: Next.js authentication UI, Better Auth integration
- Backend: FastAPI JWT validation, user management APIs
- Database: SQLModel models for User, Verification Token, Auth Event
- Clear layer boundaries maintained

### ✅ Authentication Flow (Principle IV)
- Better Auth handles frontend authentication flow
- JWT tokens issued on successful login
- Tokens included in Authorization header for all requests

### ✅ Authorization Enforcement (Principle V)
- All protected endpoints require valid JWT token
- 401 Unauthorized returned for missing/invalid tokens
- Token validation occurs before business logic

### ✅ User Isolation (Principle VI)
- User identity extracted from JWT token payload
- All database queries filtered by authenticated user_id
- No user_id accepted from client input

### ✅ Shared Secret Management (Principle VII)
- JWT signing/verification uses BETTER_AUTH_SECRET environment variable
- Same secret shared between frontend and backend
- No hardcoded secrets

### ✅ RESTful API Standards (Principle VIII)
- All routes prefixed with `/api/`
- RESTful conventions followed (POST, GET, PATCH, DELETE)
- Proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- JSON responses

### ✅ Task Ownership Enforcement (Principle IX)
- Not applicable to authentication feature (no task ownership in auth endpoints)
- Will be enforced in task CRUD endpoints that depend on this auth system

### ✅ Database Technology (Principle X)
- Neon Serverless PostgreSQL via DATABASE_URL
- No alternative databases used

### ✅ ORM Requirements (Principle XI)
- SQLModel used for all database operations
- No raw SQL queries (except migrations)

### ✅ Schema Compliance (Principle XII)
- Schema will be defined in data-model.md (Phase 1)
- UUID primary keys, created_at/updated_at timestamps
- Foreign keys with proper indexes

### ✅ Next.js App Router (Principle XIII)
- App Router structure for authentication pages
- Server Components by default, Client Components for forms

### ✅ API Client Centralization (Principle XIV)
- Centralized API client with automatic JWT token attachment
- Consistent error handling for 401/403 responses

### ✅ Responsive Design (Principle XV)
- Tailwind CSS for all styling
- Mobile, tablet, desktop responsive layouts

### ✅ Specification Organization (Principle XVI)
- Spec located at `/specs/002-auth-authorization/spec.md`
- Plan, research, data-model, contracts, quickstart to be generated

### ✅ Spec Referencing (Principle XVII)
- Using `@specs/002-auth-authorization/spec.md` notation

### ✅ Spec Updates (Principle XVIII)
- Spec created before implementation
- Any requirement changes will update spec first

### ✅ Agent-Based Workflow (Principle XIX)
- Using appropriate agents for each task domain

### ✅ Implementation Process (Principle XX)
- Following Spec-Driven Development workflow
- Currently in Plan phase

### ✅ Testing Requirements (Principle XXIII)
- pytest for backend unit/integration tests
- React Testing Library for frontend components
- Target: 80% code coverage for business logic

### ✅ Security Practices (Principle XXV)
- No secrets in code (environment variables)
- Input validation on all endpoints
- Parameterized queries via SQLModel
- OWASP Top 10 compliance
- HTTPS for production

**Gate Status**: ✅ PASSED - All applicable constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-authorization/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── register.yaml    # POST /api/auth/register
│   ├── verify-email.yaml # GET /api/auth/verify-email
│   ├── login.yaml       # POST /api/auth/login
│   ├── logout.yaml      # POST /api/auth/logout
│   └── resend-verification.yaml # POST /api/auth/resend-verification
├── checklists/
│   └── requirements.md  # Spec validation checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── user.py              # User SQLModel
│   │   ├── verification_token.py # Verification Token SQLModel
│   │   └── auth_event.py        # Authentication Event SQLModel
│   ├── schemas/
│   │   ├── auth.py              # Auth request/response schemas
│   │   └── user.py              # User schemas
│   ├── api/
│   │   └── v1/
│   │       └── auth.py          # Authentication endpoints
│   ├── core/
│   │   ├── security.py          # JWT validation, password hashing
│   │   ├── config.py            # Configuration management
│   │   └── deps.py              # Dependency injection (get_current_user)
│   ├── services/
│   │   ├── email.py             # Email sending service
│   │   └── auth.py              # Authentication business logic
│   └── middleware/
│       └── auth.py              # JWT validation middleware
└── tests/
    ├── test_auth_register.py    # Registration tests
    ├── test_auth_verify.py      # Email verification tests
    ├── test_auth_login.py       # Login tests
    ├── test_auth_logout.py      # Logout tests
    └── test_auth_middleware.py  # Middleware tests

frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── register/
│   │   │   │   └── page.tsx     # Registration page
│   │   │   ├── login/
│   │   │   │   └── page.tsx     # Login page
│   │   │   ├── verify-email/
│   │   │   │   └── page.tsx     # Email verification page
│   │   │   └── layout.tsx       # Auth layout
│   │   └── layout.tsx           # Root layout with auth provider
│   ├── components/
│   │   └── auth/
│   │       ├── RegisterForm.tsx # Registration form
│   │       ├── LoginForm.tsx    # Login form
│   │       └── AuthProvider.tsx # Better Auth provider wrapper
│   ├── lib/
│   │   ├── auth/
│   │   │   ├── better-auth.ts   # Better Auth configuration
│   │   │   └── auth-client.ts   # Auth API client
│   │   └── api/
│   │       └── client.ts        # Centralized API client with JWT
│   └── types/
│       └── auth.ts              # Auth TypeScript types
└── tests/
    ├── auth/
    │   ├── RegisterForm.test.tsx
    │   └── LoginForm.test.tsx
    └── lib/
        └── auth-client.test.ts
```

**Structure Decision**: Web application structure (Option 2) selected due to clear frontend/backend separation required by constitution. Backend handles all authentication logic and JWT validation. Frontend manages UI and Better Auth integration. This structure enables independent development and deployment of each layer.

## Complexity Tracking

> **No violations - this section is empty**

All constitution principles are satisfied without requiring complexity justifications.

---

## Phase 0: Research ✅ COMPLETE

**Status**: Complete
**Output**: `research.md`

**Key Decisions**:
1. **Email Service**: Configurable SMTP via environment variables (supports SendGrid, AWS SES, local SMTP)
2. **JWT Library**: python-jose[cryptography] (FastAPI recommended)
3. **Password Hashing**: bcrypt via passlib[bcrypt] (OWASP recommended)
4. **Token Storage**: Better Auth default (access token in memory, refresh token in httpOnly cookie)
5. **Account Lockout**: Database counter (simple, persistent)
6. **Verification Tokens**: secrets.token_urlsafe(32) (cryptographically secure)

All technical unknowns resolved. Ready for Phase 1.

---

## Phase 1: Design & Contracts ✅ COMPLETE

**Status**: Complete
**Outputs**:
- `data-model.md` - Database schema with 3 entities (User, VerificationToken, AuthEvent)
- `contracts/register.yaml` - POST /api/auth/register
- `contracts/verify-email.yaml` - GET /api/auth/verify-email
- `contracts/login.yaml` - POST /api/auth/login
- `contracts/logout.yaml` - POST /api/auth/logout
- `contracts/resend-verification.yaml` - POST /api/auth/resend-verification
- `quickstart.md` - Developer setup and testing guide

**Database Schema**:
- Users table with email verification and account lockout fields
- Verification tokens table with 24-hour expiration
- Auth events table for security audit logging
- All tables use UUID primary keys, proper indexes, and timestamps

**API Contracts**:
- 5 RESTful endpoints with OpenAPI 3.0 specifications
- Proper HTTP status codes (200, 201, 400, 401, 403, 404, 429, 500)
- Request/response schemas with validation rules
- Error response examples for all failure scenarios

**Constitution Re-Check**: ✅ PASSED
- All principles remain satisfied after design phase
- Database schema complies with Principle XII (UUID PKs, timestamps, indexes)
- API contracts follow Principle VIII (RESTful, /api/ prefix, JSON responses)
- No new complexity introduced

---

## Phase 2: Task Breakdown

**Status**: Not started (requires `/sp.tasks` command)
**Next Step**: Run `/sp.tasks` to generate `tasks.md` with implementation tasks

The planning phase is complete. All design artifacts are ready for task breakdown and implementation.
