# Tasks: Authentication & Authorization

**Input**: Design documents from `/specs/002-auth-authorization/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/ (complete)

**Tests**: Tests are included as this is a security-critical feature requiring comprehensive test coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/app/`, `frontend/src/`
- Backend tests: `backend/tests/`
- Frontend tests: `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Install backend dependencies (fastapi, sqlmodel, python-jose, passlib, email-validator) in backend/requirements.txt
- [x] T002 Install frontend dependencies (better-auth) in frontend/package.json
- [x] T003 [P] Configure environment variables template in backend/.env.example
- [x] T004 [P] Configure environment variables template in frontend/.env.local.example
- [x] T005 [P] Setup pytest configuration in backend/pytest.ini
- [x] T006 [P] Setup test fixtures in backend/tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [x] T007 Create User model in backend/app/models/user.py with all fields from data-model.md
- [x] T008 Create VerificationToken model in backend/app/models/verification_token.py
- [x] T009 Create AuthEvent model in backend/app/models/auth_event.py
- [x] T010 Create database migration for users table in backend/alembic/versions/
- [x] T011 Create database migration for verification_tokens table in backend/alembic/versions/
- [x] T012 Create database migration for auth_events table in backend/alembic/versions/

### Security Foundation

- [x] T013 [P] Implement password hashing utilities in backend/app/core/security.py (bcrypt)
- [x] T014 [P] Implement JWT token generation in backend/app/core/security.py
- [x] T015 [P] Implement JWT token validation in backend/app/core/security.py
- [x] T016 [P] Implement verification token generation in backend/app/core/security.py (secrets.token_urlsafe)
- [x] T017 Create get_current_user dependency in backend/app/api/deps.py
- [x] T018 Create get_db dependency in backend/app/api/deps.py

### Email Foundation

- [x] T019 [P] Implement SMTP email service in backend/app/services/email.py
- [x] T020 [P] Create verification email template in backend/app/templates/verification_email.html

### API Foundation

- [x] T021 Create auth router in backend/app/api/v1/auth.py (empty, endpoints added per story)
- [x] T022 Register auth router in backend/app/main.py
- [x] T023 [P] Create auth request/response schemas in backend/app/schemas/auth.py
- [x] T024 [P] Create user schemas in backend/app/schemas/user.py

### Frontend Foundation

- [x] T025 [P] Configure Better Auth in frontend/src/lib/auth/better-auth.ts
- [x] T026 [P] Create centralized API client in frontend/src/lib/api/client.ts with JWT injection
- [x] T027 [P] Create auth API client in frontend/src/lib/api/auth.ts
- [x] T028 [P] Create auth TypeScript types in frontend/src/types/auth.ts
- [x] T029 Create AuthProvider component in frontend/src/components/auth/AuthProvider.tsx
- [x] T030 Integrate AuthProvider in frontend/src/app/layout.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts with email/password, receive verification email

**Independent Test**: Submit registration form with valid credentials, verify account created and email sent

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T031 [P] [US1] Create test for successful registration in backend/tests/test_auth_register.py
- [x] T032 [P] [US1] Create test for duplicate email rejection in backend/tests/test_auth_register.py
- [x] T033 [P] [US1] Create test for invalid email format in backend/tests/test_auth_register.py
- [x] T034 [P] [US1] Create test for weak password rejection in backend/tests/test_auth_register.py
- [x] T035 [P] [US1] Create test for verification email sent in backend/tests/test_auth_register.py
- [x] T036 [P] [US1] Create test for password hashing (no plaintext) in backend/tests/test_auth_register.py

### Backend Implementation for User Story 1

- [x] T037 [US1] Implement POST /api/auth/register endpoint in backend/app/api/v1/auth.py
- [x] T038 [US1] Add email format validation in registration endpoint
- [x] T039 [US1] Add password strength validation in registration endpoint
- [x] T040 [US1] Add duplicate email check in registration endpoint
- [x] T041 [US1] Hash password with bcrypt before storing
- [x] T042 [US1] Create verification token and save to database
- [x] T043 [US1] Send verification email with token link
- [x] T044 [US1] Log registration event to auth_events table
- [x] T045 [US1] Return 201 Created with user_id and email

### Frontend Implementation for User Story 1

- [x] T046 [P] [US1] Create registration page in frontend/src/app/(auth)/register/page.tsx
- [x] T047 [P] [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [x] T048 [US1] Add email input with validation in RegisterForm
- [x] T049 [US1] Add password input with strength indicator in RegisterForm
- [x] T050 [US1] Add form submission with loading state in RegisterForm
- [x] T051 [US1] Add success message display in RegisterForm
- [x] T052 [US1] Add error handling and display in RegisterForm
- [x] T053 [P] [US1] Create RegisterForm tests in frontend/tests/auth/RegisterForm.test.tsx

**Checkpoint**: User Story 1 complete - users can register and receive verification emails

---

## Phase 4: User Story 2 - Email Verification (Priority: P2)

**Goal**: Users can verify their email by clicking link, account becomes active

**Independent Test**: Click verification link from email, verify account is marked as verified

### Tests for User Story 2

- [x] T054 [P] [US2] Create test for successful verification in backend/tests/test_auth_verify.py
- [x] T055 [P] [US2] Create test for invalid token rejection in backend/tests/test_auth_verify.py
- [x] T056 [P] [US2] Create test for expired token rejection in backend/tests/test_auth_verify.py
- [x] T057 [P] [US2] Create test for already verified account in backend/tests/test_auth_verify.py
- [x] T058 [P] [US2] Create test for token single-use enforcement in backend/tests/test_auth_verify.py

### Backend Implementation for User Story 2

- [x] T059 [US2] Implement GET /api/auth/verify-email endpoint in backend/app/api/v1/auth.py
- [x] T060 [US2] Validate token exists in database
- [x] T061 [US2] Check token expiration (24 hours)
- [x] T062 [US2] Check token not already used (verified_at is NULL)
- [x] T063 [US2] Mark user as verified (is_verified = TRUE)
- [x] T064 [US2] Mark token as used (set verified_at timestamp)
- [x] T065 [US2] Log email verification event to auth_events table
- [x] T066 [US2] Return 200 OK with success message

### Resend Verification Implementation

- [x] T067 [US2] Implement POST /api/auth/resend-verification endpoint in backend/app/api/v1/auth.py
- [x] T068 [US2] Validate email exists and is not verified
- [x] T069 [US2] Generate new verification token
- [x] T070 [US2] Send new verification email
- [x] T071 [US2] Add rate limiting (max 3 per hour per email)
- [x] T072 [US2] Return 200 OK with success message
- [x] T073 [P] [US2] Create tests for resend verification in backend/tests/test_auth_verify.py

### Frontend Implementation for User Story 2

- [x] T074 [P] [US2] Create email verification page in frontend/src/app/(auth)/verify-email/page.tsx
- [x] T075 [US2] Extract token from URL query parameter
- [x] T076 [US2] Call verify-email API endpoint
- [x] T077 [US2] Display success message and redirect to login
- [x] T078 [US2] Display error message for invalid/expired tokens
- [x] T079 [US2] Add "Resend verification email" button
- [x] T080 [P] [US2] Create verification page tests in frontend/tests/auth/VerifyEmail.test.tsx

**Checkpoint**: User Story 2 complete - users can verify emails and request new verification links

---

## Phase 5: User Story 3 - User Login (Priority: P3)

**Goal**: Verified users can login with email/password and receive JWT token

**Independent Test**: Login with verified credentials, verify JWT token returned and valid

### Tests for User Story 3

- [x] T081 [P] [US3] Create test for successful login in backend/tests/test_auth_login.py
- [x] T082 [P] [US3] Create test for invalid credentials rejection in backend/tests/test_auth_login.py
- [x] T083 [P] [US3] Create test for unverified email rejection in backend/tests/test_auth_login.py
- [x] T084 [P] [US3] Create test for account lockout after 5 failures in backend/tests/test_auth_login.py
- [x] T085 [P] [US3] Create test for locked account rejection in backend/tests/test_auth_login.py
- [x] T086 [P] [US3] Create test for failed attempt counter reset on success in backend/tests/test_auth_login.py
- [x] T087 [P] [US3] Create test for JWT token structure and expiration in backend/tests/test_auth_login.py

### Backend Implementation for User Story 3

- [x] T088 [US3] Implement POST /api/auth/login endpoint in backend/app/api/v1/auth.py
- [x] T089 [US3] Validate email and password provided
- [x] T090 [US3] Check user exists in database
- [x] T091 [US3] Check account not locked (locked_until is NULL or expired)
- [x] T092 [US3] Check email is verified (is_verified = TRUE)
- [x] T093 [US3] Verify password with bcrypt
- [x] T094 [US3] On success: reset failed_login_attempts to 0
- [x] T095 [US3] On success: update last_login_at timestamp
- [x] T096 [US3] On success: generate JWT token with 15-minute expiration
- [x] T097 [US3] On success: log successful login event
- [x] T098 [US3] On failure: increment failed_login_attempts
- [x] T099 [US3] On failure: lock account if attempts >= 5 (set locked_until = NOW + 15 min)
- [x] T100 [US3] On failure: log failed login event
- [x] T101 [US3] Return generic error message (prevent user enumeration)
- [x] T102 [US3] Return 200 OK with token on success, 401 on failure, 403 if locked

### Frontend Implementation for User Story 3

- [x] T103 [P] [US3] Create login page in frontend/src/app/(auth)/login/page.tsx
- [x] T104 [P] [US3] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [x] T105 [US3] Add email input in LoginForm
- [x] T106 [US3] Add password input in LoginForm
- [x] T107 [US3] Add form submission with loading state in LoginForm
- [x] T108 [US3] Store JWT token in Better Auth on success
- [x] T109 [US3] Redirect to dashboard on successful login
- [x] T110 [US3] Display error messages (generic for security)
- [x] T111 [US3] Display account locked message with retry time
- [x] T112 [US3] Display email verification required message
- [x] T113 [P] [US3] Create LoginForm tests in frontend/tests/auth/LoginForm.test.tsx

**Checkpoint**: User Story 3 complete - verified users can login and receive JWT tokens

---

## Phase 6: User Story 4 - Access Protected Resources (Priority: P4)

**Goal**: Authenticated users can access protected endpoints with valid JWT tokens

**Independent Test**: Make request to protected endpoint with valid token, verify access granted

### Tests for User Story 4

- [x] T114 [P] [US4] Create test for valid token access in backend/tests/test_auth_middleware.py
- [x] T115 [P] [US4] Create test for missing token rejection in backend/tests/test_auth_middleware.py
- [x] T116 [P] [US4] Create test for invalid token rejection in backend/tests/test_auth_middleware.py
- [x] T117 [P] [US4] Create test for expired token rejection in backend/tests/test_auth_middleware.py
- [x] T118 [P] [US4] Create test for tampered token rejection in backend/tests/test_auth_middleware.py
- [x] T119 [P] [US4] Create test for user extraction from token in backend/tests/test_auth_middleware.py

### Backend Implementation for User Story 4

- [x] T120 [US4] Implement JWT validation middleware in backend/app/middleware/auth.py
- [x] T121 [US4] Extract token from Authorization header (Bearer scheme)
- [x] T122 [US4] Validate token signature with BETTER_AUTH_SECRET
- [x] T123 [US4] Check token expiration claim
- [x] T124 [US4] Extract user_id from token payload
- [x] T125 [US4] Verify user exists and is active
- [x] T126 [US4] Attach user to request context
- [x] T127 [US4] Return 401 for missing/invalid/expired tokens
- [x] T128 [US4] Log token validation failures to auth_events

### Logout Implementation

- [x] T129 [US4] Implement POST /api/auth/logout endpoint in backend/app/api/v1/auth.py
- [x] T130 [US4] Require valid JWT token (use get_current_user dependency)
- [x] T131 [US4] Log logout event to auth_events table
- [x] T132 [US4] Return 200 OK with success message
- [x] T133 [P] [US4] Create logout tests in backend/tests/test_auth_logout.py

### Frontend Implementation for User Story 4

- [x] T134 [US4] Update API client to include JWT token in all requests
- [x] T135 [US4] Handle 401 responses by redirecting to login
- [x] T136 [US4] Handle 403 responses with appropriate error message
- [x] T137 [US4] Implement logout functionality in frontend
- [x] T138 [US4] Clear JWT token from Better Auth on logout
- [x] T139 [US4] Redirect to login page after logout
- [x] T140 [P] [US4] Create protected route wrapper component
- [x] T141 [P] [US4] Create API client tests in frontend/tests/lib/api-client.test.ts

**Checkpoint**: User Story 4 complete - full authentication flow working end-to-end

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Security Hardening

- [x] T142 [P] Add CORS configuration in backend/app/main.py
- [x] T143 [P] Add rate limiting for auth endpoints (optional)
- [ ] T144 [P] Add request ID tracking for audit logs
- [x] T145 [P] Add IP address logging to all auth events
- [x] T146 [P] Add user agent logging to all auth events

### Testing & Validation

- [ ] T147 [P] Run all backend tests with coverage report (target: 80%+)
- [ ] T148 [P] Run all frontend tests with coverage report
- [ ] T149 Create end-to-end integration test for full auth flow
- [ ] T150 Test account lockout mechanism manually
- [ ] T151 Test email verification expiration manually
- [ ] T152 Test JWT token expiration manually
- [ ] T153 Validate all API contracts match implementation

### Documentation & Cleanup

- [x] T154 [P] Update quickstart.md with any implementation changes
- [x] T155 [P] Add API documentation comments to all endpoints
- [x] T156 [P] Create database seed script for test users
- [x] T157 [P] Add environment variable validation on startup
- [x] T158 Code cleanup and remove debug logging
- [x] T159 Run security audit checklist from quickstart.md

**Checkpoint**: Feature complete and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Logically follows US1+US2 but technically independent
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Demonstrates complete flow but technically independent

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Email Verification)
5. Complete Phase 5: User Story 3 (Login)
6. **STOP and VALIDATE**: Test full registration → verification → login flow
7. Deploy/demo if ready

### Full Feature (All User Stories)

1. Complete MVP (Phases 1-5)
2. Complete Phase 6: User Story 4 (Protected Resources)
3. Complete Phase 7: Polish & Cross-Cutting Concerns
4. **FINAL VALIDATION**: Run all tests, security audit, quickstart validation
5. Production deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Registration)
   - Developer B: User Story 2 (Email Verification)
   - Developer C: User Story 3 (Login)
   - Developer D: User Story 4 (Protected Resources)
3. Stories complete and integrate independently
4. Team completes Polish phase together

---

## Task Summary

**Total Tasks**: 159
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 24 tasks
- Phase 3 (US1 - Registration): 23 tasks
- Phase 4 (US2 - Email Verification): 27 tasks
- Phase 5 (US3 - Login): 33 tasks
- Phase 6 (US4 - Protected Resources): 28 tasks
- Phase 7 (Polish): 18 tasks

**MVP Tasks** (Phases 1-5): 113 tasks
**Full Feature Tasks** (All phases): 159 tasks

**Parallel Tasks**: 67 tasks marked [P] can run in parallel within their phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution compliance verified throughout implementation
- Security is critical - all tests must pass before deployment
