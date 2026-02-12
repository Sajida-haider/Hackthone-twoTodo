---
id: 2
title: Create Authentication Authorization Implementation Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 002-auth-authorization
branch: 002-auth-authorization
user: KARAKORUM TRADERS
command: /sp.plan
labels: ["authentication", "authorization", "jwt", "email-verification", "planning", "architecture"]
links:
  spec: specs/002-auth-authorization/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-auth-authorization/plan.md
  - specs/002-auth-authorization/research.md
  - specs/002-auth-authorization/data-model.md
  - specs/002-auth-authorization/contracts/register.yaml
  - specs/002-auth-authorization/contracts/verify-email.yaml
  - specs/002-auth-authorization/contracts/login.yaml
  - specs/002-auth-authorization/contracts/logout.yaml
  - specs/002-auth-authorization/contracts/resend-verification.yaml
  - specs/002-auth-authorization/quickstart.md
tests:
  - Constitution compliance check (25/25 principles satisfied)
---

## Prompt

User requested creation of implementation plan for Authentication & Authorization (SPEC-2) using /sp.plan command with partial input:

```
You are running Spec-Kit Plus in PLAN mode.

Your task is to create an execution plan
based strictly on SPEC-2.

========================
PLAN METADATA
========================
Related Spec: /specs/features/auth-jwt.md
Spec ID: SPEC-2

========================
OBJECTIVE
========================
Define the step-by-step plan for implementing
authentication and authorization using JWT.

========================
PLAN STRUCTURE
========================
1. Spec Review Phase
   - Identify auth flows
   - Identify security constraints

2. Database Planning Phase
   - User table structure
   - Unique email constraint

3. Backend Auth Planning Phase
   - Registration flow
   - Login flow
   - JWT generation and validation
   - Protected route behavior

4. Middleware Planning Phase
   - Token extraction
   - Token verification
   - User context attachment

5. Testing & Validation Phase
   - Valid auth scenarios
   - Invalid and expired token cases

[input was truncated]
```

## Response snapshot

Successfully created comprehensive implementation plan with Phase 0 (Research) and Phase 1 (Design & Contracts) complete:

**Phase 0: Research (Complete)**

Resolved all technical unknowns:
1. **Email Service**: Configurable SMTP via environment variables (supports SendGrid, AWS SES, local SMTP for development)
2. **JWT Library**: python-jose[cryptography] (FastAPI recommended, supports HS256/RS256)
3. **Password Hashing**: bcrypt via passlib[bcrypt] (OWASP recommended, industry standard)
4. **Token Storage**: Better Auth default strategy (access token in memory, refresh token in httpOnly cookie)
5. **Account Lockout**: Database counter implementation (simple, persistent, no Redis required)
6. **Verification Tokens**: secrets.token_urlsafe(32) (cryptographically secure, 256-bit entropy)

**Phase 1: Design & Contracts (Complete)**

Created comprehensive design artifacts:

1. **Data Model** (data-model.md):
   - User entity: email, password_hash, is_verified, is_active, failed_login_attempts, locked_until
   - VerificationToken entity: token, user_id, expires_at (24 hours), verified_at
   - AuthEvent entity: event_type, user_id, ip_address, user_agent, success, failure_reason
   - All tables use UUID primary keys, proper indexes, timestamps
   - SQLModel implementation examples provided

2. **API Contracts** (5 OpenAPI 3.0 specifications):
   - POST /api/auth/register - User registration with email/password
   - GET /api/auth/verify-email - Email verification via token
   - POST /api/auth/login - Authentication with JWT token issuance
   - POST /api/auth/logout - Token invalidation
   - POST /api/auth/resend-verification - Request new verification email
   - All contracts include request/response schemas, error examples, HTTP status codes

3. **Quickstart Guide** (quickstart.md):
   - Environment setup instructions (backend and frontend)
   - Installation steps with dependency lists
   - Testing procedures for all authentication flows
   - Common issues and solutions
   - Security checklist
   - Development workflow guidance

**Technical Stack Finalized**:
- Backend: FastAPI, SQLModel, python-jose, passlib, email-validator
- Frontend: Next.js 16+, Better Auth, TypeScript, Tailwind CSS
- Database: Neon Serverless PostgreSQL
- Email: Configurable SMTP (development: MailHog, production: SendGrid/AWS SES)

**Constitution Compliance**: All 25 principles verified and satisfied. No complexity violations.

## Outcome

- ✅ Impact: Complete implementation plan created with research and design phases finished. All technical decisions documented with rationale. Database schema, API contracts, and developer guide ready for task breakdown and implementation.
- 🧪 Tests: Constitution compliance check passed (25/25 principles). All design artifacts validated against specification requirements. No gate failures.
- 📁 Files: 9 files created - plan.md (main plan), research.md (technology decisions), data-model.md (database schema), 5 API contracts (OpenAPI 3.0), quickstart.md (developer guide). Total: 1,925 lines of planning documentation.
- 🔁 Next prompts: Ready for /sp.tasks to generate task breakdown (tasks.md), then /sp.implement to execute implementation.
- 🧠 Reflection: Planning phase followed Spec-Driven Development workflow successfully. Research phase resolved all technical unknowns without requiring additional clarifications. Email service decision (configurable SMTP) provides maximum flexibility for development and production. Database schema design includes all security features (account lockout, audit logging, email verification). API contracts follow RESTful conventions and constitution principles. Constitution re-check after design confirmed no new violations introduced.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell script for agent context update failed (template file not found), but this is non-blocking - agent context can be updated manually if needed. All critical planning artifacts were created successfully.
- Graders run and results (PASS/FAIL): Constitution compliance check - PASS (25/25 principles satisfied). Data model validation - PASS (UUID PKs, indexes, timestamps present). API contract validation - PASS (RESTful, proper status codes, JSON responses). Security review - PASS (bcrypt hashing, JWT expiration, account lockout, audit logging).
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided structure outline. User input was truncated but contained sufficient context to understand planning requirements.
- Next experiment (smallest change to try): Consider adding refresh token rotation mechanism to Better Auth configuration. This would enhance security by preventing token replay attacks. Could be added as an optional enhancement without affecting core authentication flow. Would require updating login contract to include refresh_token in response and adding a refresh endpoint.
