# CLAUDE.md Authoring

## Purpose
Guide Claude Code with project-specific rules, conventions, and workflows through effective CLAUDE.md documentation.

## Steps
1. Write clear project overview and context
2. Define folder-level guidelines for different parts of the codebase
3. Explain spec referencing rules and Spec-Driven Development workflow
4. Document coding standards and conventions

## Output
Effective CLAUDE.md documentation that enables Claude to work autonomously within project constraints

## Implementation Details

### What is CLAUDE.md?

CLAUDE.md is a special markdown file that provides project-specific instructions to Claude Code. It acts as a "constitution" for how Claude should interact with your codebase, defining:
- Project structure and organization
- Development workflows and processes
- Coding standards and conventions
- Testing requirements
- Security guidelines
- Spec-Driven Development practices

### CLAUDE.md Hierarchy

#### Root CLAUDE.md
- Located at project root
- Provides global project context
- Defines overall architecture and structure
- Sets project-wide conventions
- Explains Spec-Kit integration

#### Folder-Level CLAUDE.md
- Located in specific directories (frontend/, backend/, etc.)
- Provides context-specific guidelines
- Overrides or extends root CLAUDE.md
- Focuses on local concerns and patterns

```
project-root/
├── CLAUDE.md                    # Global project rules
├── frontend/
│   └── CLAUDE.md                # Frontend-specific rules
├── backend/
│   └── CLAUDE.md                # Backend-specific rules
└── specs/
    └── CLAUDE.md                # Spec authoring rules
```

### Root CLAUDE.md Structure

```markdown
# Claude Code Rules

## Project Overview
[Brief description of the project, its purpose, and tech stack]

## Project Structure
[Explain the monorepo layout and key directories]

## Development Workflow
[Describe the Spec-Driven Development process]

## Core Principles
[List fundamental principles from constitution.md]

## Coding Standards
[Language-specific conventions and best practices]

## Testing Requirements
[Testing strategy and coverage expectations]

## Security Guidelines
[Security practices and requirements]

## Spec-Kit Integration
[How to use specs, plans, tasks, PHRs, and ADRs]

## Common Tasks
[Frequently performed operations and their workflows]
```

### Writing Effective Instructions

#### Be Specific and Actionable
❌ **Bad**: "Write good code"
✅ **Good**: "Use TypeScript strict mode, add type annotations to all function parameters and return values"

❌ **Bad**: "Follow best practices"
✅ **Good**: "Validate all user input at API boundaries using Pydantic models, sanitize data before database operations"

#### Use Clear Structure
```markdown
## Task: Creating a New API Endpoint

### Steps:
1. Define the Pydantic schema in `backend/app/schemas/`
2. Create the SQLModel in `backend/app/models/`
3. Implement the route in `backend/app/api/v1/`
4. Add JWT authentication using `get_current_user` dependency
5. Write unit tests in `backend/tests/`
6. Update API documentation

### Requirements:
- All endpoints must validate JWT tokens
- Use proper HTTP status codes (200, 201, 400, 401, 404, 500)
- Include error handling with descriptive messages
- Add OpenAPI documentation with examples
```

#### Provide Context
```markdown
## Authentication Flow

This project uses Better Auth for frontend authentication and JWT tokens for API authorization.

**Frontend**: Better Auth handles login/signup and stores tokens in httpOnly cookies
**Backend**: FastAPI validates JWT tokens and extracts user identity

When creating authenticated endpoints:
1. Import `get_current_user` from `app.api.deps`
2. Add as dependency: `current_user: User = Depends(get_current_user)`
3. Use `current_user.id` to filter user-specific data
4. Never trust user_id from request body - always use token identity
```

### Spec-Driven Development Integration

#### Referencing Specs
```markdown
## Spec Referencing Rules

### When to Reference Specs:
- Before implementing any feature
- When clarifying requirements
- When making architectural decisions
- When writing tests

### How to Reference:
- Specs are located in `specs/<feature-name>/`
- Always read `spec.md` first for requirements
- Check `plan.md` for architectural decisions
- Follow `tasks.md` for implementation order

### Example:
"Before implementing the todo creation endpoint, read:
- `specs/todo-crud/spec.md` for requirements
- `specs/todo-crud/plan.md` for API contract
- `specs/todo-crud/tasks.md` for implementation steps"
```

#### PHR (Prompt History Record) Policy
```markdown
## Prompt History Records (PHR)

### When to Create PHRs:
- After implementing features
- After significant debugging sessions
- After architectural discussions
- After planning sessions

### PHR Creation Process:
1. Detect the stage (spec, plan, tasks, implementation, etc.)
2. Generate a descriptive title (3-7 words)
3. Use the PHR template from `.specify/templates/phr-template.prompt.md`
4. Fill all placeholders with actual data
5. Save to appropriate directory:
   - Constitution: `history/prompts/constitution/`
   - Feature work: `history/prompts/<feature-name>/`
   - General: `history/prompts/general/`

### PHR Naming Convention:
`<ID>-<slug>.<stage>.prompt.md`

Example: `1-create-todo-api.implementation.prompt.md`
```

#### ADR (Architecture Decision Record) Policy
```markdown
## Architecture Decision Records (ADR)

### When to Suggest ADRs:
Suggest creating an ADR when a decision meets ALL criteria:
- **Impact**: Long-term consequences (framework, data model, API design)
- **Alternatives**: Multiple viable options were considered
- **Scope**: Cross-cutting and influences system design

### ADR Suggestion Format:
"📋 Architectural decision detected: [brief description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`"

### Examples of ADR-worthy Decisions:
- Choosing Next.js App Router over Pages Router
- Selecting PostgreSQL over MongoDB
- Using JWT tokens vs session-based auth
- Implementing monorepo vs separate repositories

### Not ADR-worthy:
- Naming a variable or function
- Choosing a UI component library
- Formatting preferences
```

### Folder-Level Guidelines

#### Frontend CLAUDE.md Example
```markdown
# Frontend Development Rules

## Technology Stack
- Next.js 14 with App Router
- TypeScript with strict mode
- Tailwind CSS for styling
- Better Auth for authentication
- SWR for data fetching

## Component Structure
- Use 'use client' directive only when necessary
- Prefer server components by default
- Keep components small and focused
- Extract reusable logic into custom hooks

## File Organization
- Components: `src/components/`
- Pages: `src/app/`
- Utilities: `src/lib/`
- Types: `src/types/`
- Hooks: `src/hooks/`

## Styling Guidelines
- Use Tailwind utility classes
- Follow mobile-first approach
- Maintain consistent spacing (4, 8, 16, 24, 32px)
- Use design tokens from `tailwind.config.js`

## API Integration
- All API calls go through `src/lib/api/client.ts`
- Include JWT token in Authorization header
- Handle errors with user-friendly messages
- Use SWR for data fetching and caching

## Testing
- Write tests for all components with business logic
- Use React Testing Library
- Test user interactions, not implementation details
- Maintain >80% coverage
```

#### Backend CLAUDE.md Example
```markdown
# Backend Development Rules

## Technology Stack
- FastAPI with Python 3.10+
- SQLModel for ORM
- PostgreSQL database
- Alembic for migrations
- JWT for authentication

## Project Structure
- Models: `app/models/`
- Schemas: `app/schemas/`
- Routes: `app/api/v1/`
- Core logic: `app/core/`
- Tests: `tests/`

## API Design
- Use RESTful conventions
- Version APIs: `/api/v1/`
- Return proper HTTP status codes
- Include descriptive error messages
- Document with OpenAPI/Swagger

## Authentication
- All protected endpoints use `get_current_user` dependency
- Validate JWT tokens on every request
- Extract user_id from token, never trust request body
- Return 401 for invalid/expired tokens

## Database
- Use SQLModel for all models
- Define relationships with `Relationship()`
- Add indexes on foreign keys
- Use UUID for primary keys
- Include created_at and updated_at timestamps

## Error Handling
- Use HTTPException for API errors
- Provide clear error messages
- Log errors with context
- Never expose sensitive information in errors

## Testing
- Write tests for all endpoints
- Use pytest with fixtures
- Test authentication and authorization
- Test error cases
- Maintain >80% coverage
```

### Common Patterns

#### Task Execution Pattern
```markdown
## Executing Tasks from tasks.md

When implementing features:

1. **Read the task**: Get full context from `specs/<feature>/tasks.md`
2. **Check dependencies**: Ensure prerequisite tasks are complete
3. **Implement**: Follow acceptance criteria exactly
4. **Test**: Run all test cases listed in the task
5. **Verify**: Confirm all acceptance criteria are met
6. **Update**: Mark task as complete

Example:
```
Task: Create POST /api/v1/tasks endpoint

Acceptance Criteria:
- [ ] Endpoint accepts title and description
- [ ] Validates JWT token
- [ ] Associates task with authenticated user
- [ ] Returns 201 with created task
- [ ] Returns 401 if not authenticated
```
```

#### Code Review Pattern
```markdown
## Code Review Checklist

Before considering code complete:

### Functionality
- [ ] Meets all acceptance criteria
- [ ] Handles edge cases
- [ ] Includes error handling

### Code Quality
- [ ] Follows project conventions
- [ ] No code duplication
- [ ] Clear variable/function names
- [ ] Appropriate comments for complex logic

### Testing
- [ ] Unit tests written and passing
- [ ] Integration tests if applicable
- [ ] Edge cases tested
- [ ] Error paths tested

### Security
- [ ] Input validation implemented
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Secrets not hardcoded

### Documentation
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] Complex logic documented
```

### Best Practices

#### Do's
✅ **Be explicit about workflows**: "When creating a new feature, first read specs/<feature>/spec.md"
✅ **Provide examples**: Show concrete examples of desired patterns
✅ **Define success criteria**: "Tests must pass, coverage >80%, no linting errors"
✅ **Reference specific files**: "Import from `app/core/security.py`"
✅ **Explain the why**: "Use UUID for primary keys to support distributed systems"
✅ **Set boundaries**: "Never commit .env files, always use .env.example"

#### Don'ts
❌ **Vague instructions**: "Write clean code"
❌ **Assume knowledge**: Don't assume Claude knows your project structure
❌ **Conflicting rules**: Ensure consistency across CLAUDE.md files
❌ **Over-specify**: Don't micromanage every detail
❌ **Outdated info**: Keep CLAUDE.md synchronized with actual codebase

### Template Structure

```markdown
# Claude Code Rules

## Project Identity
**Name**: [Project Name]
**Purpose**: [Brief description]
**Tech Stack**: [Technologies used]

## Project Structure
```
[Directory tree or description]
```

## Development Workflow
### Spec-Driven Development
1. [Step 1]
2. [Step 2]

### Feature Implementation
1. [Step 1]
2. [Step 2]

## Core Principles
[From constitution.md]

## Coding Standards
### [Language 1]
- [Standard 1]
- [Standard 2]

### [Language 2]
- [Standard 1]
- [Standard 2]

## Testing Requirements
- [Requirement 1]
- [Requirement 2]

## Security Guidelines
- [Guideline 1]
- [Guideline 2]

## Spec-Kit Integration
### PHR Policy
[When and how to create PHRs]

### ADR Policy
[When and how to suggest ADRs]

### Spec Referencing
[How to reference and use specs]

## Common Tasks
### [Task 1]
[Instructions]

### [Task 2]
[Instructions]

## File Organization
[Explain where different types of files go]

## Dependencies
[How to manage dependencies]

## Environment Setup
[Configuration and environment variables]

## Deployment
[Deployment process and considerations]
```

### Maintenance

#### Keep It Updated
- Review CLAUDE.md when project structure changes
- Update when new conventions are adopted
- Remove outdated instructions
- Add new patterns as they emerge

#### Test Effectiveness
- Observe if Claude follows instructions correctly
- Refine unclear instructions
- Add examples where confusion occurs
- Get feedback from team members

#### Version Control
- Commit CLAUDE.md changes with descriptive messages
- Review CLAUDE.md changes in PRs
- Document why instructions were added/changed

### Integration with Constitution

```markdown
## Relationship with Constitution

The project constitution (`.specify/memory/constitution.md`) defines core principles.
CLAUDE.md translates those principles into actionable instructions.

**Constitution**: "Write clean, maintainable code"
**CLAUDE.md**: "Use TypeScript strict mode, add type annotations to all functions,
extract complex logic into separate functions with descriptive names"

**Constitution**: "Implement proper authentication"
**CLAUDE.md**: "All protected endpoints must use `get_current_user` dependency,
validate JWT tokens, extract user_id from token payload, return 401 for invalid tokens"
```

### Examples

#### Minimal CLAUDE.md
```markdown
# Claude Code Rules

## Project
Todo app with Next.js frontend and FastAPI backend.

## Structure
- `frontend/` - Next.js app
- `backend/` - FastAPI app
- `specs/` - Feature specifications

## Workflow
1. Read spec from `specs/<feature>/spec.md`
2. Implement following `specs/<feature>/tasks.md`
3. Write tests for all features
4. Create PHR after implementation

## Standards
- TypeScript strict mode
- Python type hints
- JWT authentication required
- Test coverage >80%
```

#### Comprehensive CLAUDE.md
[See the actual CLAUDE.md in this project as a reference]

## Validation Checklist
- [ ] Project overview clearly stated
- [ ] Directory structure explained
- [ ] Development workflow documented
- [ ] Coding standards defined
- [ ] Testing requirements specified
- [ ] Security guidelines included
- [ ] Spec-Kit integration explained
- [ ] PHR policy documented
- [ ] ADR policy documented
- [ ] Common tasks with examples
- [ ] Folder-level guidelines if needed
- [ ] Instructions are specific and actionable
- [ ] Examples provided for complex patterns
- [ ] No conflicting instructions
- [ ] Synchronized with actual codebase
