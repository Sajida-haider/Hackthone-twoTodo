---
id: 1
title: Create Phase II Constitution
stage: constitution
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: KARAKORUM TRADERS
command: /sp.constitution
labels: ["constitution", "phase-ii", "governance", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (documentation only)
---

## Prompt

You are operating under a Spec-Driven Development workflow using Spec-Kit Plus.

This constitution defines the global rules, boundaries, and development principles
for Phase II of the Hackathon Todo Full-Stack Web Application.

========================
PROJECT CONTEXT
========================
Project Name: Hackathon Todo App
Current Phase: Phase II – Full-Stack Web Application
Objective:
Transform a console-based Todo application into a modern, secure, multi-user
full-stack web application with persistent storage and authentication.

========================
TECHNOLOGY STACK
========================
Frontend:
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (JWT enabled)

Backend:
- Python FastAPI
- SQLModel ORM

Database:
- Neon Serverless PostgreSQL

Development Methodology:
- Spec-Driven Development
- Spec-Kit Plus
- Claude Code

========================
CORE PRINCIPLES
========================
1. Spec-First Development
   - No code may be written without an approved specification.
   - All implementations must reference specs under /specs.

2. Phase Awareness
   - Only Phase II scope is allowed.
   - Chatbot or AI features are explicitly out of scope.

3. Separation of Concerns
   - Frontend, backend, database, and specs must remain clearly separated.
   - No cross-layer violations are allowed.

========================
AUTHENTICATION & SECURITY
========================
1. Authentication
   - User authentication must be handled via Better Auth on the frontend.
   - JWT tokens must be issued on login.

2. Authorization
   - Every backend API request must require a valid JWT token.
   - Requests without a token must return 401 Unauthorized.

3. User Isolation
   - Each user may only access their own tasks.
   - Backend must extract user identity from JWT, not from frontend input.
   - All database queries must be filtered by authenticated user_id.

4. Shared Secret
   - JWT signing and verification must use the same secret key.
   - The secret must be provided via environment variable:
     BETTER_AUTH_SECRET

========================
API RULES
========================
1. All API routes must:
   - Be prefixed with /api/
   - Be RESTful
   - Return JSON responses

2. Supported operations:
   - Create task
   - List tasks
   - Get task by ID
   - Update task
   - Delete task
   - Toggle task completion

3. API behavior:
   - Task ownership must be enforced on every operation.
   - Invalid access must return proper HTTP errors (401 / 403 / 404).

========================
DATABASE RULES
========================
1. Database:
   - Must use Neon Serverless PostgreSQL.
   - Connection string must come from DATABASE_URL.

2. ORM:
   - SQLModel must be used for all database interactions.
   - Raw SQL queries are not allowed.

3. Schema:
   - Tasks must be associated with users via user_id.
   - Database schema must match /specs/database/schema.md exactly.

========================
FRONTEND RULES
========================
1. Architecture:
   - Use Next.js App Router.
   - Prefer Server Components by default.
   - Client Components only where interactivity is required.

2. API Access:
   - All backend calls must go through a centralized API client.
   - JWT token must be attached to every request.

3. UI:
   - Responsive design is mandatory.
   - Styling must use Tailwind CSS only.

========================
SPEC-KIT USAGE RULES
========================
1. Specifications Location:
   - /specs/features → What to build
   - /specs/api → How APIs behave
   - /specs/database → Data models
   - /specs/ui → UI components and pages

2. Referencing Specs:
   - Always reference specs using @specs/path/to/file.md
   - Example:
     @specs/features/task-crud.md

3. Updates:
   - If requirements change, specs must be updated before code changes.

========================
AGENTIC DEVELOPMENT RULES
========================
1. Work must be executed via defined agents:
   - Spec Architect Agent
   - Backend API Agent
   - Frontend Agent
   - Security & Auth Agent
   - Database & ORM Agent
   - Structure & Workflow Agent

## Response snapshot

Created comprehensive constitution v1.0.0 for Hackathon Todo App Phase II with 25 core principles organized into 9 major sections:

**Core Principles (I-III)**:
- Spec-First Development (no code without approved specs)
- Phase Awareness (Phase II scope only, no AI/chatbot features)
- Separation of Concerns (clear frontend/backend/database/specs boundaries)

**Authentication & Security (IV-VII)**:
- Better Auth for frontend authentication with JWT tokens
- Authorization enforcement on all backend endpoints (401 for missing tokens)
- User isolation (extract user_id from JWT, never trust client input)
- Shared secret management via BETTER_AUTH_SECRET environment variable

**API Design (VIII-IX)**:
- RESTful API standards with /api/ prefix and JSON responses
- Task ownership enforcement with proper HTTP error codes

**Database Management (X-XII)**:
- Neon Serverless PostgreSQL with DATABASE_URL
- SQLModel ORM for all database interactions (no raw SQL)
- Schema compliance with /specs/database/schema.md

**Frontend Architecture (XIII-XV)**:
- Next.js App Router with Server Components by default
- Centralized API client with automatic JWT token attachment
- Responsive design with Tailwind CSS only

**Spec-Kit Integration (XVI-XVIII)**:
- Organized specification structure in /specs
- Consistent spec referencing with @specs/ notation
- Specs must be updated before code changes

**Agentic Development (XIX)**:
- Specialized agents for different domains (Spec Architect, Backend API, Frontend, Security & Auth, Database & ORM, Monorepo Structure)

**Development Workflow (XX-XXII)**:
- Spec-Driven Development process (Specify → Plan → Task Breakdown → Implement → Review → Document)
- PHR creation for significant work sessions
- ADR documentation for architecturally significant decisions

**Quality Standards (XXIII-XXV)**:
- Testing requirements (80% coverage, pytest, React Testing Library)
- Code review mandatory before merging
- Security best practices (OWASP Top 10, no hardcoded secrets)

**Governance**:
- Amendment process with semantic versioning
- Compliance verification in all PRs
- Living document with regular reviews

All templates reviewed for consistency. No placeholders remaining. Constitution ratified 2026-02-08.

## Outcome

- ✅ Impact: Established formal governance framework for Phase II development with 25 enforceable principles covering security, architecture, workflow, and quality standards
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Created .specify/memory/constitution.md (v1.0.0) with complete principle definitions and rationales
- 🔁 Next prompts: Create feature specifications following Spec-First Development principle, set up monorepo structure per Separation of Concerns principle, implement authentication per principles IV-VII
- 🧠 Reflection: Constitution provides clear, testable rules that prevent common pitfalls (user isolation violations, scope creep, documentation drift). Each principle includes rationale to help developers understand the "why" behind constraints.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution successfully created with all placeholders filled
- Graders run and results (PASS/FAIL): PASS - All 25 principles have clear rules and rationales, templates reviewed for consistency, semantic versioning applied correctly
- Prompt variant (if applicable): N/A (initial constitution creation)
- Next experiment (smallest change to try): Monitor constitution compliance during first feature implementation to identify any ambiguous or conflicting principles that need clarification
