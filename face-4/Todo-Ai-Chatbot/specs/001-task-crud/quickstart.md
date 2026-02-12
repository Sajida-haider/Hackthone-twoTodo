# Quickstart Guide: Task CRUD

**Feature**: Task CRUD (001-task-crud)
**Date**: 2026-02-08
**Audience**: Developers implementing or testing the Task CRUD feature

## Overview

This guide provides step-by-step instructions for setting up, running, and testing the Task CRUD feature locally.

---

## Prerequisites

### Required Software
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 15 or higher (or Neon account)
- **Git**: For version control

### Required Accounts
- **Neon Account**: For PostgreSQL database (https://neon.tech)
- **Better Auth Setup**: For authentication (configured separately)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd todo-app
git checkout 001-task-crud
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment Variables

Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@host/database

# JWT Secret (must match frontend)
BETTER_AUTH_SECRET=your-secret-key-here

# Environment
ENVIRONMENT=development
```

**Important**: Use the same `BETTER_AUTH_SECRET` value in both frontend and backend.

#### Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Create tasks table"

# Apply migrations
alembic upgrade head
```

#### Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create `frontend/.env.local` file:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Secret (must match backend)
BETTER_AUTH_SECRET=your-secret-key-here

# Environment
NODE_ENV=development
```

#### Start Frontend Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## Database Setup

### Option 1: Neon PostgreSQL (Recommended)

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string
4. Add to `backend/.env` as `DATABASE_URL`

### Option 2: Local PostgreSQL

```bash
# Create database
createdb todo_app

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://localhost/todo_app
```

### Verify Database Connection

```bash
cd backend
python -c "from app.database import engine; print('Connected!' if engine else 'Failed')"
```

---

## Testing the Feature

### 1. Authentication Setup

Before testing Task CRUD, ensure you have:
- User account created (via authentication feature)
- Valid JWT token (obtained via login)

### 2. Manual API Testing

#### Using cURL

**Create Task**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2026-02-15T10:00:00Z"
  }'
```

**List Tasks**:
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Get Single Task**:
```bash
curl -X GET http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Update Task**:
```bash
curl -X PATCH http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

**Delete Task**:
```bash
curl -X DELETE http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" button
3. Enter JWT token: `Bearer YOUR_JWT_TOKEN`
4. Test endpoints interactively

### 3. Frontend Testing

1. Navigate to `http://localhost:3000`
2. Log in with test user credentials
3. Navigate to tasks page
4. Test CRUD operations:
   - Create new task
   - View task list
   - Update task details
   - Mark task as completed
   - Delete task

### 4. Automated Testing

#### Backend Tests

```bash
cd backend
pytest tests/ -v

# Run specific test file
pytest tests/test_task_crud.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

#### Frontend Tests

```bash
cd frontend
npm test

# Run specific test
npm test -- TaskList.test.tsx

# Run with coverage
npm test -- --coverage
```

---

## Verification Checklist

Use this checklist to verify the feature is working correctly:

### Backend Verification
- [ ] Backend server starts without errors
- [ ] Database connection successful
- [ ] Migrations applied successfully
- [ ] Swagger UI accessible at /docs
- [ ] All 5 endpoints visible in Swagger UI

### API Verification
- [ ] POST /api/tasks creates task with valid token
- [ ] POST /api/tasks returns 401 without token
- [ ] GET /api/tasks returns user's tasks only
- [ ] GET /api/tasks/{id} returns 404 for other user's task
- [ ] PATCH /api/tasks/{id} updates task successfully
- [ ] PATCH /api/tasks/{id} validates input (empty title rejected)
- [ ] DELETE /api/tasks/{id} removes task permanently

### Frontend Verification
- [ ] Frontend server starts without errors
- [ ] Login redirects to tasks page
- [ ] Task list displays user's tasks
- [ ] Create task form works
- [ ] Task update form works
- [ ] Delete button removes task
- [ ] Completion toggle works
- [ ] Responsive design works on mobile

### Security Verification
- [ ] JWT token required for all endpoints
- [ ] User can only see their own tasks
- [ ] User cannot access other users' tasks
- [ ] Invalid tokens return 401
- [ ] Expired tokens return 401

---

## Common Issues & Solutions

### Issue: Database Connection Failed

**Symptoms**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions**:
1. Verify DATABASE_URL is correct
2. Check PostgreSQL is running
3. Verify network connectivity to Neon
4. Check firewall settings

### Issue: JWT Token Invalid

**Symptoms**: `401 Unauthorized` on all requests

**Solutions**:
1. Verify BETTER_AUTH_SECRET matches in frontend and backend
2. Check token format: `Bearer <token>`
3. Verify token hasn't expired
4. Check token is being sent in Authorization header

### Issue: CORS Errors

**Symptoms**: `Access-Control-Allow-Origin` errors in browser console

**Solutions**:
1. Add CORS middleware to FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Port Already in Use

**Symptoms**: `Address already in use` error

**Solutions**:
```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill process
# Windows
taskkill /PID <pid> /F

# Linux/Mac
kill -9 <pid>
```

---

## Development Workflow

### Making Changes

1. **Update Specification**: Modify `specs/001-task-crud/spec.md` if requirements change
2. **Update Plan**: Modify `specs/001-task-crud/plan.md` if architecture changes
3. **Update Data Model**: Modify `specs/001-task-crud/data-model.md` if schema changes
4. **Create Migration**: Generate Alembic migration for schema changes
5. **Update Code**: Implement changes in backend/frontend
6. **Update Tests**: Add/modify tests for new functionality
7. **Run Tests**: Verify all tests pass
8. **Update Documentation**: Update this quickstart if setup changes

### Running in Production

**Backend**:
```bash
# Use production WSGI server
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend**:
```bash
# Build for production
npm run build

# Start production server
npm start
```

**Environment Variables**:
- Use production DATABASE_URL (Neon production database)
- Use strong BETTER_AUTH_SECRET (32+ random characters)
- Set ENVIRONMENT=production
- Enable HTTPS in production

---

## Next Steps

After completing this quickstart:

1. **Implement Tasks**: Run `/sp.tasks` to generate implementation tasks
2. **Execute Implementation**: Follow tasks in priority order (P1 → P2 → P3)
3. **Run Tests**: Ensure all tests pass
4. **Deploy**: Follow deployment guide for production deployment

---

## Support

### Documentation
- Feature Specification: `specs/001-task-crud/spec.md`
- Implementation Plan: `specs/001-task-crud/plan.md`
- Data Model: `specs/001-task-crud/data-model.md`
- API Contracts: `specs/001-task-crud/contracts/`

### Troubleshooting
- Check backend logs: `backend/logs/`
- Check frontend console: Browser DevTools
- Review test output: `pytest -v` or `npm test`

### Getting Help
- Review constitution: `.specify/memory/constitution.md`
- Check PHRs: `history/prompts/001-task-crud/`
- Consult team members or documentation
