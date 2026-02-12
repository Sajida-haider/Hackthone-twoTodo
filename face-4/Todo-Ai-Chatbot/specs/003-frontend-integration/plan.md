# Implementation Plan: Frontend Integration

**Branch**: `003-frontend-integration` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend-integration/spec.md`

## Summary

Implement a complete Next.js frontend that integrates with existing FastAPI backend (SPEC-1 and SPEC-2) to provide user authentication and task management capabilities. The frontend will handle user registration, email verification, login/logout, and full CRUD operations for tasks. All authenticated requests will include JWT tokens, and the UI will provide responsive design, loading states, error handling, and accessibility features.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**: Next.js, React 18+, Better Auth (JWT), Tailwind CSS, React Hook Form, Zod (validation)
**Storage**: Browser localStorage for JWT tokens and session persistence
**Testing**: React Testing Library, Jest, Playwright (E2E)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge) on desktop and mobile
**Project Type**: Web application (frontend only - integrates with existing backend)
**Performance Goals**: <2s initial page load, <5s task creation visibility, <1s status update reflection, <500ms form validation
**Constraints**: Must integrate with existing backend APIs (SPEC-1, SPEC-2), 15-minute JWT expiration, responsive design (320px-1920px)
**Scale/Scope**: 5 prioritized user stories, 20 functional requirements, 10 success criteria, full authentication + task CRUD

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Review

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec-First Development** | ✅ PASS | Specification created and validated before planning |
| **II. Phase Awareness** | ✅ PASS | Phase II scope only - no AI/chatbot features |
| **III. Separation of Concerns** | ✅ PASS | Frontend code in /frontend, no backend logic in UI |
| **IV. Authentication Flow** | ✅ PASS | Better Auth for JWT token management |
| **V. Authorization Enforcement** | ✅ PASS | JWT tokens sent with all authenticated requests |
| **VI. User Isolation** | ✅ PASS | Backend enforces isolation, frontend respects user context |
| **VII. Shared Secret Management** | ✅ PASS | BETTER_AUTH_SECRET from environment variable |
| **VIII. RESTful API Standards** | ✅ PASS | Consuming existing RESTful APIs from SPEC-1 and SPEC-2 |
| **IX. Task Ownership Enforcement** | ✅ PASS | Backend enforces ownership, frontend handles 401/403/404 |
| **X. Database Technology** | N/A | Frontend does not access database directly |
| **XI. ORM Requirements** | N/A | Frontend does not access database directly |
| **XII. Schema Compliance** | N/A | Frontend does not define database schema |
| **XIII. Next.js App Router** | ✅ PASS | Using App Router with Server Components by default |
| **XIV. API Client Centralization** | ✅ PASS | Centralized API client with automatic JWT attachment |
| **XV. Responsive Design** | ✅ PASS | Tailwind CSS for responsive design (320px-1920px) |
| **XVI. Specification Organization** | ✅ PASS | Spec in /specs/003-frontend-integration/ |
| **XVII. Spec Referencing** | ✅ PASS | References @specs/003-frontend-integration/spec.md |
| **XVIII. Spec Updates** | ✅ PASS | Spec updated before code changes |
| **XIX. Agent-Based Workflow** | ✅ PASS | Using Frontend Agent for implementation |
| **XX. Implementation Process** | ✅ PASS | Following Specify → Plan → Tasks → Implement workflow |
| **XXI. Prompt History Records** | ✅ PASS | PHRs created for specification and planning |
| **XXII. Architecture Decision Records** | ⚠️ PENDING | Will create ADR if significant decisions emerge |
| **XXIII. Testing Requirements** | ✅ PASS | React Testing Library + Jest for component tests, Playwright for E2E |
| **XXIV. Code Review** | ✅ PASS | All changes reviewed before merge |
| **XXV. Security Practices** | ✅ PASS | No secrets in code, input validation, secure token storage |

**Gate Result**: ✅ PASSED - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-integration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (next)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── api-client.ts    # API client interface
│   ├── auth-types.ts    # Authentication types
│   └── task-types.ts    # Task types
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/              # Auth route group (unauthenticated)
│   │   │   ├── login/
│   │   │   │   └── page.tsx     # Login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx     # Registration page
│   │   │   └── verify-email/
│   │   │       └── page.tsx     # Email verification page
│   │   ├── (dashboard)/         # Dashboard route group (authenticated)
│   │   │   ├── layout.tsx       # Dashboard layout with auth check
│   │   │   └── page.tsx         # Task dashboard (main page)
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Landing/redirect page
│   ├── components/              # React components
│   │   ├── auth/
│   │   │   ├── AuthProvider.tsx      # Auth context provider
│   │   │   ├── LoginForm.tsx         # Login form component
│   │   │   ├── RegisterForm.tsx      # Registration form component
│   │   │   └── ProtectedRoute.tsx    # Route protection HOC
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx          # Task list display
│   │   │   ├── TaskItem.tsx          # Individual task item
│   │   │   ├── TaskForm.tsx          # Create/edit task form
│   │   │   ├── TaskDeleteDialog.tsx  # Delete confirmation
│   │   │   └── EmptyState.tsx        # Empty task list state
│   │   ├── ui/
│   │   │   ├── Button.tsx            # Reusable button
│   │   │   ├── Input.tsx             # Reusable input
│   │   │   ├── LoadingSpinner.tsx    # Loading indicator
│   │   │   ├── ErrorMessage.tsx      # Error display
│   │   │   └── Toast.tsx             # Success/error notifications
│   │   └── layout/
│   │       ├── Header.tsx            # App header with user info
│   │       └── Footer.tsx            # App footer
│   ├── lib/                     # Utility libraries
│   │   ├── api/
│   │   │   ├── client.ts             # Centralized API client
│   │   │   ├── auth.ts               # Auth API methods
│   │   │   └── tasks.ts              # Task API methods
│   │   ├── auth/
│   │   │   ├── better-auth.ts        # Better Auth configuration
│   │   │   └── session.ts            # Session management utilities
│   │   ├── validation/
│   │   │   ├── auth-schemas.ts       # Zod schemas for auth forms
│   │   │   └── task-schemas.ts       # Zod schemas for task forms
│   │   └── utils/
│   │       ├── cn.ts                 # Tailwind class name utility
│   │       └── format.ts             # Date/text formatting
│   ├── types/                   # TypeScript type definitions
│   │   ├── auth.ts                   # Auth-related types
│   │   ├── task.ts                   # Task-related types
│   │   └── api.ts                    # API response types
│   └── hooks/                   # Custom React hooks
│       ├── useAuth.ts                # Auth state hook
│       ├── useTasks.ts               # Task operations hook
│       └── useToast.ts               # Toast notifications hook
├── tests/                       # Test files
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.test.tsx
│   │   │   └── RegisterForm.test.tsx
│   │   └── tasks/
│   │       ├── TaskList.test.tsx
│   │       ├── TaskItem.test.tsx
│   │       └── TaskForm.test.tsx
│   ├── integration/
│   │   ├── auth-flow.test.ts         # E2E auth flow tests
│   │   └── task-crud.test.ts         # E2E task CRUD tests
│   └── lib/
│       └── api/
│           └── client.test.ts        # API client tests
├── public/                      # Static assets
│   ├── favicon.ico
│   └── images/
├── .env.local.example           # Environment variable template
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── jest.config.js               # Jest configuration
├── playwright.config.ts         # Playwright configuration
└── package.json                 # Dependencies
```

**Structure Decision**: Using Next.js App Router structure with route groups for authenticated vs. unauthenticated pages. Components are organized by feature (auth, tasks, ui, layout). Centralized API client in lib/api/ with automatic JWT token attachment. Type definitions separated for clarity. Tests mirror source structure.

## Complexity Tracking

> **No violations detected** - All constitution principles are satisfied without requiring additional complexity.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Better Auth Integration with Next.js App Router**
   - Research: How to integrate Better Auth with Next.js 16+ App Router
   - Focus: Server Components vs Client Components for auth state
   - Output: Best practices for auth context and session management

2. **JWT Token Storage Strategy**
   - Research: Secure token storage options (localStorage vs httpOnly cookies)
   - Focus: XSS protection, CSRF protection, session persistence
   - Output: Recommended storage approach with security justification

3. **API Client Architecture**
   - Research: Centralized API client patterns for Next.js
   - Focus: Automatic token injection, error handling, retry logic
   - Output: API client design with interceptors and error boundaries

4. **Form Validation with Zod**
   - Research: Client-side validation patterns with Zod and React Hook Form
   - Focus: Real-time validation, error messages, accessibility
   - Output: Validation schema structure and form integration approach

5. **Responsive Design Patterns**
   - Research: Tailwind CSS responsive design best practices
   - Focus: Mobile-first approach, breakpoints, component responsiveness
   - Output: Responsive design guidelines and component patterns

6. **Loading and Error States**
   - Research: UX patterns for loading indicators and error handling
   - Focus: Optimistic UI updates, skeleton screens, error recovery
   - Output: Loading/error state component library and usage patterns

7. **Accessibility Requirements**
   - Research: WCAG AA compliance for forms and interactive elements
   - Focus: Keyboard navigation, ARIA labels, screen reader support
   - Output: Accessibility checklist and implementation guidelines

8. **Testing Strategy**
   - Research: Testing approaches for Next.js App Router applications
   - Focus: Component testing, integration testing, E2E testing
   - Output: Test structure and coverage requirements

**Output**: research.md with all decisions documented

## Phase 1: Design & Contracts

### Data Models (data-model.md)

**Frontend State Models:**

1. **AuthState**
   - Fields: user (email, id), token (JWT string), isAuthenticated (boolean), isLoading (boolean)
   - Purpose: Global authentication state managed by AuthProvider
   - Persistence: Token stored in localStorage, state rehydrated on app load

2. **TaskState**
   - Fields: tasks (Task[]), isLoading (boolean), error (string | null)
   - Purpose: Task list state for dashboard
   - Operations: fetch, create, update, delete, toggle completion

3. **FormState**
   - Fields: values (Record<string, any>), errors (Record<string, string>), isSubmitting (boolean)
   - Purpose: Generic form state for all forms
   - Validation: Zod schemas for each form type

4. **ToastState**
   - Fields: message (string), type (success | error | info), isVisible (boolean)
   - Purpose: User feedback notifications
   - Behavior: Auto-dismiss after 3 seconds

**Type Definitions:**

1. **User**
   - id: string (UUID)
   - email: string
   - isVerified: boolean

2. **Task**
   - id: string (UUID)
   - title: string (max 200 chars)
   - description: string (max 2000 chars)
   - isCompleted: boolean
   - createdAt: string (ISO 8601)
   - updatedAt: string (ISO 8601)

3. **APIError**
   - status: number (HTTP status code)
   - message: string
   - details?: Record<string, string[]> (validation errors)

### API Contracts (contracts/)

**API Client Interface:**

```typescript
// contracts/api-client.ts
interface APIClient {
  // Auth endpoints
  register(email: string, password: string): Promise<RegisterResponse>
  login(email: string, password: string): Promise<LoginResponse>
  logout(): Promise<void>
  verifyEmail(token: string): Promise<VerifyEmailResponse>
  resendVerification(email: string): Promise<void>

  // Task endpoints
  getTasks(): Promise<Task[]>
  getTask(id: string): Promise<Task>
  createTask(data: CreateTaskInput): Promise<Task>
  updateTask(id: string, data: UpdateTaskInput): Promise<Task>
  deleteTask(id: string): Promise<void>
  toggleTaskCompletion(id: string): Promise<Task>
}
```

**Request/Response Types:**

```typescript
// contracts/auth-types.ts
interface RegisterRequest {
  email: string
  password: string
}

interface RegisterResponse {
  message: string
  userId: string
  email: string
}

interface LoginRequest {
  email: string
  password: string
}

interface LoginResponse {
  accessToken: string
  tokenType: string
  expiresIn: number
  user: {
    id: string
    email: string
  }
}

// contracts/task-types.ts
interface CreateTaskInput {
  title: string
  description: string
}

interface UpdateTaskInput {
  title?: string
  description?: string
  isCompleted?: boolean
}
```

### Integration Points (quickstart.md)

**Backend API Endpoints:**

From SPEC-2 (Authentication):
- POST /api/v1/auth/register
- GET /api/v1/auth/verify-email?token={token}
- POST /api/v1/auth/resend-verification
- POST /api/v1/auth/login
- POST /api/v1/auth/logout

From SPEC-1 (Task CRUD):
- GET /api/v1/tasks
- POST /api/v1/tasks
- GET /api/v1/tasks/{id}
- PUT /api/v1/tasks/{id}
- DELETE /api/v1/tasks/{id}

**Environment Variables:**

```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<shared-secret-with-backend>
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Development Setup:**

1. Install dependencies: `npm install`
2. Copy `.env.local.example` to `.env.local`
3. Configure environment variables
4. Start development server: `npm run dev`
5. Run tests: `npm test`

## Architecture Decisions

### Decision 1: Token Storage Strategy

**Decision**: Store JWT tokens in localStorage with XSS protection measures

**Rationale**:
- localStorage provides session persistence across browser restarts (requirement FR-004)
- Better Auth supports localStorage by default
- XSS protection through Content Security Policy and input sanitization
- Simpler implementation than httpOnly cookies for SPA architecture

**Alternatives Considered**:
- httpOnly cookies: Better XSS protection but requires backend cookie management and CSRF tokens
- sessionStorage: More secure but loses session on browser close (violates FR-004)

**Trade-offs**:
- Accepts XSS risk in exchange for simpler architecture and session persistence
- Mitigated through CSP headers, input validation, and regular security audits

### Decision 2: Form Management

**Decision**: Use React Hook Form with Zod validation

**Rationale**:
- React Hook Form provides excellent performance with minimal re-renders
- Zod offers type-safe schema validation with TypeScript integration
- Supports real-time validation (requirement NFR-007)
- Reduces boilerplate code for form state management

**Alternatives Considered**:
- Formik: More popular but heavier and slower
- Manual state management: Too much boilerplate, error-prone

### Decision 3: State Management

**Decision**: Use React Context for auth state, local state for task operations

**Rationale**:
- Auth state is global and needs to be accessed throughout the app
- Task state is localized to dashboard and doesn't need global access
- Avoids complexity of Redux or other state management libraries
- Aligns with Next.js App Router patterns

**Alternatives Considered**:
- Redux: Overkill for this application's state management needs
- Zustand: Good option but adds dependency for minimal benefit

### Decision 4: API Error Handling

**Decision**: Centralized error handling with toast notifications and error boundaries

**Rationale**:
- Consistent error UX across all API calls (requirement FR-012)
- Error boundaries catch unexpected errors and prevent app crashes
- Toast notifications provide non-intrusive feedback
- Specific error messages guide users to resolution

**Alternatives Considered**:
- Inline error messages only: Less consistent, harder to maintain
- Modal dialogs: More intrusive, worse UX for minor errors

## Implementation Phases

### Phase 1: Foundation (P1 - Authentication Flow)

**Goal**: Implement complete authentication flow with session persistence

**Components**:
1. API client with JWT token management
2. Better Auth configuration
3. AuthProvider context
4. Registration page and form
5. Login page and form
6. Email verification page
7. Protected route wrapper
8. Session persistence logic

**Success Criteria**:
- Users can register, verify email, and login
- JWT tokens stored securely and persist across sessions
- Unauthenticated users redirected to login
- Authenticated users can access dashboard

### Phase 2: Task Management (P2 - Task Creation and Viewing)

**Goal**: Implement task creation and viewing functionality

**Components**:
1. Dashboard layout with header
2. Task list component
3. Task item component
4. Task creation form
5. Empty state component
6. Task API client methods

**Success Criteria**:
- Users can create tasks with title and description
- Tasks appear in list immediately after creation
- Empty state shown when no tasks exist
- Task list persists across page refreshes

### Phase 3: Task Operations (P3 & P4 - Status Management, Edit, Delete)

**Goal**: Implement task status updates, editing, and deletion

**Components**:
1. Task completion toggle
2. Task edit form
3. Task delete confirmation dialog
4. Optimistic UI updates

**Success Criteria**:
- Users can mark tasks complete/incomplete
- Users can edit task details
- Users can delete tasks with confirmation
- All operations reflect immediately in UI

### Phase 4: Polish (P5 - Error Handling and Feedback)

**Goal**: Implement comprehensive error handling and user feedback

**Components**:
1. Loading spinners for all async operations
2. Error message components
3. Toast notification system
4. Form validation with real-time feedback
5. Network error handling with retry
6. Session expiration handling

**Success Criteria**:
- All operations show loading states
- Clear error messages for all failure scenarios
- Success notifications for completed actions
- Form validation errors shown immediately
- Network failures handled gracefully

### Phase 5: Testing & Accessibility

**Goal**: Achieve comprehensive test coverage and accessibility compliance

**Components**:
1. Component unit tests (React Testing Library)
2. API client tests
3. Integration tests for auth flow
4. E2E tests for task CRUD (Playwright)
5. Accessibility audit and fixes
6. Keyboard navigation testing

**Success Criteria**:
- 80%+ code coverage for business logic
- All user stories have E2E tests
- WCAG AA compliance verified
- Keyboard navigation works for all features

## Testing Strategy

### Unit Tests (React Testing Library + Jest)

**Coverage**:
- All form components (LoginForm, RegisterForm, TaskForm)
- All task components (TaskList, TaskItem, TaskDeleteDialog)
- All UI components (Button, Input, LoadingSpinner, ErrorMessage, Toast)
- API client methods
- Custom hooks (useAuth, useTasks, useToast)
- Validation schemas

**Approach**:
- Test component rendering with different props
- Test user interactions (clicks, form submissions)
- Test error states and loading states
- Mock API calls and test success/failure scenarios

### Integration Tests (Playwright)

**Coverage**:
- Complete authentication flow (register → verify → login → logout)
- Complete task CRUD flow (create → view → edit → delete)
- Session persistence across page refreshes
- Error handling scenarios (network failures, validation errors)
- Protected route access control

**Approach**:
- Use real backend API (test environment)
- Test full user workflows end-to-end
- Verify UI state changes after API calls
- Test error recovery and retry mechanisms

### Accessibility Tests

**Coverage**:
- Keyboard navigation for all interactive elements
- ARIA labels for all form fields and buttons
- Color contrast ratios (WCAG AA)
- Screen reader compatibility
- Focus management

**Approach**:
- Use axe-core for automated accessibility testing
- Manual keyboard navigation testing
- Screen reader testing (NVDA/JAWS)
- Color contrast verification tools

## Performance Optimization

### Initial Load Performance

**Strategies**:
- Code splitting with Next.js dynamic imports
- Image optimization with Next.js Image component
- Font optimization with next/font
- Minimize JavaScript bundle size
- Use Server Components where possible

**Targets**:
- First Contentful Paint (FCP): <1.5s
- Largest Contentful Paint (LCP): <2.0s
- Time to Interactive (TTI): <2.5s

### Runtime Performance

**Strategies**:
- Memoize expensive computations with useMemo
- Optimize re-renders with React.memo
- Debounce form validation
- Virtualize long task lists (if >100 tasks)
- Optimize images and assets

**Targets**:
- Task list rendering: <100ms for 1000 tasks
- Form validation: <500ms response time
- UI interactions: <100ms feedback

## Security Considerations

### XSS Protection

- Content Security Policy (CSP) headers
- Input sanitization for all user-provided content
- Escape HTML in task titles and descriptions
- Use React's built-in XSS protection (JSX escaping)

### CSRF Protection

- Not required for JWT-based auth (no cookies)
- Backend validates JWT signature
- Frontend includes JWT in Authorization header

### Token Security

- Store tokens in localStorage (not in JavaScript variables)
- Clear tokens completely on logout
- Handle token expiration gracefully
- Never log tokens to console

### Input Validation

- Client-side validation with Zod schemas
- Backend validation as source of truth
- Sanitize all user input before display
- Limit input lengths (title: 200, description: 2000)

## Deployment Considerations

### Environment Configuration

**Development**:
- NEXT_PUBLIC_API_URL: http://localhost:8000
- BETTER_AUTH_SECRET: development-secret

**Production**:
- NEXT_PUBLIC_API_URL: https://api.production.com
- BETTER_AUTH_SECRET: secure-production-secret (from secrets manager)

### Build Process

1. Run tests: `npm test`
2. Run linter: `npm run lint`
3. Build production bundle: `npm run build`
4. Verify build output
5. Deploy to hosting platform (Vercel, Netlify, etc.)

### Monitoring

- Error tracking (Sentry or similar)
- Performance monitoring (Web Vitals)
- User analytics (optional, out of scope for Phase II)

## Dependencies

### Required npm Packages

**Core**:
- next@16.x
- react@18.x
- react-dom@18.x
- typescript@5.x

**Authentication**:
- better-auth@latest

**Forms & Validation**:
- react-hook-form@7.x
- zod@3.x
- @hookform/resolvers@3.x

**Styling**:
- tailwindcss@3.x
- @tailwindcss/forms@0.5.x
- clsx@2.x
- tailwind-merge@2.x

**HTTP Client**:
- axios@1.x (or use native fetch)

**Testing**:
- @testing-library/react@14.x
- @testing-library/jest-dom@6.x
- jest@29.x
- @playwright/test@1.x

**Development**:
- eslint@8.x
- prettier@3.x
- @types/react@18.x
- @types/node@20.x

## Next Steps

1. **Complete Phase 0**: Generate research.md with all technology decisions documented
2. **Complete Phase 1**: Generate data-model.md, contracts/, and quickstart.md
3. **Run /sp.tasks**: Generate detailed task breakdown (tasks.md)
4. **Run /sp.implement**: Execute implementation following task breakdown

## Open Questions

None - All technical decisions can be made based on constitution and specification requirements.
