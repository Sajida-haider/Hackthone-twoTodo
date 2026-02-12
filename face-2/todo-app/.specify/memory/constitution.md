<!--
Sync Impact Report:
- Version: NEW → 1.0.0 (Initial constitution for Phase II)
- Rationale: First formal constitution for Hackathon Todo App Phase II
- Modified Principles: N/A (new constitution)
- Added Sections: All sections are new
- Removed Sections: N/A
- Templates Status:
  ✅ spec-template.md - Reviewed, compatible with Spec-First Development principle
  ✅ plan-template.md - Reviewed, Constitution Check section aligns with principles
  ✅ tasks-template.md - Reviewed, user story organization aligns with Phase Awareness
- Follow-up TODOs: None
- Date: 2026-02-08
-->

# Hackathon Todo App Constitution

## Project Identity

**Project Name**: Hackathon Todo App
**Current Phase**: Phase II – Full-Stack Web Application
**Objective**: Transform a console-based Todo application into a modern, secure, multi-user full-stack web application with persistent storage and authentication.

**Technology Stack**:
- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS, Better Auth (JWT enabled)
- **Backend**: Python FastAPI, SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Development Methodology**: Spec-Driven Development, Spec-Kit Plus, Claude Code

## Core Principles

### I. Spec-First Development

**Rule**: No code may be written without an approved specification.

All implementations MUST reference specifications under `/specs`. Every feature, API endpoint, database change, or UI component must have a corresponding spec document that has been reviewed and approved before implementation begins.

**Rationale**: Spec-first development ensures alignment between requirements and implementation, reduces rework, and provides clear documentation for all stakeholders. It prevents scope creep and ensures that all team members understand what is being built before resources are committed.

### II. Phase Awareness

**Rule**: Only Phase II scope is allowed. Chatbot or AI features are explicitly out of scope.

All work must remain within the boundaries of Phase II: building a full-stack web application with authentication, task management, and persistent storage. Any features beyond this scope must be rejected.

**Rationale**: Phase boundaries prevent scope creep and ensure focused delivery. By explicitly excluding AI/chatbot features, we maintain clarity about what this phase delivers and avoid premature optimization or feature bloat.

### III. Separation of Concerns

**Rule**: Frontend, backend, database, and specs must remain clearly separated. No cross-layer violations are allowed.

- Frontend code lives in `/frontend`
- Backend code lives in `/backend`
- Specifications live in `/specs`
- Database schemas are defined in specs and implemented via SQLModel
- No business logic in the frontend
- No UI rendering in the backend

**Rationale**: Clear separation enables independent development, testing, and deployment of each layer. It improves maintainability, allows for technology changes in one layer without affecting others, and enables parallel development by multiple team members.

## Authentication & Security

### IV. Authentication Flow

**Rule**: User authentication MUST be handled via Better Auth on the frontend. JWT tokens MUST be issued on login.

Better Auth manages the authentication flow, including login, signup, and token issuance. All authenticated requests must include a valid JWT token in the Authorization header.

**Rationale**: Better Auth provides a secure, battle-tested authentication solution that handles common security concerns (password hashing, token management, session handling) correctly by default.

### V. Authorization Enforcement

**Rule**: Every backend API request MUST require a valid JWT token. Requests without a token MUST return 401 Unauthorized.

No backend endpoint (except public endpoints like login/signup) may be accessed without a valid JWT token. Token validation must occur before any business logic executes.

**Rationale**: Consistent authorization enforcement prevents unauthorized access and ensures that all protected resources require authentication. This is a fundamental security requirement for multi-user applications.

### VI. User Isolation

**Rule**: Each user may only access their own tasks. Backend MUST extract user identity from JWT, not from frontend input. All database queries MUST be filtered by authenticated user_id.

User identity comes exclusively from the validated JWT token payload. Any user_id provided in request bodies or query parameters must be ignored. All database queries must include a WHERE clause filtering by the authenticated user's ID.

**Rationale**: User isolation is critical for data security and privacy. Trusting user_id from client input would allow users to access or modify other users' data. Extracting identity from the validated JWT ensures that users can only access their own resources.

### VII. Shared Secret Management

**Rule**: JWT signing and verification MUST use the same secret key. The secret MUST be provided via environment variable: BETTER_AUTH_SECRET.

Both frontend (Better Auth) and backend (FastAPI) must use the same secret key for JWT operations. This secret must never be hardcoded and must be loaded from the environment.

**Rationale**: Shared secret ensures that tokens issued by the frontend can be validated by the backend. Environment variable usage prevents accidental secret exposure in version control and allows different secrets for different environments.

## API Design

### VIII. RESTful API Standards

**Rule**: All API routes MUST be prefixed with `/api/`, MUST be RESTful, and MUST return JSON responses.

API endpoints must follow REST conventions:
- GET for retrieval
- POST for creation
- PUT/PATCH for updates
- DELETE for deletion
- Proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)

**Supported Operations**:
- Create task (POST /api/tasks)
- List tasks (GET /api/tasks)
- Get task by ID (GET /api/tasks/{id})
- Update task (PUT/PATCH /api/tasks/{id})
- Delete task (DELETE /api/tasks/{id})
- Toggle task completion (PATCH /api/tasks/{id}/toggle)

**Rationale**: RESTful design provides a consistent, predictable API structure that is easy to understand and use. JSON responses ensure compatibility with modern frontend frameworks and tools.

### IX. Task Ownership Enforcement

**Rule**: Task ownership MUST be enforced on every operation. Invalid access MUST return proper HTTP errors (401 / 403 / 404).

Every task operation must verify that the authenticated user owns the task being accessed. Return 401 for missing/invalid tokens, 403 for valid tokens accessing unauthorized resources, and 404 when a task doesn't exist or doesn't belong to the user.

**Rationale**: Ownership enforcement at the API layer provides defense in depth. Even if frontend validation is bypassed, the backend ensures users cannot access others' data.

## Database Management

### X. Database Technology

**Rule**: MUST use Neon Serverless PostgreSQL. Connection string MUST come from DATABASE_URL environment variable.

All database connections must use the Neon PostgreSQL connection string provided via the DATABASE_URL environment variable. No other database systems are permitted in Phase II.

**Rationale**: Neon provides serverless PostgreSQL with automatic scaling, branching, and modern developer experience. Standardizing on one database simplifies development and deployment.

### XI. ORM Requirements

**Rule**: SQLModel MUST be used for all database interactions. Raw SQL queries are NOT allowed.

All database operations must use SQLModel's ORM interface. Direct SQL queries (via execute, raw SQL strings, etc.) are prohibited except for migrations.

**Rationale**: SQLModel provides type safety, prevents SQL injection, and ensures consistent database access patterns. It also generates proper SQL for PostgreSQL and handles connection pooling correctly.

### XII. Schema Compliance

**Rule**: Database schema MUST match `/specs/database/schema.md` exactly.

The implemented database schema must precisely match the specification. Any deviations require updating the spec first, then implementing the change.

**Key Requirements**:
- Tasks MUST be associated with users via user_id foreign key
- All tables MUST include created_at and updated_at timestamps
- Primary keys MUST use UUID
- Foreign keys MUST have proper indexes

**Rationale**: Schema compliance ensures that the database structure matches documented requirements and prevents drift between specification and implementation.

## Frontend Architecture

### XIII. Next.js App Router

**Rule**: Use Next.js App Router. Prefer Server Components by default. Client Components only where interactivity is required.

All new pages and layouts must use the App Router structure (`app/` directory). Components should be Server Components unless they require client-side interactivity (event handlers, hooks, browser APIs).

**Rationale**: App Router provides better performance through server-side rendering, automatic code splitting, and improved data fetching patterns. Server Components reduce JavaScript bundle size and improve initial page load.

### XIV. API Client Centralization

**Rule**: All backend calls MUST go through a centralized API client. JWT token MUST be attached to every request.

Create a single API client module that handles all backend communication. This client must automatically attach the JWT token to every request and handle common error scenarios (401, 403, network errors).

**Rationale**: Centralized API access ensures consistent error handling, token management, and request/response formatting. It prevents token handling bugs and makes it easy to add logging, retry logic, or other cross-cutting concerns.

### XV. Responsive Design

**Rule**: Responsive design is mandatory. Styling MUST use Tailwind CSS only.

All UI components must work correctly on mobile, tablet, and desktop screen sizes. Use Tailwind CSS utility classes for all styling. No custom CSS files or inline styles except where absolutely necessary.

**Rationale**: Responsive design ensures accessibility across devices. Tailwind CSS provides a consistent design system, reduces CSS bundle size, and improves development velocity through utility-first approach.

## Spec-Kit Integration

### XVI. Specification Organization

**Rule**: Specifications MUST be organized in `/specs` with the following structure:
- `/specs/features` → What to build (user stories, requirements)
- `/specs/api` → How APIs behave (contracts, endpoints)
- `/specs/database` → Data models (schema, relationships)
- `/specs/ui` → UI components and pages (wireframes, behavior)

Each feature must have its own directory under `/specs/features/<feature-name>/` containing:
- `spec.md` - Requirements specification
- `plan.md` - Architecture and design
- `tasks.md` - Implementation tasks
- `quickstart.md` - Getting started guide
- `research.md` - Research notes

**Rationale**: Organized specifications make it easy to find relevant documentation, ensure completeness, and maintain traceability between requirements and implementation.

### XVII. Spec Referencing

**Rule**: Always reference specs using `@specs/path/to/file.md` notation.

When discussing or implementing features, reference the relevant spec document using the `@specs/` prefix. Example: `@specs/features/task-crud/spec.md`

**Rationale**: Consistent referencing creates clear traceability between code and specifications, making it easy to understand why code exists and what requirements it fulfills.

### XVIII. Spec Updates

**Rule**: If requirements change, specs MUST be updated before code changes.

Never implement requirement changes without first updating the specification. The spec is the source of truth for what should be built.

**Rationale**: Keeping specs synchronized with implementation prevents documentation drift and ensures that specifications remain useful throughout the project lifecycle.

## Agentic Development

### XIX. Agent-Based Workflow

**Rule**: Work MUST be executed via defined specialized agents.

The following agents are available for specific tasks:
- **Spec Architect Agent** - Creating and updating specifications
- **Backend API Agent** - Implementing FastAPI endpoints with JWT auth
- **Frontend Agent** - Building Next.js components and pages
- **Security & Auth Agent** - Implementing JWT validation and user isolation
- **Database & ORM Agent** - Designing schemas and SQLModel models
- **Monorepo Structure Agent** - Organizing project structure

Each agent has specific expertise and should be used for tasks within their domain.

**Rationale**: Specialized agents ensure that domain-specific best practices are followed and that implementations are consistent across the codebase.

## Development Workflow

### XX. Implementation Process

**Rule**: Follow the Spec-Driven Development workflow for all features.

1. **Specify** - Create or update feature specification (`/sp.specify`)
2. **Plan** - Design architecture and implementation approach (`/sp.plan`)
3. **Task Breakdown** - Create detailed implementation tasks (`/sp.tasks`)
4. **Implement** - Execute tasks following the plan (`/sp.implement`)
5. **Review** - Verify implementation matches specification
6. **Document** - Create PHRs and ADRs as needed

**Rationale**: A consistent workflow ensures quality, reduces rework, and maintains clear documentation of decisions and implementations.

### XXI. Prompt History Records (PHR)

**Rule**: Create PHRs for significant work sessions.

PHRs must be created for:
- Feature implementations
- Architectural decisions
- Debugging sessions
- Specification creation
- Planning sessions

PHRs are stored in `history/prompts/` organized by feature or category.

**Rationale**: PHRs provide a historical record of development decisions, making it easier to understand why certain choices were made and enabling knowledge transfer.

### XXII. Architecture Decision Records (ADR)

**Rule**: Document architecturally significant decisions in ADRs.

Create ADRs when decisions meet ALL criteria:
- **Impact**: Long-term consequences (framework choice, data model, API design)
- **Alternatives**: Multiple viable options were considered
- **Scope**: Cross-cutting and influences system design

ADRs are stored in `history/adr/` and must include context, decision, consequences, and alternatives considered.

**Rationale**: ADRs capture the reasoning behind important architectural choices, preventing future developers from questioning or reversing decisions without understanding the original context.

## Quality Standards

### XXIII. Testing Requirements

**Rule**: All business logic MUST have automated tests.

- Backend: pytest for unit and integration tests
- Frontend: React Testing Library for component tests
- API: Contract tests for all endpoints
- Minimum 80% code coverage for business logic

**Rationale**: Automated tests prevent regressions, document expected behavior, and enable confident refactoring.

### XXIV. Code Review

**Rule**: All code changes MUST be reviewed before merging.

No code may be merged to main branch without review. Reviews must verify:
- Specification compliance
- Test coverage
- Security considerations
- Code quality and maintainability

**Rationale**: Code review catches bugs, ensures consistency, and facilitates knowledge sharing across the team.

### XXV. Security Practices

**Rule**: Follow security best practices for all code.

- Never commit secrets or credentials
- Validate all user input
- Use parameterized queries (via SQLModel)
- Implement proper error handling without exposing sensitive information
- Follow OWASP Top 10 guidelines
- Use HTTPS for all production traffic

**Rationale**: Security must be built in from the start. Following established security practices prevents common vulnerabilities and protects user data.

## Governance

### Amendment Process

This constitution may be amended when:
1. New requirements emerge that conflict with existing principles
2. Technology choices change (e.g., moving to a different framework)
3. Security vulnerabilities require policy updates
4. Team retrospectives identify process improvements

**Amendment Procedure**:
1. Propose amendment with rationale
2. Review impact on existing code and specifications
3. Update constitution with version bump
4. Update dependent templates and documentation
5. Communicate changes to all team members

### Version Policy

Constitution versions follow semantic versioning:
- **MAJOR**: Backward incompatible changes (principle removal, fundamental policy changes)
- **MINOR**: New principles or sections added
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance

All pull requests and code reviews must verify compliance with this constitution. Any violations must be justified and documented. Complexity that violates principles must be explicitly justified in the implementation plan.

### Living Document

This constitution is a living document that evolves with the project. Regular reviews (at phase boundaries or quarterly) ensure it remains relevant and useful.

---

**Version**: 1.0.0 | **Ratified**: 2026-02-08 | **Last Amended**: 2026-02-08
