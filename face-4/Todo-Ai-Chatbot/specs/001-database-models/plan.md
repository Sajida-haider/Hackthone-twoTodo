# Implementation Plan: Database & Models

**Branch**: `001-database-models` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-database-models/spec.md`

## Summary

This plan implements the database persistence layer for Phase III AI Chatbot, defining three core models (Task, Conversation, Message) using SQLModel ORM with Neon PostgreSQL. The implementation ensures stateless API operation with all conversation context and task data persisted in the database, supporting user isolation, data integrity, and efficient retrieval for context-aware chatbot responses.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: SQLModel 0.0.14+, psycopg2-binary 2.9+, alembic 1.13+ (migrations)
**Storage**: Neon Serverless PostgreSQL (via DATABASE_URL environment variable)
**Testing**: pytest 7.4+, pytest-asyncio 0.21+
**Target Platform**: Linux server (FastAPI backend)
**Project Type**: Web application (backend component)
**Performance Goals**:
- Data retrieval < 200ms for 95% of requests
- Support 10,000+ tasks per user
- Support 1,000+ conversations per user
- Conversation history retrieval < 500ms for 100 messages
**Constraints**:
- 100% user isolation enforcement
- 100% data integrity (no data loss)
- UTC timezone for all timestamps
- Cascade deletion for conversation → messages
**Scale/Scope**: Multi-user system with isolated data per user, supporting concurrent access

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance

✅ **I. Spec-First Development**: Implementation follows approved spec.md
✅ **II. Phase Awareness**: Within Phase III scope (AI Chatbot database layer)
✅ **III. Separation of Concerns**: Database models isolated in backend/app/models/
✅ **VI. User Isolation**: All models include user_id filtering
✅ **X. Database Technology**: Using Neon Serverless PostgreSQL
✅ **XI. ORM Requirements**: Using SQLModel exclusively (no raw SQL)
✅ **XII. Schema Compliance**: Models match spec.md entity definitions exactly

### Constitution-Mandated Requirements

From **Principle XII (Schema Compliance)**:
- ✅ Tasks associated with users via user_id foreign key
- ✅ Conversations associated with users via user_id foreign key
- ✅ Messages associated with conversations via conversation_id foreign key
- ✅ All tables include created_at and updated_at timestamps
- ✅ Primary keys use integer IDs (auto-increment)
- ✅ Foreign keys will have proper indexes

From **Principle VI (User Isolation)**:
- ✅ All database queries filtered by authenticated user_id
- ✅ User identity from JWT token, not client input

From **Principle XI (ORM Requirements)**:
- ✅ All database operations use SQLModel ORM
- ✅ No raw SQL queries (except migrations)

**Gate Status**: ✅ PASSED - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-database-models/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── database-schema.yaml
└── checklists/
    └── requirements.md  # Already created
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task model
│   │   ├── conversation.py  # Conversation model
│   │   └── message.py       # Message model
│   ├── database.py          # Database connection and session management
│   └── core/
│       └── config.py        # Configuration (DATABASE_URL)
├── alembic/
│   ├── versions/            # Migration scripts
│   └── env.py
├── alembic.ini
└── tests/
    ├── unit/
    │   └── test_models.py   # Model validation tests
    └── integration/
        └── test_database.py # Database integration tests
```

**Structure Decision**: Using web application structure (Option 2) with backend-only components. Models are organized in `backend/app/models/` following FastAPI conventions. Database connection logic in `backend/app/database.py`. Alembic for migrations at backend root level.

## Complexity Tracking

No constitutional violations. All requirements align with established principles.

---

## Phase 0: Research & Technology Validation

### Research Tasks

**R1: SQLModel Best Practices for Multi-User Systems**
- Research: User isolation patterns in SQLModel
- Research: Automatic timestamp handling (created_at, updated_at)
- Research: Foreign key relationships and cascade deletion
- Research: Index optimization for user_id filtering
- **Output**: Best practices for model design

**R2: Neon PostgreSQL Connection Patterns**
- Research: Connection pooling with Neon Serverless
- Research: Environment variable configuration (DATABASE_URL)
- Research: Connection retry and error handling
- Research: Transaction management for data integrity
- **Output**: Connection strategy and configuration

**R3: Alembic Migration Strategy**
- Research: Alembic setup with SQLModel
- Research: Auto-generation of migrations from models
- Research: Migration rollback strategies
- Research: Data migration for existing users (if applicable)
- **Output**: Migration workflow and tooling

**R4: Testing Strategy for Database Models**
- Research: pytest fixtures for database testing
- Research: Test database setup/teardown
- Research: Mocking vs real database for tests
- Research: Testing cascade deletion and constraints
- **Output**: Testing approach and tools

### Research Findings

See [research.md](./research.md) for detailed findings.

**Key Decisions**:
- SQLModel with automatic timestamps via `datetime.utcnow`
- Connection pooling with psycopg2 driver
- Alembic for schema migrations with auto-generation
- pytest with separate test database (SQLite for speed)

---

## Phase 1: Design & Contracts

### Data Model Design

See [data-model.md](./data-model.md) for complete entity definitions.

**Entity Summary**:
- **Task**: User's todo items with completion tracking
- **Conversation**: Chat sessions with AI assistant
- **Message**: Individual messages within conversations

**Relationships**:
- User → Tasks (one-to-many)
- User → Conversations (one-to-many)
- Conversation → Messages (one-to-many, cascade delete)
- User → Messages (one-to-many)

### Database Schema Contract

See [contracts/database-schema.yaml](./contracts/database-schema.yaml) for OpenAPI-style schema definitions.

### Quickstart Guide

See [quickstart.md](./quickstart.md) for setup and usage instructions.

---

## Phase 2: Implementation Planning Complete

**Status**: Planning phase complete. Ready for task breakdown.

**Next Command**: `/sp.tasks` to generate implementation tasks

**Artifacts Created**:
- ✅ plan.md (this file)
- ✅ research.md (Phase 0 findings)
- ✅ data-model.md (Phase 1 entity design)
- ✅ contracts/database-schema.yaml (Phase 1 schema contract)
- ✅ quickstart.md (Phase 1 usage guide)

**Constitution Re-Check**: ✅ PASSED - All design decisions comply with constitutional principles

**Ready for**: Task generation and implementation
