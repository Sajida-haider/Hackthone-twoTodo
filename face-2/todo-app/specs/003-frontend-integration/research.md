# Research: Frontend Integration

**Feature**: Frontend Integration (SPEC-3)
**Date**: 2026-02-08
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings and technology decisions for implementing the frontend integration with existing backend APIs (SPEC-1 and SPEC-2). All decisions are made in accordance with the project constitution and specification requirements.

## Research Task 1: Better Auth Integration with Next.js App Router

### Context
Need to integrate Better Auth for JWT token management with Next.js 16+ App Router, which has different patterns for Server Components vs Client Components.

### Findings

**Better Auth Capabilities**:
- Provides JWT token generation and validation
- Supports multiple authentication strategies
- Handles token refresh and expiration
- Compatible with Next.js App Router

**Integration Approach**:
- Better Auth client runs on the client side (Client Components)
- Use React Context (AuthProvider) to manage auth state globally
- Server Components can read auth state but cannot modify it
- Client Components handle all auth interactions (login, logout, token management)

**Best Practices**:
- Create AuthProvider as a Client Component wrapping the app
- Store auth state in React Context for global access
- Use localStorage for token persistence (session requirement)
- Implement useAuth hook for consuming auth state
- Separate auth logic from UI components

### Decision

**Chosen Approach**: Client-side AuthProvider with React Context

**Rationale**:
- Aligns with Better Auth's client-side architecture
- Provides global auth state access throughout the app
- Supports session persistence via localStorage
- Compatible with Next.js App Router patterns
- Simplifies auth state management

**Implementation Pattern**:
```typescript
// Client Component
'use client'
export function AuthProvider({ children }) {
  const [authState, setAuthState] = useState(...)
  // Better Auth initialization
  // Token management logic
  return <AuthContext.Provider value={authState}>{children}</AuthContext.Provider>
}
```

## Research Task 2: JWT Token Storage Strategy

### Context
Need to securely store JWT tokens with session persistence across browser restarts while protecting against XSS attacks.

### Findings

**Storage Options**:

1. **localStorage**:
   - Pros: Persists across browser restarts, simple API, synchronous access
   - Cons: Vulnerable to XSS attacks, accessible to all scripts
   - Use case: When session persistence is required

2. **sessionStorage**:
   - Pros: More secure (cleared on tab close), simple API
   - Cons: Lost on browser close, doesn't meet persistence requirement
   - Use case: When session should not persist

3. **httpOnly Cookies**:
   - Pros: Not accessible to JavaScript (XSS protection), automatic inclusion in requests
   - Cons: Requires backend cookie management, CSRF protection needed, complex for SPA
   - Use case: When maximum security is required

4. **Memory Only**:
   - Pros: Most secure (no persistence)
   - Cons: Lost on page refresh, poor UX
   - Use case: High-security applications

### Security Considerations

**XSS Protection Measures**:
- Content Security Policy (CSP) headers
- Input sanitization and output encoding
- Regular security audits
- Avoid inline scripts
- Use React's built-in XSS protection

**CSRF Protection**:
- Not required for JWT in Authorization header
- Backend validates JWT signature
- No cookies means no CSRF vulnerability

### Decision

**Chosen Approach**: localStorage with XSS protection measures

**Rationale**:
- Meets session persistence requirement (FR-004)
- Better Auth supports localStorage by default
- Simpler implementation than httpOnly cookies for SPA
- XSS risk mitigated through CSP and input sanitization
- No CSRF vulnerability with Authorization header approach

**Security Measures**:
- Implement strict Content Security Policy
- Sanitize all user input before storage/display
- Clear tokens completely on logout
- Never log tokens to console
- Regular security audits

**Trade-offs Accepted**:
- Accept XSS risk in exchange for simpler architecture and session persistence
- Rely on multiple layers of XSS protection rather than httpOnly cookies

## Research Task 3: API Client Architecture

### Context
Need centralized API client that automatically attaches JWT tokens to all authenticated requests and handles errors consistently.

### Findings

**API Client Patterns**:

1. **Axios with Interceptors**:
   - Pros: Built-in interceptor support, request/response transformation, automatic JSON handling
   - Cons: Additional dependency, larger bundle size
   - Use case: Complex API interactions with many transformations

2. **Fetch with Wrapper**:
   - Pros: Native browser API, no dependencies, smaller bundle
   - Cons: Manual interceptor implementation, more boilerplate
   - Use case: Simple API interactions, bundle size critical

3. **React Query / SWR**:
   - Pros: Built-in caching, automatic refetching, optimistic updates
   - Cons: Additional complexity, learning curve, overkill for simple apps
   - Use case: Complex data fetching with caching requirements

### Required Features

**Token Management**:
- Automatically attach JWT token to all authenticated requests
- Read token from localStorage on each request
- Handle missing token (redirect to login)

**Error Handling**:
- 401 Unauthorized: Clear auth state, redirect to login
- 403 Forbidden: Show access denied message
- 404 Not Found: Show not found message
- 500 Server Error: Show generic error with retry option
- Network Error: Show network error with retry option

**Request/Response Handling**:
- Automatic JSON parsing
- Request timeout (30 seconds)
- Retry logic for network failures
- Loading state management

### Decision

**Chosen Approach**: Axios with request/response interceptors

**Rationale**:
- Built-in interceptor support simplifies token injection
- Automatic JSON handling reduces boilerplate
- Better error handling than native fetch
- Widely used and well-documented
- Acceptable bundle size increase for better DX

**Implementation Pattern**:
```typescript
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
})

// Request interceptor: Add JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
    }
    return Promise.reject(error)
  }
)
```

## Research Task 4: Form Validation with Zod

### Context
Need client-side form validation with real-time feedback, type safety, and good developer experience.

### Findings

**Form Management Options**:

1. **React Hook Form + Zod**:
   - Pros: Excellent performance, minimal re-renders, type-safe validation, small bundle
   - Cons: Learning curve for advanced features
   - Use case: Most React applications

2. **Formik + Yup**:
   - Pros: Popular, well-documented, mature ecosystem
   - Cons: More re-renders, larger bundle, slower performance
   - Use case: Legacy applications, teams familiar with Formik

3. **Manual State Management**:
   - Pros: Full control, no dependencies
   - Cons: Lots of boilerplate, error-prone, hard to maintain
   - Use case: Very simple forms

**Validation Timing**:
- onChange: Real-time validation (can be annoying for users)
- onBlur: Validate when field loses focus (better UX)
- onSubmit: Validate on form submission (minimum requirement)

### Decision

**Chosen Approach**: React Hook Form + Zod with onBlur validation

**Rationale**:
- Best performance with minimal re-renders
- Type-safe validation with TypeScript integration
- Zod schemas are reusable and composable
- onBlur validation provides good UX (not too aggressive)
- Meets real-time validation requirement (NFR-007)

**Validation Schemas**:
```typescript
// Auth schemas
const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

// Task schemas
const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().max(2000, 'Description too long'),
})
```

## Research Task 5: Responsive Design Patterns

### Context
Need responsive design that works on mobile (320px) to desktop (1920px) using Tailwind CSS.

### Findings

**Tailwind Breakpoints**:
- sm: 640px (small tablets)
- md: 768px (tablets)
- lg: 1024px (laptops)
- xl: 1280px (desktops)
- 2xl: 1536px (large desktops)

**Mobile-First Approach**:
- Default styles for mobile (320px+)
- Add breakpoint modifiers for larger screens
- Example: `text-sm md:text-base lg:text-lg`

**Responsive Patterns**:

1. **Layout**:
   - Single column on mobile
   - Multi-column on desktop
   - Use CSS Grid or Flexbox

2. **Navigation**:
   - Hamburger menu on mobile
   - Full navigation on desktop

3. **Forms**:
   - Full-width inputs on mobile
   - Constrained width on desktop
   - Stack labels above inputs on mobile

4. **Task List**:
   - Card layout on mobile
   - Table/list layout on desktop
   - Touch-friendly targets (44px minimum)

### Decision

**Chosen Approach**: Mobile-first responsive design with Tailwind CSS

**Rationale**:
- Mobile-first ensures good mobile experience
- Tailwind provides utility classes for all breakpoints
- Meets responsive design requirement (NFR-015)
- Supports 320px-1920px range

**Component Patterns**:
```typescript
// Responsive container
<div className="container mx-auto px-4 sm:px-6 lg:px-8">

// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Responsive text
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
```

## Research Task 6: Loading and Error States

### Context
Need consistent UX patterns for loading indicators and error handling across all async operations.

### Findings

**Loading State Patterns**:

1. **Spinner**: Simple rotating icon
   - Use case: Button loading, small components
   - Duration: Any length

2. **Skeleton Screen**: Placeholder content
   - Use case: List loading, content-heavy pages
   - Duration: >500ms operations

3. **Progress Bar**: Linear progress indicator
   - Use case: File uploads, multi-step processes
   - Duration: Known duration operations

4. **Optimistic UI**: Show result immediately, rollback on error
   - Use case: Toggle actions, quick updates
   - Duration: <1s operations

**Error State Patterns**:

1. **Inline Error**: Error message next to field
   - Use case: Form validation errors
   - Action: Fix input and retry

2. **Toast Notification**: Temporary message
   - Use case: Operation failures, network errors
   - Action: Auto-dismiss or manual close

3. **Error Boundary**: Full-page error
   - Use case: Unexpected errors, app crashes
   - Action: Reload page or go home

4. **Empty State with Error**: No data + error message
   - Use case: Failed data fetch
   - Action: Retry button

### Decision

**Chosen Approach**: Combination of patterns based on context

**Loading States**:
- Buttons: Spinner + disabled state
- Task list: Skeleton screen (if >500ms)
- Forms: Spinner on submit button
- Page transitions: Top progress bar

**Error States**:
- Form validation: Inline errors
- API failures: Toast notifications
- Network errors: Toast with retry button
- Unexpected errors: Error boundary

**Rationale**:
- Provides immediate feedback (NFR-003)
- Clear error messages (NFR-010)
- Consistent UX across the app
- Meets all usability requirements

## Research Task 7: Accessibility Requirements

### Context
Need WCAG AA compliance for all interactive elements with keyboard navigation support.

### Findings

**WCAG AA Requirements**:

1. **Keyboard Navigation**:
   - All interactive elements accessible via Tab
   - Enter/Space to activate buttons
   - Escape to close modals/dialogs
   - Arrow keys for lists (optional)

2. **ARIA Labels**:
   - aria-label for icon-only buttons
   - aria-describedby for error messages
   - aria-live for dynamic content
   - role attributes for custom components

3. **Color Contrast**:
   - Normal text: 4.5:1 minimum
   - Large text (18pt+): 3:1 minimum
   - UI components: 3:1 minimum

4. **Focus Management**:
   - Visible focus indicators
   - Logical tab order
   - Focus trap in modals
   - Return focus after modal close

**Testing Tools**:
- axe-core: Automated accessibility testing
- WAVE: Browser extension for manual testing
- Lighthouse: Accessibility audit in Chrome DevTools
- Screen readers: NVDA (Windows), VoiceOver (Mac)

### Decision

**Chosen Approach**: WCAG AA compliance with automated and manual testing

**Implementation Checklist**:
- [ ] All forms keyboard navigable
- [ ] All buttons have accessible labels
- [ ] All images have alt text
- [ ] Color contrast ratios verified
- [ ] Focus indicators visible
- [ ] ARIA labels for dynamic content
- [ ] Error messages announced to screen readers
- [ ] Modal focus management

**Testing Strategy**:
- Run axe-core in unit tests
- Manual keyboard navigation testing
- Screen reader testing for critical flows
- Lighthouse accessibility audit in CI/CD

**Rationale**:
- Meets accessibility requirement (SC-010)
- Ensures inclusive user experience
- Reduces legal risk
- Improves usability for all users

## Research Task 8: Testing Strategy

### Context
Need comprehensive testing strategy covering unit, integration, and E2E tests with 80%+ coverage.

### Findings

**Testing Pyramid**:

1. **Unit Tests (70%)**: Fast, isolated, many
   - Components with React Testing Library
   - Utility functions with Jest
   - Custom hooks with React Hooks Testing Library
   - API client methods with mocked axios

2. **Integration Tests (20%)**: Medium speed, some dependencies
   - User flows with multiple components
   - API integration with mock server
   - Form submission with validation

3. **E2E Tests (10%)**: Slow, full stack, few
   - Critical user journeys with Playwright
   - Auth flow: register → verify → login
   - Task CRUD: create → view → edit → delete

**Testing Tools**:

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing
- **Playwright**: E2E testing
- **MSW (Mock Service Worker)**: API mocking
- **Testing Library User Event**: User interaction simulation

**Coverage Goals**:
- Overall: 80%+
- Business logic: 90%+
- UI components: 70%+
- E2E: Critical paths only

### Decision

**Chosen Approach**: Testing pyramid with React Testing Library + Playwright

**Test Structure**:
```
tests/
├── components/          # Unit tests for components
├── lib/                 # Unit tests for utilities
├── integration/         # Integration tests
└── e2e/                 # E2E tests with Playwright
```

**Testing Patterns**:
- Test user behavior, not implementation
- Use data-testid sparingly (prefer accessible queries)
- Mock API calls in unit/integration tests
- Use real API in E2E tests (test environment)
- Test accessibility in component tests

**Rationale**:
- Meets testing requirement (XXIII)
- Provides confidence in code changes
- Fast feedback loop with unit tests
- Critical path coverage with E2E tests
- Aligns with industry best practices

## Summary of Decisions

| Research Area | Decision | Rationale |
|---------------|----------|-----------|
| Auth Integration | Client-side AuthProvider with React Context | Aligns with Better Auth, provides global state |
| Token Storage | localStorage with XSS protection | Meets persistence requirement, simpler than cookies |
| API Client | Axios with interceptors | Built-in interceptor support, better DX |
| Form Validation | React Hook Form + Zod | Best performance, type-safe validation |
| Responsive Design | Mobile-first with Tailwind | Ensures good mobile experience |
| Loading States | Context-based patterns | Immediate feedback, consistent UX |
| Accessibility | WCAG AA compliance | Inclusive experience, legal compliance |
| Testing | Testing pyramid with RTL + Playwright | Comprehensive coverage, fast feedback |

## Implementation Readiness

All research tasks completed. Ready to proceed to Phase 1: Design & Contracts.

**Next Steps**:
1. Create data-model.md with frontend state models
2. Create contracts/ with API type definitions
3. Create quickstart.md with setup instructions
4. Proceed to /sp.tasks for task breakdown
