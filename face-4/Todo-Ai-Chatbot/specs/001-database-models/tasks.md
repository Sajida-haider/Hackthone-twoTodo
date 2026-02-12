---
description: "Implementation tasks for Database & Models"
---

# Tasks: Database & Models

**Input**: Design documents from `/specs/001-database-models/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- Models in `backend/app/models/`
- Database config in `backend/app/database.py`
- Tests in `backend/tests/unit/` and `backend/tests/integration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Install SQLModel, psycopg2-binary, and alembic dependencies in backend/requirements.txt
- [ ] T002 [P] Create backend/app/models/__init__.py for model exports
- [ ] T003 [P] Create backend/app/core/config.py for DATABASE_URL configuration using pydantic-settings
- [ ] T004 Create backend/app/database.py with engine creation and session management

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Initialize Alembic in backend/ directory with `alembic init alembic`
- [ ] T006 Configure alembic/env.py to import SQLModel metadata and use DATABASE_URL from environment
- [ ] T007 Create base model class with automatic timestamp handling (created_at, updated_at) in backend/app/models/base.py
- [ ] T008 [P] Set up pytest configuration in backend/pytest.ini with test database settings
- [ ] T009 [P] Create pytest fixtures for test database setup/teardown in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Data Persistence (Priority: P1) 🎯 MVP

**Goal**: Implement Task model with user isolation, automatic timestamps, and persistence

**Independent Test**: Create tasks, close application, reopen, verify tasks persist with correct data

### Implementation for User Story 1

- [ ] T010 [US1] Create Task model in backend/app/models/task.py with fields: id, user_id, title, description, completed, created_at, updated_at
- [ ] T011 [US1] Add indexes to Task model: user_id (single), completed (single), (user_id, completed) composite
- [ ] T012 [US1] Add validation to Task model: title max 500 chars, description max 5000 chars, title not empty
- [ ] T013 [US1] Generate Alembic migration for Task table: `alembic revision --autogenerate -m "Add task table"`
- [ ] T014 [US1] Review and apply migration: verify indexes, constraints, and field types in generated migration
- [ ] T015 [US1] Apply migration to database: `alembic upgrade head`
- [ ] T016 [P] [US1] Write unit tests for Task model in backend/tests/unit/test_task_model.py (creation, validation, timestamps)
- [ ] T017 [P] [US1] Write integration tests for Task persistence in backend/tests/integration/test_task_database.py (CRUD operations, user isolation)
- [ ] T018 [US1] Verify user isolation: test that user A cannot access user B's tasks
- [ ] T019 [US1] Verify automatic timestamps: test created_at is set on creation, updated_at changes on modification

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Conversation History Persistence (Priority: P2)

**Goal**: Implement Conversation model with user isolation and automatic timestamps

**Independent Test**: Create conversation, close application, reopen, verify conversation persists

### Implementation for User Story 2

- [ ] T020 [US2] Create Conversation model in backend/app/models/conversation.py with fields: id, user_id, created_at, updated_at
- [ ] T021 [US2] Add indexes to Conversation model: user_id (single), updated_at (single)
- [ ] T022 [US2] Generate Alembic migration for Conversation table: `alembic revision --autogenerate -m "Add conversation table"`
- [ ] T023 [US2] Review and apply migration: verify indexes and field types
- [ ] T024 [US2] Apply migration to database: `alembic upgrade head`
- [ ] T025 [P] [US2] Write unit tests for Conversation model in backend/tests/unit/test_conversation_model.py
- [ ] T026 [P] [US2] Write integration tests for Conversation persistence in backend/tests/integration/test_conversation_database.py
- [ ] T027 [US2] Verify user isolation: test that user A cannot access user B's conversations
- [ ] T028 [US2] Verify automatic timestamps: test created_at and updated_at behavior

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Message Storage and Retrieval (Priority: P3)

**Goal**: Implement Message model with foreign key to Conversation, cascade deletion, and chronological ordering

**Independent Test**: Send messages in conversation, query messages, verify order and cascade deletion

### Implementation for User Story 3

- [ ] T029 [US3] Create Message model in backend/app/models/message.py with fields: id, user_id, conversation_id, role, content, created_at
- [ ] T030 [US3] Add MessageRole enum with values: "user", "assistant"
- [ ] T031 [US3] Add foreign key relationship: message.conversation_id → conversation.id with CASCADE DELETE
- [ ] T032 [US3] Add indexes to Message model: user_id, conversation_id, created_at, (conversation_id, created_at) composite
- [ ] T033 [US3] Add validation to Message model: role in enum, content max 10000 chars, content not empty
- [ ] T034 [US3] Add bidirectional relationship: Conversation.messages (one-to-many) with cascade="all, delete-orphan"
- [ ] T035 [US3] Generate Alembic migration for Message table: `alembic revision --autogenerate -m "Add message table with foreign key"`
- [ ] T036 [US3] Review migration: verify foreign key constraint, cascade delete, and indexes
- [ ] T037 [US3] Apply migration to database: `alembic upgrade head`
- [ ] T038 [P] [US3] Write unit tests for Message model in backend/tests/unit/test_message_model.py (creation, validation, enum)
- [ ] T039 [P] [US3] Write integration tests for Message persistence in backend/tests/integration/test_message_database.py
- [ ] T040 [US3] Test cascade deletion: verify deleting conversation deletes all messages
- [ ] T041 [US3] Test message ordering: verify messages retrieved in chronological order (created_at ASC)
- [ ] T042 [US3] Test user isolation: verify user A cannot access user B's messages
- [ ] T043 [US3] Test foreign key constraint: verify cannot create message with invalid conversation_id

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T044 [P] Add database connection pooling configuration in backend/app/database.py (pool_size=5, max_overflow=10)
- [ ] T045 [P] Add connection retry logic with exponential backoff in backend/app/database.py
- [ ] T046 [P] Create context manager for database sessions with automatic commit/rollback in backend/app/database.py
- [ ] T047 [P] Add database health check endpoint helper function
- [ ] T048 [P] Document all models with docstrings explaining purpose and relationships
- [ ] T049 [P] Add logging for database operations (connection, queries, errors)
- [ ] T050 [P] Create database initialization script for development setup
- [ ] T051 Run full test suite: `pytest backend/tests/ -v --cov=app/models`
- [ ] T052 Verify all migrations are reversible: test `alembic downgrade -1` for each migration
- [ ] T053 Update quickstart.md with any implementation-specific details discovered during development
- [ ] T054 Create database seeding script for development/testing with sample data

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (Task): Can start after Foundational
  - User Story 2 (Conversation): Can start after Foundational (independent of US1)
  - User Story 3 (Message): Depends on User Story 2 (needs Conversation table)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Task)**: No dependencies on other stories - fully independent
- **User Story 2 (Conversation)**: No dependencies on other stories - fully independent
- **User Story 3 (Message)**: Depends on User Story 2 (Conversation must exist for foreign key)

### Within Each User Story

- Model creation before migration generation
- Migration generation before migration application
- Migration application before tests
- Unit tests can run in parallel with integration tests
- Validation tests after basic CRUD tests

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- User Story 1 and User Story 2 can be developed in parallel (independent)
- User Story 3 must wait for User Story 2 (Conversation) to complete
- All tests within a user story marked [P] can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Task persistence)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Task) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Conversation) → Test independently → Deploy/Demo
4. Add User Story 3 (Message) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Task)
   - Developer B: User Story 2 (Conversation)
3. After US2 completes:
   - Developer C: User Story 3 (Message) - depends on US2
4. Stories complete and integrate independently

---

## Testing Strategy

### Unit Tests (Fast, Isolated)

- Test model creation and validation
- Test field constraints (max length, not null, etc.)
- Test enum values
- Test timestamp behavior
- Use SQLite in-memory database

### Integration Tests (Realistic)

- Test CRUD operations with real PostgreSQL
- Test user isolation queries
- Test cascade deletion
- Test foreign key constraints
- Test index performance
- Use separate test database

### Test Coverage Goals

- Minimum 80% code coverage for models
- 100% coverage for critical paths (user isolation, cascade deletion)
- All edge cases covered (empty strings, null values, invalid foreign keys)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Story 3 (Message) MUST wait for User Story 2 (Conversation) due to foreign key dependency
- All timestamps must be in UTC
- All queries must filter by user_id for user isolation
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
