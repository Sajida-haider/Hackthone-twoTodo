# Tasks: Frontend Integration

**Input**: Design documents from `/specs/003-frontend-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included following TDD approach - write tests first, ensure they fail, then implement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

All paths are relative to `frontend/` directory:
- Components: `src/components/`
- Pages: `src/app/`
- API client: `src/lib/api/`
- Types: `src/types/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize Next.js 16+ project with TypeScript in frontend/ directory
- [ ] T002 [P] Install core dependencies (React 18+, Next.js, TypeScript, Tailwind CSS)
- [ ] T003 [P] Install auth dependencies (Better Auth)
- [ ] T004 [P] Install form dependencies (React Hook Form, Zod, @hookform/resolvers)
- [ ] T005 [P] Install HTTP client (Axios)
- [ ] T006 [P] Install testing dependencies (Jest, React Testing Library, Playwright)
- [ ] T007 Configure TypeScript (tsconfig.json) with strict mode enabled
- [ ] T008 [P] Configure Tailwind CSS (tailwind.config.js, globals.css)
- [ ] T009 [P] Configure Jest (jest.config.js) for component testing
- [ ] T010 [P] Configure Playwright (playwright.config.ts) for E2E testing
- [ ] T011 [P] Configure ESLint and Prettier
- [ ] T012 Create .env.local.example with required environment variables
- [ ] T013 Create project directory structure per plan.md (components/, lib/, types/, hooks/)
- [ ] T014 [P] Setup Git ignore patterns for frontend artifacts

**Checkpoint**: Project structure ready, dependencies installed, configuration complete

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Types and Utilities

- [X] T015 [P] Create User type in src/types/auth.ts
- [X] T016 [P] Create Task type in src/types/task.ts
- [X] T017 [P] Create APIError type in src/types/api.ts
- [X] T018 [P] Create form validation schemas in src/lib/validation/auth-schemas.ts (email, password)
- [X] T019 [P] Create form validation schemas in src/lib/validation/task-schemas.ts (title, description)
- [X] T020 [P] Create utility functions in src/lib/utils/cn.ts (Tailwind class merger)
- [X] T021 [P] Create utility functions in src/lib/utils/format.ts (date formatting)

### API Client Infrastructure

- [X] T022 Create Axios instance in src/lib/api/client.ts with base configuration
- [X] T023 Add request interceptor to attach JWT token from localStorage
- [X] T024 Add response interceptor for error handling (401, 403, 404, 500, network errors)
- [X] T025 Implement token management functions (getToken, setToken, clearToken)
- [X] T026 [P] Create auth API methods in src/lib/api/auth.ts (register, login, logout, verifyEmail, resendVerification)
- [X] T027 [P] Create task API methods in src/lib/api/tasks.ts (getTasks, getTask, createTask, updateTask, deleteTask, toggleCompletion)

### Authentication Infrastructure

- [X] T028 Create AuthContext in src/components/auth/AuthProvider.tsx with state management
- [X] T029 Implement Better Auth configuration in src/lib/auth/better-auth.ts
- [X] T030 Implement session persistence logic (load token from localStorage on mount)
- [X] T031 Implement login action in AuthProvider
- [X] T032 Implement logout action in AuthProvider
- [X] T033 Implement register action in AuthProvider
- [X] T034 Create useAuth hook in src/hooks/useAuth.ts
- [X] T035 Create ProtectedRoute component in src/components/auth/ProtectedRoute.tsx

### UI Component Library

- [X] T036 [P] Create Button component in src/components/ui/Button.tsx
- [X] T037 [P] Create Input component in src/components/ui/Input.tsx
- [X] T038 [P] Create LoadingSpinner component in src/components/ui/LoadingSpinner.tsx
- [X] T039 [P] Create ErrorMessage component in src/components/ui/ErrorMessage.tsx
- [X] T040 Create Toast notification system in src/components/ui/Toast.tsx
- [X] T041 Create useToast hook in src/hooks/useToast.ts
- [X] T042 [P] Create Header component in src/components/layout/Header.tsx (with user email display and logout button)

### Root Layout

- [X] T043 Create root layout in src/app/layout.tsx with AuthProvider wrapper
- [X] T044 Create landing page in src/app/page.tsx (redirect to dashboard if authenticated, login if not)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Complete Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Users can register, verify email, login, and logout with session persistence

**Independent Test**: Register new account → receive verification email → verify email → login → close browser → reopen → still logged in → logout

### Tests for User Story 1 (TDD Approach) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T045 [P] [US1] Component test for RegisterForm in tests/components/auth/RegisterForm.test.tsx (8 test cases)
- [ ] T046 [P] [US1] Component test for LoginForm in tests/components/auth/LoginForm.test.tsx (8 test cases)
- [ ] T047 [P] [US1] Integration test for auth flow in tests/integration/auth-flow.test.ts
- [ ] T048 [P] [US1] E2E test for complete auth flow in tests/e2e/auth.spec.ts (register → verify → login → logout)

### Implementation for User Story 1

#### Registration

- [X] T049 [P] [US1] Create RegisterForm component in src/components/auth/RegisterForm.tsx
- [X] T050 [US1] Integrate React Hook Form with Zod validation in RegisterForm
- [X] T051 [US1] Add password strength indicator to RegisterForm
- [X] T052 [US1] Add email validation and error display to RegisterForm
- [X] T053 [US1] Implement form submission with API call to register endpoint
- [X] T054 [US1] Add loading state during registration
- [X] T055 [US1] Add success state with message about verification email
- [X] T056 [US1] Create registration page in src/app/(auth)/register/page.tsx
- [X] T057 [US1] Add navigation link to login page from registration page

#### Email Verification

- [X] T058 [P] [US1] Create email verification page in src/app/(auth)/verify-email/page.tsx
- [X] T059 [US1] Extract token from URL query parameter
- [X] T060 [US1] Call verifyEmail API on page load
- [X] T061 [US1] Display success message and redirect to login on successful verification
- [X] T062 [US1] Display error message on failed verification
- [X] T063 [US1] Add resend verification form for expired tokens
- [X] T064 [US1] Implement resend verification with rate limiting feedback

#### Login

- [X] T065 [P] [US1] Create LoginForm component in src/components/auth/LoginForm.tsx
- [X] T066 [US1] Integrate React Hook Form with Zod validation in LoginForm
- [X] T067 [US1] Implement form submission with API call to login endpoint
- [X] T068 [US1] Store JWT token in localStorage on successful login
- [X] T069 [US1] Update AuthContext state on successful login
- [X] T070 [US1] Add loading state during login
- [X] T071 [US1] Handle error states (invalid credentials, unverified email, locked account)
- [X] T072 [US1] Redirect to dashboard on successful login
- [X] T073 [US1] Create login page in src/app/(auth)/login/page.tsx
- [X] T074 [US1] Add navigation link to registration page from login page

#### Logout

- [X] T075 [US1] Implement logout button in Header component
- [X] T076 [US1] Call logout API endpoint on logout button click
- [X] T077 [US1] Clear JWT token from localStorage on logout
- [X] T078 [US1] Clear AuthContext state on logout
- [X] T079 [US1] Redirect to login page after logout

#### Session Persistence

- [X] T080 [US1] Implement token rehydration on app initialization in AuthProvider
- [X] T081 [US1] Validate token on app load (check expiration)
- [X] T082 [US1] Handle expired token (clear state, redirect to login)
- [X] T083 [US1] Test session persistence across browser restarts

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can register, verify email, login, and logout with session persistence.

---

## Phase 4: User Story 2 - Task Creation and Viewing (Priority: P2)

**Goal**: Authenticated users can create tasks and view their task list

**Independent Test**: Login → create multiple tasks → see tasks in list → refresh page → tasks still visible

### Tests for User Story 2 (TDD Approach) ⚠️

- [ ] T084 [P] [US2] Component test for TaskForm in tests/components/tasks/TaskForm.test.tsx (6 test cases)
- [ ] T085 [P] [US2] Component test for TaskList in tests/components/tasks/TaskList.test.tsx (5 test cases)
- [ ] T086 [P] [US2] Component test for TaskItem in tests/components/tasks/TaskItem.test.tsx (4 test cases)
- [ ] T087 [P] [US2] Component test for EmptyState in tests/components/tasks/EmptyState.test.tsx (2 test cases)
- [ ] T088 [P] [US2] Integration test for task CRUD in tests/integration/task-crud.test.ts
- [ ] T089 [P] [US2] E2E test for task creation and viewing in tests/e2e/tasks.spec.ts

### Implementation for User Story 2

#### Dashboard Layout

- [X] T090 [P] [US2] Create dashboard layout in src/app/(dashboard)/layout.tsx with ProtectedRoute wrapper
- [X] T091 [US2] Add Header component to dashboard layout
- [X] T092 [US2] Create main dashboard page in src/app/(dashboard)/page.tsx

#### Task State Management

- [X] T093 [US2] Create useTasks hook in src/hooks/useTasks.ts for task state management
- [X] T094 [US2] Implement fetchTasks function in useTasks hook
- [X] T095 [US2] Implement createTask function in useTasks hook
- [X] T096 [US2] Add loading state management to useTasks hook
- [X] T097 [US2] Add error state management to useTasks hook

#### Task Creation

- [X] T098 [P] [US2] Create TaskForm component in src/components/tasks/TaskForm.tsx
- [X] T099 [US2] Integrate React Hook Form with Zod validation in TaskForm
- [X] T100 [US2] Add title input with character count (max 200)
- [X] T101 [US2] Add description textarea with character count (max 2000)
- [X] T102 [US2] Implement form submission with API call to createTask endpoint
- [X] T103 [US2] Add loading state during task creation
- [X] T104 [US2] Show success toast on task creation
- [X] T105 [US2] Clear form after successful creation
- [X] T106 [US2] Refresh task list after creation

#### Task Viewing

- [X] T107 [P] [US2] Create TaskList component in src/components/tasks/TaskList.tsx
- [X] T108 [P] [US2] Create TaskItem component in src/components/tasks/TaskItem.tsx
- [X] T109 [US2] Display task title and description in TaskItem
- [X] T110 [US2] Display task creation date in TaskItem
- [X] T111 [US2] Add loading skeleton for task list
- [X] T112 [US2] Handle empty task list with EmptyState component
- [X] T113 [P] [US2] Create EmptyState component in src/components/tasks/EmptyState.tsx
- [X] T114 [US2] Add "Create Task" button to EmptyState
- [X] T115 [US2] Integrate TaskList and TaskForm in dashboard page
- [X] T116 [US2] Fetch tasks on dashboard mount
- [X] T117 [US2] Handle task fetch errors with error message

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can authenticate and manage their task list.

---

## Phase 5: User Story 3 - Task Status Management (Priority: P3)

**Goal**: Users can mark tasks as complete/incomplete with visual feedback

**Independent Test**: Login → create task → mark as complete → see visual change → refresh → still complete → mark as incomplete

### Tests for User Story 3 (TDD Approach) ⚠️

- [ ] T118 [P] [US3] Add toggle completion tests to TaskItem.test.tsx (3 test cases)
- [ ] T119 [P] [US3] Add completion status tests to TaskList.test.tsx (2 test cases)
- [ ] T120 [P] [US3] E2E test for task completion toggle in tests/e2e/tasks.spec.ts

### Implementation for User Story 3

- [X] T121 [US3] Add toggleCompletion function to useTasks hook
- [X] T122 [US3] Add checkbox to TaskItem component
- [X] T123 [US3] Implement checkbox click handler to call toggleCompletion
- [X] T124 [US3] Add visual styling for completed tasks (strikethrough, different color)
- [X] T125 [US3] Add loading state during toggle operation
- [X] T126 [US3] Implement optimistic UI update (update immediately, rollback on error)
- [X] T127 [US3] Show success toast on completion toggle
- [X] T128 [US3] Handle toggle errors with error toast and rollback
- [X] T129 [US3] Refresh task list after toggle to ensure consistency

**Checkpoint**: All three user stories should now work independently. Users can authenticate, manage tasks, and track completion status.

---

## Phase 6: User Story 4 - Task Editing and Deletion (Priority: P4)

**Goal**: Users can edit task details and delete tasks with confirmation

**Independent Test**: Login → create task → edit title/description → save → see changes → delete task → confirm → task removed

### Tests for User Story 4 (TDD Approach) ⚠️

- [ ] T130 [P] [US4] Component test for TaskDeleteDialog in tests/components/tasks/TaskDeleteDialog.test.tsx (4 test cases)
- [ ] T131 [P] [US4] Add edit mode tests to TaskForm.test.tsx (3 test cases)
- [ ] T132 [P] [US4] E2E test for task editing and deletion in tests/e2e/tasks.spec.ts

### Implementation for User Story 4

#### Task Editing

- [X] T133 [US4] Add updateTask function to useTasks hook
- [X] T134 [US4] Add edit mode support to TaskForm component (accept initialValues prop)
- [X] T135 [US4] Add "Edit" button to TaskItem component
- [X] T136 [US4] Implement edit button click handler to show TaskForm in edit mode
- [X] T137 [US4] Pre-fill TaskForm with existing task data in edit mode
- [X] T138 [US4] Implement form submission with API call to updateTask endpoint
- [X] T139 [US4] Add loading state during task update
- [X] T140 [US4] Show success toast on task update
- [X] T141 [US4] Refresh task list after update
- [X] T142 [US4] Handle update errors with error toast
- [X] T143 [US4] Add cancel button to exit edit mode

#### Task Deletion

- [X] T144 [P] [US4] Create TaskDeleteDialog component in src/components/tasks/TaskDeleteDialog.tsx
- [X] T145 [US4] Add deleteTask function to useTasks hook
- [X] T146 [US4] Add "Delete" button to TaskItem component
- [X] T147 [US4] Implement delete button click handler to show confirmation dialog
- [X] T148 [US4] Implement confirm delete action in dialog
- [X] T149 [US4] Call deleteTask API endpoint on confirmation
- [X] T150 [US4] Add loading state during deletion
- [X] T151 [US4] Show success toast on task deletion
- [X] T152 [US4] Remove task from list immediately (optimistic update)
- [X] T153 [US4] Handle deletion errors with error toast and rollback
- [X] T154 [US4] Add cancel button to close dialog without deleting

**Checkpoint**: All four user stories should work independently. Users have full CRUD control over their tasks.

---

## Phase 7: User Story 5 - Error Handling and User Feedback (Priority: P5)

**Goal**: Users receive clear, helpful feedback for all actions and errors

**Independent Test**: Trigger various error scenarios (network failure, validation errors, expired session) and verify appropriate feedback

### Tests for User Story 5 (TDD Approach) ⚠️

- [ ] T155 [P] [US5] Component test for Toast in tests/components/ui/Toast.test.tsx (5 test cases)
- [ ] T156 [P] [US5] Component test for ErrorMessage in tests/components/ui/ErrorMessage.test.tsx (3 test cases)
- [ ] T157 [P] [US5] Integration test for error handling in tests/integration/error-handling.test.ts
- [ ] T158 [P] [US5] E2E test for error scenarios in tests/e2e/error-handling.spec.ts

### Implementation for User Story 5

#### Loading States

- [ ] T159 [P] [US5] Add loading spinner to all form submit buttons
- [ ] T160 [P] [US5] Add loading skeleton to task list while fetching
- [ ] T161 [P] [US5] Add loading state to task operations (toggle, edit, delete)
- [ ] T162 [US5] Disable form inputs during submission
- [ ] T163 [US5] Prevent multiple simultaneous submissions

#### Error Messages

- [ ] T164 [US5] Implement inline error messages for form validation
- [ ] T165 [US5] Display field-specific errors below each input
- [ ] T166 [US5] Add error styling to invalid form fields
- [ ] T167 [US5] Implement toast notifications for API errors
- [ ] T168 [US5] Add specific error messages for different error types (401, 403, 404, 500, network)
- [ ] T169 [US5] Add retry button to network error toasts
- [ ] T170 [US5] Implement retry logic for failed requests

#### Session Expiration Handling

- [ ] T171 [US5] Detect 401 errors in API client interceptor
- [ ] T172 [US5] Clear auth state on 401 error
- [ ] T173 [US5] Redirect to login page on session expiration
- [ ] T174 [US5] Show toast message explaining session expiration
- [ ] T175 [US5] Preserve form data in localStorage before redirect (optional enhancement)

#### Success Notifications

- [ ] T176 [P] [US5] Add success toast for task creation
- [ ] T177 [P] [US5] Add success toast for task update
- [ ] T178 [P] [US5] Add success toast for task deletion
- [ ] T179 [P] [US5] Add success toast for task completion toggle
- [ ] T180 [US5] Implement auto-dismiss for success toasts (3 seconds)
- [ ] T181 [US5] Add manual close button to all toasts

#### Form Validation Feedback

- [ ] T182 [US5] Implement real-time validation on blur for all form fields
- [ ] T183 [US5] Display validation errors within 500ms of blur event
- [ ] T184 [US5] Clear validation errors when user corrects input
- [ ] T185 [US5] Focus first error field on form submission failure
- [ ] T186 [US5] Add ARIA labels for screen reader accessibility

**Checkpoint**: All five user stories complete. Application provides comprehensive user feedback and error handling.

---

## Phase 8: Testing & Accessibility

**Purpose**: Comprehensive test coverage and accessibility compliance

### Unit Tests

- [ ] T187 [P] Run all component tests and verify 80%+ coverage
- [ ] T188 [P] Add missing unit tests for utility functions
- [ ] T189 [P] Add missing unit tests for custom hooks
- [ ] T190 [P] Add missing unit tests for API client methods

### Integration Tests

- [ ] T191 [P] Run all integration tests and verify complete user flows
- [ ] T192 [P] Add integration test for session persistence
- [ ] T193 [P] Add integration test for error recovery

### E2E Tests

- [ ] T194 [P] Run all E2E tests with Playwright
- [ ] T195 [P] Add E2E test for complete user journey (register → verify → login → create task → logout)
- [ ] T196 [P] Add E2E test for error scenarios

### Accessibility

- [ ] T197 Test keyboard navigation for all interactive elements
- [ ] T198 Verify all forms are keyboard accessible (Tab, Enter, Escape)
- [ ] T199 Add ARIA labels to all form fields and buttons
- [ ] T200 Verify color contrast ratios meet WCAG AA standards
- [ ] T201 Test with screen reader (NVDA or VoiceOver)
- [ ] T202 Run axe-core accessibility audit
- [ ] T203 Fix all accessibility violations found in audit
- [ ] T204 Add focus indicators to all interactive elements

**Checkpoint**: All tests passing, accessibility compliance verified

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

### Performance Optimization

- [ ] T205 [P] Implement React.memo for expensive components
- [ ] T206 [P] Add useMemo for computed values in task list
- [ ] T207 [P] Implement debouncing for form validation (300ms)
- [ ] T208 [P] Optimize bundle size with dynamic imports
- [ ] T209 Run Lighthouse performance audit
- [ ] T210 Fix performance issues identified in audit

### Security Hardening

- [ ] T211 [P] Verify JWT tokens never logged to console
- [ ] T212 [P] Verify all user input is sanitized before display
- [ ] T213 [P] Implement Content Security Policy headers
- [ ] T214 [P] Run security audit with npm audit
- [ ] T215 Fix security vulnerabilities found in audit

### Code Quality

- [ ] T216 [P] Run ESLint and fix all warnings
- [ ] T217 [P] Run Prettier to format all code
- [ ] T218 [P] Run TypeScript compiler and fix all type errors
- [ ] T219 [P] Remove console.log statements
- [ ] T220 [P] Remove commented-out code
- [ ] T221 Add JSDoc comments to complex functions

### Documentation

- [ ] T222 [P] Update README.md with setup instructions
- [ ] T223 [P] Verify quickstart.md is accurate and complete
- [ ] T224 [P] Add inline code comments for complex logic
- [ ] T225 [P] Document environment variables in .env.local.example
- [ ] T226 Create deployment guide

### Final Validation

- [ ] T227 Run complete test suite (unit + integration + E2E)
- [ ] T228 Verify all user stories work independently
- [ ] T229 Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] T230 Test on mobile devices (responsive design)
- [ ] T231 Verify backend integration (all API endpoints working)
- [ ] T232 Run quickstart.md validation (follow guide from scratch)

**Checkpoint**: Feature complete, tested, accessible, and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Testing & Accessibility (Phase 8)**: Depends on all user stories being complete
- **Polish (Phase 9)**: Depends on Testing & Accessibility completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Requires US1 for authentication but independently testable
- **User Story 3 (P3)**: Can start after Foundational - Requires US2 for task list but independently testable
- **User Story 4 (P4)**: Can start after Foundational - Requires US2 for task list but independently testable
- **User Story 5 (P5)**: Can start after Foundational - Enhances all stories but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Components before integration
- Core functionality before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Components within a story marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Task Creation/Viewing)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Auth MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Task Management MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo (Status Tracking!)
5. Add User Story 4 → Test independently → Deploy/Demo (Full CRUD!)
6. Add User Story 5 → Test independently → Deploy/Demo (Production Ready!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Task Management) - starts after US1 auth is available
   - Developer C: User Story 5 (Error Handling) - can work on infrastructure in parallel
3. After US1 & US2 complete:
   - Developer A: User Story 3 (Status Management)
   - Developer B: User Story 4 (Edit/Delete)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Follow TDD: Write tests first, ensure they fail, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All paths relative to `frontend/` directory
- Backend APIs (SPEC-1 and SPEC-2) must be running for integration testing

---

## Task Count Summary

- **Phase 1 (Setup)**: 14 tasks
- **Phase 2 (Foundational)**: 28 tasks
- **Phase 3 (User Story 1 - Auth)**: 39 tasks
- **Phase 4 (User Story 2 - Task CRUD)**: 34 tasks
- **Phase 5 (User Story 3 - Status)**: 9 tasks
- **Phase 6 (User Story 4 - Edit/Delete)**: 22 tasks
- **Phase 7 (User Story 5 - Error Handling)**: 28 tasks
- **Phase 8 (Testing & Accessibility)**: 18 tasks
- **Phase 9 (Polish)**: 26 tasks

**Total**: 232 tasks

**MVP (Phases 1-4)**: 115 tasks
**Full Feature (All Phases)**: 232 tasks
