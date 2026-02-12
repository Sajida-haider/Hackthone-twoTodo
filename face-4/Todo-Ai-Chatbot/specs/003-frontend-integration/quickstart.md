# Quickstart Guide: Frontend Integration

**Feature**: Frontend Integration (SPEC-3)
**Date**: 2026-02-08
**Audience**: Frontend developers implementing the integration

## Overview

This guide provides step-by-step instructions for setting up the frontend development environment and integrating with the existing backend APIs (SPEC-1 and SPEC-2).

## Prerequisites

### Required Software

- **Node.js**: v18.x or higher
- **npm**: v9.x or higher (comes with Node.js)
- **Git**: Latest version
- **Code Editor**: VS Code recommended with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - TypeScript and JavaScript Language Features

### Backend Requirements

Before starting frontend development, ensure:

1. **Backend is running**: FastAPI backend from SPEC-1 and SPEC-2 must be running
   - Default URL: `http://localhost:8000`
   - Health check: `http://localhost:8000/health`
   - API docs: `http://localhost:8000/docs`

2. **Database is configured**: Neon PostgreSQL database is set up and migrations are applied

3. **Environment variables are set**: Backend has `BETTER_AUTH_SECRET` configured

## Initial Setup

### 1. Clone Repository

```bash
# If not already cloned
git clone <repository-url>
cd todo-app

# Checkout feature branch
git checkout 003-frontend-integration
```

### 2. Install Dependencies

```bash
cd frontend
npm install
```

This installs all required packages:
- Next.js 16+
- React 18+
- TypeScript
- Tailwind CSS
- Better Auth
- React Hook Form
- Zod
- Axios
- Testing libraries

### 3. Configure Environment Variables

Create `.env.local` file in the `frontend/` directory:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Secret (must match backend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=your-secret-key-here

# Frontend URL (for redirects)
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Important**: The `BETTER_AUTH_SECRET` must be the same value used by the backend for JWT token signing and verification.

### 4. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 5. Verify Setup

1. **Check backend connection**:
   - Open browser to `http://localhost:3000`
   - Open browser console (F12)
   - Look for any API connection errors

2. **Test authentication flow**:
   - Navigate to `/register`
   - Create a test account
   - Check email for verification link (if email service configured)
   - Login with credentials

3. **Test task operations**:
   - Create a new task
   - View task list
   - Toggle task completion
   - Edit task
   - Delete task

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Unauthenticated routes
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── verify-email/
│   │   ├── (dashboard)/       # Authenticated routes
│   │   │   └── page.tsx       # Main dashboard
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page
│   ├── components/            # React components
│   │   ├── auth/             # Auth-related components
│   │   ├── tasks/            # Task-related components
│   │   ├── ui/               # Reusable UI components
│   │   └── layout/           # Layout components
│   ├── lib/                  # Utility libraries
│   │   ├── api/              # API client
│   │   ├── auth/             # Auth utilities
│   │   ├── validation/       # Zod schemas
│   │   └── utils/            # Helper functions
│   ├── types/                # TypeScript types
│   ├── hooks/                # Custom React hooks
│   └── styles/               # Global styles
├── tests/                    # Test files
├── public/                   # Static assets
└── package.json              # Dependencies
```

## Development Workflow

### 1. Create New Component

```bash
# Example: Create a new UI component
touch src/components/ui/Badge.tsx
```

Component template:

```typescript
interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'error'
}

export function Badge({ children, variant = 'default' }: BadgeProps) {
  return (
    <span className={`badge badge-${variant}`}>
      {children}
    </span>
  )
}
```

### 2. Add API Method

Edit `src/lib/api/tasks.ts`:

```typescript
export async function getTaskStats(): Promise<TaskStats> {
  const response = await apiClient.get('/api/v1/tasks/stats')
  return response.data
}
```

### 3. Create Custom Hook

Edit `src/hooks/useTaskStats.ts`:

```typescript
export function useTaskStats() {
  const [stats, setStats] = useState<TaskStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getTaskStats()
      .then(setStats)
      .finally(() => setIsLoading(false))
  }, [])

  return { stats, isLoading }
}
```

### 4. Write Tests

Create test file alongside component:

```typescript
// src/components/ui/Badge.test.tsx
import { render, screen } from '@testing-library/react'
import { Badge } from './Badge'

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>Test</Badge>)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})
```

Run tests:

```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- Badge.test     # Run specific test
```

## API Integration

### Authentication Flow

```typescript
// 1. Register
const response = await apiClient.register(email, password)
// User receives verification email

// 2. Verify Email
await apiClient.verifyEmail(token)
// User account is activated

// 3. Login
const loginResponse = await apiClient.login(email, password)
// Store token in localStorage
localStorage.setItem('auth_token', loginResponse.accessToken)

// 4. Make Authenticated Requests
// Token automatically attached by API client interceptor
const tasks = await apiClient.getTasks()

// 5. Logout
await apiClient.logout()
// Clear token from localStorage
localStorage.removeItem('auth_token')
```

### Task Operations

```typescript
// Create task
const newTask = await apiClient.createTask({
  title: 'My Task',
  description: 'Task description'
})

// Get all tasks
const tasks = await apiClient.getTasks()

// Update task
const updated = await apiClient.updateTask(taskId, {
  title: 'Updated Title'
})

// Toggle completion
const toggled = await apiClient.toggleCompletion(taskId)

// Delete task
await apiClient.deleteTask(taskId)
```

### Error Handling

```typescript
try {
  await apiClient.createTask(data)
} catch (error) {
  if (isAPIError(error)) {
    if (error.status === 401) {
      // Redirect to login
      router.push('/login')
    } else if (error.status === 400 && error.details) {
      // Show validation errors
      Object.entries(error.details).forEach(([field, messages]) => {
        setError(field, { message: messages[0] })
      })
    } else {
      // Show generic error
      toast.error(error.message)
    }
  }
}
```

## Common Tasks

### Add New Page

1. Create page file in `src/app/`:
   ```bash
   mkdir -p src/app/settings
   touch src/app/settings/page.tsx
   ```

2. Implement page component:
   ```typescript
   export default function SettingsPage() {
     return <div>Settings</div>
   }
   ```

3. Add navigation link in header

### Add Form Validation

1. Create Zod schema in `src/lib/validation/`:
   ```typescript
   export const taskSchema = z.object({
     title: z.string().min(1).max(200),
     description: z.string().max(2000),
   })
   ```

2. Use with React Hook Form:
   ```typescript
   const form = useForm({
     resolver: zodResolver(taskSchema),
   })
   ```

### Add Loading State

```typescript
const [isLoading, setIsLoading] = useState(false)

async function handleSubmit() {
  setIsLoading(true)
  try {
    await apiClient.createTask(data)
  } finally {
    setIsLoading(false)
  }
}

return (
  <Button disabled={isLoading}>
    {isLoading ? <LoadingSpinner /> : 'Submit'}
  </Button>
)
```

### Add Toast Notification

```typescript
import { useToast } from '@/hooks/useToast'

function MyComponent() {
  const { toast } = useToast()

  function handleSuccess() {
    toast.success('Task created successfully!')
  }

  function handleError() {
    toast.error('Failed to create task')
  }
}
```

## Testing

### Run Tests

```bash
# Unit tests
npm test

# Watch mode
npm test -- --watch

# Coverage report
npm test -- --coverage

# E2E tests
npm run test:e2e

# E2E tests in UI mode
npm run test:e2e:ui
```

### Test Structure

```
tests/
├── components/           # Component unit tests
│   ├── auth/
│   └── tasks/
├── lib/                 # Utility tests
│   └── api/
├── integration/         # Integration tests
│   ├── auth-flow.test.ts
│   └── task-crud.test.ts
└── e2e/                 # E2E tests (Playwright)
    ├── auth.spec.ts
    └── tasks.spec.ts
```

## Debugging

### Enable Debug Logging

Add to `.env.local`:

```env
NEXT_PUBLIC_DEBUG=true
```

### Browser DevTools

1. **Network Tab**: Monitor API requests
2. **Console**: Check for errors and logs
3. **React DevTools**: Inspect component state
4. **Application Tab**: View localStorage

### Common Issues

**Issue**: "Network Error" when calling API

**Solution**:
- Check backend is running: `curl http://localhost:8000/health`
- Verify CORS configuration in backend
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

**Issue**: "401 Unauthorized" on authenticated requests

**Solution**:
- Check JWT token in localStorage
- Verify `BETTER_AUTH_SECRET` matches backend
- Check token expiration (15 minutes)

**Issue**: Form validation not working

**Solution**:
- Check Zod schema is correct
- Verify `zodResolver` is used in `useForm`
- Check field names match schema

## Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized production build in `.next/` directory.

### Environment Variables for Production

Create `.env.production`:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
BETTER_AUTH_SECRET=<production-secret>
NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Deploy to Other Platforms

The application can be deployed to any platform that supports Next.js:
- Netlify
- AWS Amplify
- Google Cloud Run
- Docker container

## Performance Optimization

### Code Splitting

Next.js automatically code-splits by route. For additional splitting:

```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
})
```

### Image Optimization

Use Next.js Image component:

```typescript
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={100}
  priority
/>
```

### Bundle Analysis

```bash
npm run analyze
```

This generates a bundle size report.

## Security Checklist

- [ ] JWT tokens stored in localStorage (not in code)
- [ ] All user input validated with Zod
- [ ] XSS protection via React's JSX escaping
- [ ] Content Security Policy configured
- [ ] HTTPS used in production
- [ ] Secrets not committed to git
- [ ] Dependencies regularly updated
- [ ] Security audit run: `npm audit`

## Resources

### Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Better Auth Docs](https://better-auth.com)
- [React Hook Form Docs](https://react-hook-form.com)
- [Zod Docs](https://zod.dev)

### Backend APIs

- SPEC-1: Task CRUD API (`/specs/001-task-crud/spec.md`)
- SPEC-2: Authentication API (`/specs/002-auth-authorization/spec.md`)
- API Documentation: `http://localhost:8000/docs`

### Project Documentation

- Feature Spec: `specs/003-frontend-integration/spec.md`
- Implementation Plan: `specs/003-frontend-integration/plan.md`
- Research Notes: `specs/003-frontend-integration/research.md`
- Data Model: `specs/003-frontend-integration/data-model.md`

## Getting Help

### Common Commands

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm test             # Run tests
npm run lint         # Run ESLint
npm run format       # Format code with Prettier
npm run type-check   # Run TypeScript compiler
```

### Troubleshooting

If you encounter issues:

1. Check this quickstart guide
2. Review error messages in console
3. Check backend API documentation
4. Review specification documents
5. Ask team for help

## Next Steps

After completing setup:

1. Review the implementation plan: `specs/003-frontend-integration/plan.md`
2. Run `/sp.tasks` to generate detailed task breakdown
3. Start implementation with `/sp.implement`
4. Follow TDD approach: write tests first, then implementation
5. Commit work incrementally after each user story

Happy coding! 🚀
