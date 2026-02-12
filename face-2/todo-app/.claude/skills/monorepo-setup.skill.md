# Monorepo Setup

## Purpose
Organize the project in a single repository with clear separation of frontend, backend, and specification artifacts following Spec-Kit conventions.

## Steps
1. Create frontend and backend directories with proper structure
2. Configure specs folders for feature documentation
3. Add Spec-Kit configuration and templates
4. Set up shared tooling and documentation

## Output
Clean and scalable monorepo structure with Spec-Driven Development support

## Implementation Details

### Root Directory Structure

```
project-root/
├── .specify/                    # Spec-Kit configuration
│   ├── memory/                  # Project memory and principles
│   │   └── constitution.md      # Project constitution
│   ├── templates/               # Document templates
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── phr-template.prompt.md
│   │   └── adr-template.md
│   └── scripts/                 # Automation scripts
│       ├── bash/
│       └── powershell/
├── specs/                       # Feature specifications
│   └── <feature-name>/
│       ├── spec.md              # Requirements specification
│       ├── plan.md              # Architecture and design
│       ├── tasks.md             # Implementation tasks
│       ├── quickstart.md        # Getting started guide
│       ├── research.md          # Research notes
│       └── checklists/          # Custom checklists
├── history/                     # Project history
│   ├── prompts/                 # Prompt History Records
│   │   ├── constitution/
│   │   ├── <feature-name>/
│   │   └── general/
│   └── adr/                     # Architecture Decision Records
├── frontend/                    # Frontend application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
├── backend/                     # Backend application
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── .claude/                     # Claude Code configuration
│   ├── skills/                  # Custom skills
│   └── commands/                # Custom commands
├── .github/                     # GitHub configuration
│   └── workflows/               # CI/CD workflows
├── docs/                        # General documentation
├── CLAUDE.md                    # Claude Code instructions
├── README.md                    # Project overview
├── .gitignore
└── .env.example
```

### Frontend Directory Structure

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── (auth)/              # Auth route group
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/         # Dashboard route group
│   │   │   └── todos/
│   │   ├── api/                 # API routes
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Home page
│   ├── components/              # React components
│   │   ├── ui/                  # UI primitives
│   │   ├── forms/               # Form components
│   │   └── layouts/             # Layout components
│   ├── lib/                     # Utilities and helpers
│   │   ├── api/                 # API client
│   │   ├── auth/                # Auth utilities
│   │   └── utils.ts             # General utilities
│   ├── hooks/                   # Custom React hooks
│   ├── types/                   # TypeScript types
│   ├── styles/                  # Global styles
│   └── config/                  # Configuration
├── public/                      # Static assets
│   ├── images/
│   └── favicon.ico
├── tests/                       # Frontend tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.local.example           # Environment variables template
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── package.json                 # Dependencies
├── package-lock.json
└── README.md                    # Frontend documentation
```

### Backend Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection
│   ├── dependencies.py          # FastAPI dependencies
│   ├── models/                  # SQLModel models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── deps.py              # Route dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── tasks.py
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py          # JWT and password hashing
│   │   └── config.py            # Core configuration
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/                       # Backend tests
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_tasks.py
├── alembic/                     # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── .env.example                 # Environment variables template
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── pyproject.toml               # Python project configuration
└── README.md                    # Backend documentation
```

### Spec-Kit Configuration

#### .specify/memory/constitution.md
```markdown
# Project Constitution

## Project Identity
- **Name**: Todo Application
- **Purpose**: Full-stack task management system
- **Tech Stack**: Next.js, FastAPI, PostgreSQL, SQLModel

## Core Principles

### Code Quality
- Write clean, maintainable, and testable code
- Follow language-specific best practices
- Use type hints and proper typing
- Document complex logic

### Testing
- Write tests for all business logic
- Maintain high test coverage
- Use TDD when appropriate
- Test edge cases and error paths

### Security
- Never commit secrets or credentials
- Use environment variables for configuration
- Implement proper authentication and authorization
- Validate all user input
- Follow OWASP security guidelines

### Performance
- Optimize database queries
- Use proper indexing
- Implement caching where appropriate
- Monitor and profile performance

### Architecture
- Follow separation of concerns
- Use dependency injection
- Keep components loosely coupled
- Design for scalability

## Development Workflow
1. Specify requirements in spec.md
2. Plan architecture in plan.md
3. Break down into tasks in tasks.md
4. Implement with tests
5. Review and refactor
6. Document decisions in ADRs

## Git Conventions
- Use conventional commits
- Create feature branches
- Write descriptive commit messages
- Review code before merging
```

#### .specify/templates/spec-template.md
```markdown
# [Feature Name]

## Overview
Brief description of the feature and its purpose.

## User Stories
- As a [user type], I want to [action] so that [benefit]

## Requirements

### Functional Requirements
- [ ] Requirement 1
- [ ] Requirement 2

### Non-Functional Requirements
- Performance: [criteria]
- Security: [criteria]
- Usability: [criteria]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Out of Scope
- Item 1
- Item 2

## Dependencies
- Dependency 1
- Dependency 2

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Risk 1 | High | Strategy |
```

#### .specify/templates/plan-template.md
```markdown
# [Feature Name] - Implementation Plan

## Architecture Overview
High-level description of the solution architecture.

## Components

### Frontend
- Component 1: Description
- Component 2: Description

### Backend
- Endpoint 1: Description
- Endpoint 2: Description

### Database
- Table 1: Description
- Table 2: Description

## Data Flow
1. Step 1
2. Step 2

## API Contracts

### Endpoint 1
- **Method**: POST
- **Path**: /api/v1/resource
- **Request**: Schema
- **Response**: Schema

## Security Considerations
- Authentication approach
- Authorization rules
- Data validation

## Performance Considerations
- Caching strategy
- Query optimization
- Scalability approach

## Testing Strategy
- Unit tests
- Integration tests
- E2E tests

## Deployment Plan
1. Step 1
2. Step 2

## Rollback Plan
Steps to rollback if issues occur.
```

#### .specify/templates/tasks-template.md
```markdown
# [Feature Name] - Tasks

## Task List

### 1. [Task Name]
**Description**: What needs to be done

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Test Cases**:
- [ ] Test case 1
- [ ] Test case 2

**Dependencies**: None

**Estimated Effort**: [Small/Medium/Large]

---

### 2. [Next Task]
...
```

### CLAUDE.md Configuration

Create a comprehensive CLAUDE.md file at the root with:
- Project overview and structure
- Development guidelines
- Spec-Driven Development workflow
- PHR and ADR policies
- Code standards and conventions
- Testing requirements
- Security guidelines

### Package Management

#### Root package.json (if using workspaces)
```json
{
  "name": "todo-app-monorepo",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "frontend",
    "backend"
  ],
  "scripts": {
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && uvicorn app.main:app --reload",
    "build:frontend": "cd frontend && npm run build",
    "test:frontend": "cd frontend && npm test",
    "test:backend": "cd backend && pytest",
    "lint": "npm run lint:frontend && npm run lint:backend",
    "format": "prettier --write \"**/*.{js,jsx,ts,tsx,json,md}\""
  }
}
```

### Git Configuration

#### .gitignore
```
# Dependencies
node_modules/
__pycache__/
*.pyc
.Python
env/
venv/
.venv/

# Environment variables
.env
.env.local
.env.*.local

# Build outputs
.next/
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
.pytest_cache/
.coverage

# Logs
*.log
logs/

# Database
*.db
*.sqlite
```

### Documentation Structure

#### Root README.md
```markdown
# Todo Application

Full-stack task management application built with Next.js and FastAPI.

## Project Structure
- `frontend/` - Next.js frontend application
- `backend/` - FastAPI backend application
- `specs/` - Feature specifications
- `history/` - Project history (PHRs and ADRs)
- `.specify/` - Spec-Kit configuration

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+

### Installation
1. Clone the repository
2. Install frontend dependencies: `cd frontend && npm install`
3. Install backend dependencies: `cd backend && pip install -r requirements.txt`
4. Set up environment variables
5. Run migrations: `cd backend && alembic upgrade head`

### Development
- Frontend: `npm run dev:frontend`
- Backend: `npm run dev:backend`

## Documentation
- [Frontend README](./frontend/README.md)
- [Backend README](./backend/README.md)
- [Specifications](./specs/)
- [Architecture Decisions](./history/adr/)

## Contributing
See [CLAUDE.md](./CLAUDE.md) for development guidelines.
```

### Environment Configuration

#### .env.example (root)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
PYTHON_ENV=development
```

### CI/CD Configuration

#### .github/workflows/ci.yml
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm test
      - run: cd frontend && npm run build

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest
```

## Setup Steps

### 1. Initialize Repository
```bash
# Create root directory
mkdir todo-app && cd todo-app
git init

# Create main directories
mkdir -p frontend backend specs history/{prompts,adr} .specify/{memory,templates,scripts/{bash,powershell}} .claude/skills docs
```

### 2. Set Up Spec-Kit
```bash
# Create constitution
touch .specify/memory/constitution.md

# Create templates
touch .specify/templates/{spec,plan,tasks,phr,adr}-template.md

# Create scripts directories
mkdir -p .specify/scripts/{bash,powershell}
```

### 3. Initialize Frontend
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
npm install
```

### 4. Initialize Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn sqlmodel psycopg2-binary alembic python-jose passlib bcrypt
pip freeze > requirements.txt
```

### 5. Create Configuration Files
```bash
# Root
touch CLAUDE.md README.md .gitignore .env.example

# Frontend
cd frontend && touch .env.local.example README.md

# Backend
cd backend && touch .env.example README.md
```

### 6. Initialize Git
```bash
git add .
git commit -m "Initial monorepo setup with Spec-Kit configuration"
```

## Best Practices

### Monorepo Management
- Keep frontend and backend independent
- Share types/interfaces when possible
- Use workspace features for shared dependencies
- Maintain separate CI/CD pipelines
- Version components independently if needed

### Spec-Kit Usage
- Create specs before implementation
- Update specs as requirements change
- Record all significant decisions in ADRs
- Create PHRs for major work sessions
- Keep constitution up to date

### Documentation
- Keep README files current
- Document setup and deployment
- Maintain API documentation
- Update architecture diagrams
- Document breaking changes

### Version Control
- Use feature branches
- Follow conventional commits
- Keep commits atomic and focused
- Write descriptive commit messages
- Review code before merging

## Validation Checklist
- [ ] Directory structure created
- [ ] Spec-Kit configuration in place
- [ ] Frontend initialized with Next.js
- [ ] Backend initialized with FastAPI
- [ ] Environment variables configured
- [ ] Git repository initialized
- [ ] README files created
- [ ] CLAUDE.md configured
- [ ] .gitignore properly set up
- [ ] CI/CD workflows configured
