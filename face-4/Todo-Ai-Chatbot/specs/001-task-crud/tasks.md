# Tasks: Task CRUD

**Input**: Design documents from `/specs/001-task-crud/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included as per constitution requirement (Principle XXIII: minimum 80% code coverage)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`
- Backend tests: `backend/tests/`
- Frontend tests: `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure (app/, tests/, alembic/)
- [x] T002 Create frontend directory structure (src/app/, src/components/, src/lib/)
- [x] T003 [P] Install backend dependencies (FastAPI, SQLModel, python-jose, psycopg2-binary, pytest)
- [x] T004 [P] Install frontend dependencies (Next.js, TypeScript, Tailwind CSS)
- [x] T005 [P] Configure backend environment variables template (.env.example)
- [x] T006 [P] Configure frontend environment variables template (.env.local.example)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [ ] T007 Initialize Alembic for database migrations in backend/
- [ ] T008 Create database configuration in backend/app/database.py (engine, session management)
- [ ] T009 Create User model reference in backend/app/models/user.py (stub for foreign key)
- [ ] T010 Create Task model in backend/app/models/task.py per data-model.md
- [ ] T011 Generate initial migration for tasks table with indexes
- [ ] T012 Create database trigger for automatic updated_at timestamp

### Authentication Foundation

- [ ] T013 Implement JWT validation utility in backend/app/core/security.py
- [ ] T014 Create get_current_user dependency in backend/app/api/deps.py
- [ ] T015 Create get_db session dependency in backend/app/api/deps.py

### API Foundation

- [ ] T016 [P] Initialize FastAPI application in backend/app/main.py
- [ ] T017 [P] Configure CORS middleware for frontend origin
- [ ] T018 [P] Create error response models in backend/app/schemas/error.py
- [ ] T019 [P] Create task schemas in backend/app/schemas/task.py (TaskCreate, TaskUpdate, TaskRead)

### Frontend Foundation

- [ ] T020 [P] Create centralized API client in frontend/src/lib/api/client.ts
- [ ] T021 [P] Create task TypeScript types in frontend/src/lib/types/task.ts
- [ ] T022 [P] Configure Tailwind CSS in frontend/

### Testing Foundation

- [ ] T023 [P] Configure pytest in backend/tests/conftest.py with fixtures
- [ ] T024 [P] Configure Jest and React Testing Library in frontend/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create New Task (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to create tasks with title, optional description, and optional due date

**Independent Test**: Authenticate a user, create a task, verify it appears in database with correct ownership and defaults

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T025 [P] [US1] Contract test for POST /api/tasks in backend/tests/test_task_create.py
- [ ] T026 [P] [US1] Test task creation with valid data returns 201
- [ ] T027 [P] [US1] Test task creation without token returns 401
- [ ] T028 [P] [US1] Test task creation with empty title returns 400
- [ ] T029 [P] [US1] Test task defaults to "pending" status
- [ ] T030 [P] [US1] Test task associates with authenticated user

### Implementation for User Story 1

- [ ] T031 [US1] Implement POST /api/tasks endpoint in backend/app/api/v1/tasks.py
- [ ] T032 [US1] Add input validation for TaskCreate schema
- [ ] T033 [US1] Add user_id extraction from JWT token
- [ ] T034 [US1] Add database insertion with default values
- [ ] T035 [US1] Add error handling for validation failures
- [ ] T036 [US1] Create task creation form component in frontend/src/components/tasks/TaskForm.tsx
- [ ] T037 [US1] Implement createTask API method in frontend/src/lib/api/tasks.ts
- [ ] T038 [US1] Add form validation in frontend
- [ ] T039 [US1] Add success/error feedback in UI

**Checkpoint**: At this point, users can create tasks. User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - View My Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to view all their tasks and individual task details

**Independent Test**: Create multiple tasks for a user, retrieve task list, verify only user's tasks are returned

### Tests for User Story 2

- [ ] T040 [P] [US2] Contract test for GET /api/tasks in backend/tests/test_task_list.py
- [ ] T041 [P] [US2] Test list returns only authenticated user's tasks
- [ ] T042 [P] [US2] Test list returns empty array for user with no tasks
- [ ] T043 [P] [US2] Test list without token returns 401
- [ ] T044 [P] [US2] Contract test for GET /api/tasks/{id} in backend/tests/test_task_get.py
- [ ] T045 [P] [US2] Test get task returns 200 for owned task
- [ ] T046 [P] [US2] Test get task returns 404 for other user's task
- [ ] T047 [P] [US2] Test get task returns 404 for non-existent task

### Implementation for User Story 2

- [ ] T048 [P] [US2] Implement GET /api/tasks endpoint in backend/app/api/v1/tasks.py
- [ ] T049 [P] [US2] Implement GET /api/tasks/{id} endpoint in backend/app/api/v1/tasks.py
- [ ] T050 [US2] Add user_id filtering in database queries
- [ ] T051 [US2] Add ownership verification for single task retrieval
- [ ] T052 [US2] Implement listTasks API method in frontend/src/lib/api/tasks.ts
- [ ] T053 [US2] Implement getTask API method in frontend/src/lib/api/tasks.ts
- [ ] T054 [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx
- [ ] T055 [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [ ] T056 [US2] Create tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T057 [US2] Add loading and empty states in UI
- [ ] T058 [US2] Add error handling in UI

**Checkpoint**: At this point, users can create and view tasks. MVP is complete (P1 stories done).

---

## Phase 5: User Story 3 - Update Task Details (Priority: P2)

**Goal**: Enable authenticated users to update task title, description, status, and due date

**Independent Test**: Create a task, update various fields, verify changes persist and updated_at changes

### Tests for User Story 3

- [ ] T059 [P] [US3] Contract test for PATCH /api/tasks/{id} in backend/tests/test_task_update.py
- [ ] T060 [P] [US3] Test update title returns 200 with updated task
- [ ] T061 [P] [US3] Test update status to "completed" works
- [ ] T062 [P] [US3] Test update with empty title returns 400
- [ ] T063 [P] [US3] Test update with invalid status returns 400
- [ ] T064 [P] [US3] Test update other user's task returns 404
- [ ] T065 [P] [US3] Test update without token returns 401
- [ ] T066 [P] [US3] Test updated_at timestamp changes on update

### Implementation for User Story 3

- [ ] T067 [US3] Implement PATCH /api/tasks/{id} endpoint in backend/app/api/v1/tasks.py
- [ ] T068 [US3] Add partial update logic (only update provided fields)
- [ ] T069 [US3] Add ownership verification before update
- [ ] T070 [US3] Add validation for TaskUpdate schema
- [ ] T071 [US3] Add automatic updated_at timestamp update
- [ ] T072 [US3] Implement updateTask API method in frontend/src/lib/api/tasks.ts
- [ ] T073 [US3] Add edit mode to TaskItem component
- [ ] T074 [US3] Create completion toggle button in TaskItem
- [ ] T075 [US3] Add optimistic UI updates
- [ ] T076 [US3] Add error handling and rollback on failure

**Checkpoint**: At this point, users can create, view, and update tasks. All P1 and P2 stories complete.

---

## Phase 6: User Story 4 - Delete Task (Priority: P3)

**Goal**: Enable authenticated users to permanently delete their tasks

**Independent Test**: Create a task, delete it, verify it no longer appears in list and cannot be retrieved

### Tests for User Story 4

- [ ] T077 [P] [US4] Contract test for DELETE /api/tasks/{id} in backend/tests/test_task_delete.py
- [ ] T078 [P] [US4] Test delete returns 204 for owned task
- [ ] T079 [P] [US4] Test delete removes task from database
- [ ] T080 [P] [US4] Test delete other user's task returns 404
- [ ] T081 [P] [US4] Test delete non-existent task returns 404
- [ ] T082 [P] [US4] Test delete without token returns 401
- [ ] T083 [P] [US4] Test deleted task cannot be retrieved

### Implementation for User Story 4

- [ ] T084 [US4] Implement DELETE /api/tasks/{id} endpoint in backend/app/api/v1/tasks.py
- [ ] T085 [US4] Add ownership verification before deletion
- [ ] T086 [US4] Add permanent deletion from database
- [ ] T087 [US4] Implement deleteTask API method in frontend/src/lib/api/tasks.ts
- [ ] T088 [US4] Create DeleteTaskButton component in frontend/src/components/tasks/DeleteTaskButton.tsx
- [ ] T089 [US4] Add confirmation dialog before deletion
- [ ] T090 [US4] Remove task from UI after successful deletion
- [ ] T091 [US4] Add error handling for deletion failures

**Checkpoint**: All user stories complete. Full CRUD lifecycle implemented.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T092 [P] Add API documentation with OpenAPI/Swagger UI
- [ ] T093 [P] Add request logging in backend
- [ ] T094 [P] Add error logging in backend
- [ ] T095 [P] Implement rate limiting middleware (optional)
- [ ] T096 [P] Add loading spinners for all async operations in frontend
- [ ] T097 [P] Add toast notifications for success/error messages in frontend
- [ ] T098 [P] Optimize database queries with proper indexes
- [ ] T099 [P] Add frontend component tests for TaskList, TaskItem, TaskForm
- [ ] T100 [P] Add integration tests for complete user flows
- [ ] T101 [P] Run quickstart.md validation (setup and test all features)
- [ ] T102 [P] Update documentation with any implementation changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but logically follows US1+US2)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend implementation before frontend integration
- API methods before UI components
- Core functionality before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Backend and frontend tasks within a story can run in parallel after API contract is defined
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T025: Contract test for POST /api/tasks
Task T026: Test task creation with valid data
Task T027: Test task creation without token
Task T028: Test task creation with empty title
Task T029: Test task defaults to "pending" status
Task T030: Test task associates with authenticated user

# After tests fail, implement backend and frontend in parallel:
Backend: Task T031-T035 (API endpoint implementation)
Frontend: Task T036-T039 (UI implementation)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test MVP independently
6. Deploy/demo if ready

**MVP Delivers**: Users can create and view tasks - core value proposition

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Create Task)
   - Developer B: User Story 2 (View Tasks)
   - Developer C: User Story 3 (Update Task)
   - Developer D: User Story 4 (Delete Task)
3. Stories complete and integrate independently

---

## Task Execution Checklist

For each task:
- [ ] Read task description and acceptance criteria
- [ ] Check dependencies are complete
- [ ] Write tests first (if test task)
- [ ] Implement functionality
- [ ] Verify tests pass
- [ ] Verify acceptance criteria met
- [ ] Commit changes with descriptive message
- [ ] Update task status to complete

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow constitution Principle XXIII: minimum 80% code coverage
- Follow constitution Principle VI: user isolation enforced at query level
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Total Task Count

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 18 tasks
- **Phase 3 (US1 - Create)**: 15 tasks (6 tests + 9 implementation)
- **Phase 4 (US2 - View)**: 19 tasks (8 tests + 11 implementation)
- **Phase 5 (US3 - Update)**: 18 tasks (8 tests + 10 implementation)
- **Phase 6 (US4 - Delete)**: 15 tasks (7 tests + 8 implementation)
- **Phase 7 (Polish)**: 11 tasks

**Total**: 102 tasks

**MVP (P1 only)**: 58 tasks (Setup + Foundational + US1 + US2)
**Full Feature**: 102 tasks (all phases)
