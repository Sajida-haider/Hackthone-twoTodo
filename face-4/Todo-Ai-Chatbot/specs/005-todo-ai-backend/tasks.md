---
description: "Implementation tasks for Todo AI Chatbot Backend"
---

# Tasks: Todo AI Chatbot Backend

**Input**: Design documents from `/specs/005-todo-ai-backend/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure: backend/src/ with subdirectories (api/, models/, services/, agent/, mcp/, schemas/, config.py, main.py)
- [ ] T002 [P] Create requirements.txt with dependencies: fastapi, uvicorn, sqlmodel, pydantic, python-jose, openai-agents-sdk, mcp-sdk, psycopg2-binary, alembic, pytest
- [ ] T003 [P] Create config.py: Load environment variables (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
- [ ] T004 [P] Create main.py: Initialize FastAPI application with CORS, health endpoint
- [ ] T005 Install dependencies: pip install -r backend/requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create database connection service in backend/src/services/database.py: SQLModel engine, session management, connection pooling
- [ ] T007 [P] Create Conversation model in backend/src/models/conversation.py: SQLModel with id, user_id, created_at, updated_at
- [ ] T008 [P] Create Message model in backend/src/models/message.py: SQLModel with id, conversation_id, role, content, tool_calls (JSONB), created_at
- [ ] T009 [P] Create Task model reference in backend/src/models/task.py: Import existing Task model from Phase III-A
- [ ] T010 Initialize Alembic: alembic init alembic, configure env.py with SQLModel metadata
- [ ] T011 Create migration for Conversation and Message tables: alembic revision --autogenerate -m "Add conversations and messages"
- [ ] T012 Run migration: alembic upgrade head
- [ ] T013 [P] Create Pydantic schemas in backend/src/schemas/chat.py: ChatRequest, ChatResponse, ToolCallSchema
- [ ] T014 [P] Create JWT authentication dependency in backend/src/api/dependencies.py: Validate JWT token, extract user_id
- [ ] T015 [P] Create conversation service in backend/src/services/conversation.py: load_history(), save_message(), create_conversation()

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can add new tasks by sending natural language messages to the AI assistant

**Independent Test**: User sends "Add a task to buy groceries tomorrow" and receives confirmation with task created in database

### MCP Tool Implementation for User Story 1

- [ ] T016 [P] [US1] Initialize MCP server in backend/src/mcp/server.py: Create MCPServer instance, register tools
- [ ] T017 [P] [US1] Implement add_task MCP tool in backend/src/mcp/tools/add_task.py: Accept user_id, title, description, due_date; create Task in database; return success/error
- [ ] T018 [US1] Register add_task tool with MCP server in backend/src/mcp/server.py

### TodoAgent Implementation for User Story 1

- [ ] T019 [P] [US1] Create TodoAgent in backend/src/agent/todo_agent.py: Initialize OpenAI Agent with system prompt
- [ ] T020 [P] [US1] Define Task Management Skill in backend/src/agent/skills.py: Skill for task operations
- [ ] T021 [US1] Attach Task Management Skill to TodoAgent with add_task tool
- [ ] T022 [US1] Configure agent behavior: Friendly confirmations, clear action descriptions

### Chat API Implementation for User Story 1

- [ ] T023 [P] [US1] Create chat route in backend/src/api/routes/chat.py: POST /api/v1/chat endpoint with JWT authentication
- [ ] T024 [US1] Implement conversation creation logic: If no conversation_id, create new Conversation
- [ ] T025 [US1] Implement user message storage: Save user message to Message table
- [ ] T026 [US1] Implement conversation history loading: Load last 50 messages for context
- [ ] T027 [US1] Implement agent execution: Pass user message and history to TodoAgent
- [ ] T028 [US1] Implement assistant response storage: Save agent response and tool_calls to Message table
- [ ] T029 [US1] Implement response formatting: Return ChatResponse with conversation_id, response, tool_calls
- [ ] T030 [US1] Add error handling: Catch database errors, AI service errors, return user-friendly messages

### Tests for User Story 1

- [ ] T031 [P] [US1] Unit test for add_task MCP tool in backend/tests/unit/test_add_task.py: Test task creation, validation, error handling
- [ ] T032 [P] [US1] Unit test for TodoAgent in backend/tests/unit/test_todo_agent.py: Test agent initialization, skill attachment
- [ ] T033 [P] [US1] Unit test for conversation service in backend/tests/unit/test_conversation_service.py: Test history loading, message saving
- [ ] T034 [US1] Integration test for chat API in backend/tests/integration/test_chat_add_task.py: Test full flow (send message, task created, response returned)
- [ ] T035 [US1] Integration test for JWT authentication in backend/tests/integration/test_auth.py: Test token validation, user_id extraction

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks via natural language

---

## Phase 4: User Story 2 - List Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can view their tasks by asking the AI assistant in natural language

**Independent Test**: User sends "Show me all my tasks" and receives formatted list of all their tasks

### MCP Tool Implementation for User Story 2

- [ ] T036 [P] [US2] Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py: Accept user_id, optional status filter; query Tasks from database; return task list
- [ ] T037 [US2] Register list_tasks tool with MCP server and TodoAgent

### Agent Enhancement for User Story 2

- [ ] T038 [US2] Update TodoAgent system prompt: Add instructions for formatting task lists
- [ ] T039 [US2] Add list_tasks tool to Task Management Skill

### Tests for User Story 2

- [ ] T040 [P] [US2] Unit test for list_tasks MCP tool in backend/tests/unit/test_list_tasks.py: Test task retrieval, filtering, empty list
- [ ] T041 [US2] Integration test for chat API in backend/tests/integration/test_chat_list_tasks.py: Test full flow (send message, tasks listed, response formatted)

**Checkpoint**: At this point, User Stories 1 AND 2 work together - users can add and list tasks

---

## Phase 5: User Story 3 - Complete Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can mark tasks as complete by telling the AI assistant

**Independent Test**: User sends "Mark 'buy groceries' as complete" and receives confirmation with task status updated

### MCP Tool Implementation for User Story 3

- [ ] T042 [P] [US3] Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py: Accept user_id, task_id; update Task status to "completed"; return success/error
- [ ] T043 [US3] Register complete_task tool with MCP server and TodoAgent

### Agent Enhancement for User Story 3

- [ ] T044 [US3] Update TodoAgent system prompt: Add instructions for task completion confirmations
- [ ] T045 [US3] Add complete_task tool to Task Management Skill

### Tests for User Story 3

- [ ] T046 [P] [US3] Unit test for complete_task MCP tool in backend/tests/unit/test_complete_task.py: Test task completion, task not found, already completed
- [ ] T047 [US3] Integration test for chat API in backend/tests/integration/test_chat_complete_task.py: Test full flow (send message, task completed, response confirmed)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 work together - full MVP functionality (add, list, complete)

---

## Phase 6: User Story 6 - Resume Conversation After Server Restart (Priority: P1) 🎯 MVP

**Goal**: Users can continue conversations after server restarts with full context preserved

**Independent Test**: User has conversation, server restarts, user sends new message, AI responds with context from previous messages

### Implementation for User Story 6

- [ ] T048 [US6] Verify stateless architecture: Ensure no in-memory state stored between requests
- [ ] T049 [US6] Test conversation history loading: Verify last 50 messages loaded correctly
- [ ] T050 [US6] Test conversation continuity: Send message, restart server, send follow-up, verify context maintained

### Tests for User Story 6

- [ ] T051 [P] [US6] Integration test for stateless behavior in backend/tests/integration/test_stateless.py: Test conversation persistence across "restarts" (new session instances)
- [ ] T052 [US6] Integration test for conversation context in backend/tests/integration/test_conversation_context.py: Test agent understands references to previous messages

**Checkpoint**: At this point, MVP is complete with stateless architecture verified

---

## Phase 7: User Story 4 - Update Task via Natural Language (Priority: P2)

**Goal**: Users can modify existing tasks by describing changes in natural language

**Independent Test**: User sends "Change the groceries task due date to next Monday" and receives confirmation of update

### MCP Tool Implementation for User Story 4

- [ ] T053 [P] [US4] Implement update_task MCP tool in backend/src/mcp/tools/update_task.py: Accept user_id, task_id, optional title, description, due_date; update Task in database; return success/error
- [ ] T054 [US4] Register update_task tool with MCP server and TodoAgent

### Agent Enhancement for User Story 4

- [ ] T055 [US4] Update TodoAgent system prompt: Add instructions for task update confirmations
- [ ] T056 [US4] Add update_task tool to Task Management Skill

### Tests for User Story 4

- [ ] T057 [P] [US4] Unit test for update_task MCP tool in backend/tests/unit/test_update_task.py: Test task updates, partial updates, task not found
- [ ] T058 [US4] Integration test for chat API in backend/tests/integration/test_chat_update_task.py: Test full flow (send message, task updated, response confirmed)

**Checkpoint**: User Story 4 complete - users can update tasks

---

## Phase 8: User Story 5 - Delete Task via Natural Language (Priority: P2)

**Goal**: Users can remove tasks from their list by asking the AI assistant

**Independent Test**: User sends "Delete the groceries task" and receives confirmation that task was removed

### MCP Tool Implementation for User Story 5

- [ ] T059 [P] [US5] Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py: Accept user_id, task_id; delete Task from database; return success/error
- [ ] T060 [US5] Register delete_task tool with MCP server and TodoAgent

### Agent Enhancement for User Story 5

- [ ] T061 [US5] Update TodoAgent system prompt: Add instructions for task deletion confirmations
- [ ] T062 [US5] Add delete_task tool to Task Management Skill

### Tests for User Story 5

- [ ] T063 [P] [US5] Unit test for delete_task MCP tool in backend/tests/unit/test_delete_task.py: Test task deletion, task not found, already deleted
- [ ] T064 [US5] Integration test for chat API in backend/tests/integration/test_chat_delete_task.py: Test full flow (send message, task deleted, response confirmed)

**Checkpoint**: All user stories complete - full CRUD operations via natural language

---

## Phase 9: Error Handling & Edge Cases

**Purpose**: Robust error handling and edge case coverage

- [ ] T065 [P] Implement task-not-found error handling: Return user-friendly message when task doesn't exist
- [ ] T066 [P] Implement ambiguous intent handling: Agent asks for clarification when intent is unclear
- [ ] T067 [P] Implement database connection error handling: Graceful degradation, retry logic
- [ ] T068 [P] Implement AI service timeout handling: 10-second timeout, user-friendly error message
- [ ] T069 [P] Implement rate limit handling: Exponential backoff for OpenAI API rate limits
- [ ] T070 [P] Implement user isolation verification: Ensure users can only access their own tasks and conversations
- [ ] T071 [P] Add input validation: Validate message length, conversation_id format
- [ ] T072 [P] Add SQL injection prevention: Verify SQLModel parameterized queries used throughout

### Tests for Error Handling

- [ ] T073 [P] Test task-not-found scenario in backend/tests/integration/test_error_handling.py
- [ ] T074 [P] Test ambiguous intent scenario in backend/tests/integration/test_ambiguous_intent.py
- [ ] T075 [P] Test database connection failure in backend/tests/integration/test_db_errors.py
- [ ] T076 [P] Test AI service timeout in backend/tests/integration/test_ai_timeout.py
- [ ] T077 [P] Test user isolation in backend/tests/integration/test_user_isolation.py

**Checkpoint**: Error handling complete - system handles failures gracefully

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T078 [P] Add logging: Configure structured logging for debugging and monitoring
- [ ] T079 [P] Add request/response logging: Log all API requests with user_id, conversation_id
- [ ] T080 [P] Add performance monitoring: Log query times, agent execution times
- [ ] T081 [P] Optimize database queries: Add indexes, verify query plans
- [ ] T082 [P] Implement connection pooling: Configure SQLModel connection pool size
- [ ] T083 [P] Add health check endpoint: GET /health with database connectivity check
- [ ] T084 [P] Add API documentation: Configure FastAPI automatic docs at /docs
- [ ] T085 [P] Add CORS configuration: Allow frontend origin in CORS middleware
- [ ] T086 [P] Create pytest fixtures in backend/tests/conftest.py: Database session, test user, test conversation
- [ ] T087 [P] Add test database setup: Create test database, run migrations before tests
- [ ] T088 [P] Add code formatting: Configure black, flake8 for code quality
- [ ] T089 [P] Create .env.example: Document required environment variables
- [ ] T090 [P] Create README.md: Setup instructions, API documentation links
- [ ] T091 Run full test suite: pytest backend/tests/
- [ ] T092 Run test coverage: pytest --cov=backend/src --cov-report=html
- [ ] T093 Run linting: flake8 backend/src/
- [ ] T094 Run formatting: black backend/src/
- [ ] T095 Verify all success criteria from spec.md: 95% NLP success, <3s response, 100% persistence, 100 concurrent users
- [ ] T096 Create deployment documentation: Docker setup, environment variables, database migrations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User Story 1 (Add Task): Can start after Foundational
  - User Story 2 (List Tasks): Can start after Foundational (independent of US1)
  - User Story 3 (Complete Task): Can start after Foundational (independent of US1, US2)
  - User Story 6 (Resume Conversation): Depends on US1 (needs conversation to test)
  - User Story 4 (Update Task): Can start after Foundational (independent of others)
  - User Story 5 (Delete Task): Can start after Foundational (independent of others)
- **Error Handling (Phase 9)**: Depends on at least US1 being complete
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Add Task)**: No dependencies on other stories - fully independent
- **User Story 2 (List Tasks)**: Independent of US1 (can be implemented in parallel)
- **User Story 3 (Complete Task)**: Independent of US1, US2 (can be implemented in parallel)
- **User Story 6 (Resume Conversation)**: Depends on US1 (needs conversation to test persistence)
- **User Story 4 (Update Task)**: Independent of all others
- **User Story 5 (Delete Task)**: Independent of all others

### Critical Path

The minimum viable product (MVP) requires:
1. Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1: Add Task) → Phase 4 (US2: List Tasks) → Phase 5 (US3: Complete Task) → Phase 6 (US6: Resume Conversation)

This delivers core chat functionality with task management. US4 and US5 are enhancements.

### Parallel Execution Opportunities

Tasks marked with [P] can be executed in parallel:
- Phase 1: T002, T003, T004 can run in parallel
- Phase 2: T007, T008, T009, T013, T014, T015 can run in parallel
- Phase 3: T016, T017, T019, T020, T023 can run in parallel initially
- Tests: All test tasks within a phase can run in parallel

---

## Task Estimates

**Phase 1 (Setup)**: ~2 hours
**Phase 2 (Foundational)**: ~6 hours
**Phase 3 (US1 - Add Task)**: ~10 hours
**Phase 4 (US2 - List Tasks)**: ~4 hours
**Phase 5 (US3 - Complete Task)**: ~4 hours
**Phase 6 (US6 - Resume Conversation)**: ~3 hours
**Phase 7 (US4 - Update Task)**: ~4 hours
**Phase 8 (US5 - Delete Task)**: ~4 hours
**Phase 9 (Error Handling)**: ~6 hours
**Phase 10 (Polish)**: ~8 hours

**Total Estimated Time**: ~51 hours

**MVP Time** (Phase 1 + 2 + 3 + 4 + 5 + 6): ~29 hours

---

## Testing Strategy

### Unit Tests
- Test individual MCP tools in isolation
- Test TodoAgent initialization and configuration
- Test database services (conversation, message storage)
- Mock database and AI service calls
- Target: 80%+ code coverage

### Integration Tests
- Test full chat API flow (request → agent → database → response)
- Test JWT authentication and user isolation
- Test conversation persistence and history loading
- Test stateless behavior (no in-memory state)
- Use test database with real queries
- Target: All user flows covered

### Manual Testing
- Test natural language variations ("add task", "create todo", "remind me to...")
- Test ambiguous intents (agent asks for clarification)
- Test error scenarios (invalid token, database down, AI service timeout)
- Test concurrent requests (multiple users)
- Verify response times (<3 seconds)

---

## Success Criteria Verification

After completing all tasks, verify these success criteria from spec.md:

- [ ] **SC-001**: Users can create tasks using natural language with 95% success rate for common phrasings
- [ ] **SC-002**: System responds to user messages in under 3 seconds (95th percentile)
- [ ] **SC-003**: Conversations persist correctly across 100% of server restarts with no data loss
- [ ] **SC-004**: Users can complete a 5-message conversation (create, list, complete, list, delete) without errors
- [ ] **SC-005**: System correctly interprets user intent and invokes appropriate MCP tool in 90% of cases
- [ ] **SC-007**: System handles 100 concurrent users without performance degradation
- [ ] **SC-009**: Zero unauthorized access - users can only see and modify their own tasks

---

## Notes

### Implementation Order Recommendation

1. **Start with MVP** (Phases 1-6): Get basic chat working with add, list, complete operations
2. **Add Error Handling** (Phase 9): Essential for production readiness
3. **Add Update/Delete** (Phases 7-8): Complete CRUD operations
4. **Polish** (Phase 10): Final touches and optimization

### Code Review Checkpoints

- After Phase 2: Review foundational infrastructure (database, auth, services)
- After Phase 3: Review MVP functionality (add task via chat)
- After Phase 6: Review complete MVP (add, list, complete, persistence)
- After Phase 9: Review error handling
- After Phase 10: Final review before deployment

### Performance Considerations

- Use database connection pooling (T082)
- Limit conversation history to 50 messages (T026)
- Add database indexes (T081)
- Monitor query performance (T080)
- Implement timeout handling for AI service (T068)

### Security Requirements

- JWT authentication on all endpoints (T014)
- User isolation enforcement (T070)
- SQL injection prevention via SQLModel (T072)
- Input validation (T071)
- No secrets in code (use environment variables)

---

**Tasks Status**: ✅ COMPLETE - Ready for implementation
