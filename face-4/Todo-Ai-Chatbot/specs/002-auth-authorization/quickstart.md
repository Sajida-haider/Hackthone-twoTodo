# Quickstart Guide: Authentication & Authorization

**Feature**: 002-auth-authorization
**Date**: 2026-02-08
**Purpose**: Get started with implementing and testing the authentication system

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- PostgreSQL database (Neon Serverless recommended)
- SMTP server access (or local mail server for development)
- Git repository cloned

## Environment Setup

### 1. Backend Environment Variables

Create `backend/.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Configuration
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# Email Configuration (Development - MailHog)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@localhost

# Email Configuration (Production - SendGrid example)
# SMTP_HOST=smtp.sendgrid.net
# SMTP_PORT=587
# SMTP_USER=apikey
# SMTP_PASSWORD=your-sendgrid-api-key
# SMTP_FROM=noreply@yourdomain.com

# Verification
VERIFICATION_TOKEN_EXPIRATION_HOURS=24
FRONTEND_URL=http://localhost:3000

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 2. Frontend Environment Variables

Create `frontend/.env.local` file:

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
```

**IMPORTANT**: Use the same `BETTER_AUTH_SECRET` in both backend and frontend!

## Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Email Server (Development)

For local development, use MailHog to capture emails:

```bash
# Install MailHog (macOS)
brew install mailhog

# Install MailHog (Windows - download from GitHub)
# https://github.com/mailhog/MailHog/releases

# Start MailHog
mailhog

# Access web UI at http://localhost:8025
```

## Testing the Authentication Flow

### 1. User Registration

**API Request**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response** (201 Created):
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com"
}
```

**Check Email**: Open MailHog at http://localhost:8025 to see the verification email.

### 2. Email Verification

Copy the verification token from the email link and verify:

```bash
curl -X GET "http://localhost:8000/api/auth/verify-email?token=YOUR_TOKEN_HERE"
```

**Expected Response** (200 OK):
```json
{
  "message": "Email verified successfully. You can now login.",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. User Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com"
  }
}
```

### 4. Access Protected Resource

Use the JWT token to access protected endpoints:

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected Response** (200 OK):
```json
{
  "tasks": []
}
```

### 5. User Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

## Frontend Testing

### 1. Registration Page

Navigate to: http://localhost:3000/register

- Fill in email and password
- Submit form
- Check for success message
- Check MailHog for verification email

### 2. Email Verification

- Click verification link from email
- Should redirect to login page with success message

### 3. Login Page

Navigate to: http://localhost:3000/login

- Enter verified email and password
- Submit form
- Should redirect to dashboard with JWT token stored

### 4. Protected Pages

- Navigate to protected routes (e.g., /tasks)
- Should have access with valid token
- Should redirect to login if token is missing/expired

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_register.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- RegisterForm.test.tsx

# Run in watch mode
npm test -- --watch
```

## Common Issues and Solutions

### Issue: Email not sending

**Solution**: Check SMTP configuration in `.env` file. For development, ensure MailHog is running.

### Issue: JWT token validation fails

**Solution**: Ensure `BETTER_AUTH_SECRET` is identical in both backend and frontend `.env` files.

### Issue: Database connection error

**Solution**: Verify `DATABASE_URL` is correct and database is accessible. Check Neon dashboard for connection string.

### Issue: Account locked after failed logins

**Solution**: Wait 15 minutes or manually reset `failed_login_attempts` and `locked_until` in database:

```sql
UPDATE users
SET failed_login_attempts = 0, locked_until = NULL
WHERE email = 'test@example.com';
```

### Issue: Verification token expired

**Solution**: Request a new verification email:

```bash
curl -X POST http://localhost:8000/api/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b 002-auth-authorization
```

### 2. Implement Backend

- Create models in `backend/app/models/`
- Create schemas in `backend/app/schemas/`
- Create API endpoints in `backend/app/api/v1/`
- Create services in `backend/app/services/`
- Write tests in `backend/tests/`

### 3. Implement Frontend

- Create auth pages in `frontend/src/app/(auth)/`
- Create auth components in `frontend/src/components/auth/`
- Configure Better Auth in `frontend/src/lib/auth/`
- Write tests in `frontend/tests/`

### 4. Test Integration

- Test full authentication flow end-to-end
- Verify JWT token validation works
- Test error scenarios (invalid credentials, expired tokens, etc.)
- Check security audit logs in database

### 5. Code Review

- Verify constitution compliance
- Check test coverage (target: 80%+)
- Review security considerations
- Validate API contracts match implementation

## Security Checklist

- [ ] Passwords hashed with bcrypt (never plaintext)
- [ ] JWT tokens expire in 15 minutes
- [ ] Verification tokens expire in 24 hours
- [ ] Account lockout after 5 failed attempts
- [ ] Generic error messages (no user enumeration)
- [ ] All auth events logged with IP and user agent
- [ ] HTTPS enabled in production
- [ ] Secrets in environment variables (not hardcoded)
- [ ] CORS configured correctly
- [ ] Rate limiting on verification email endpoint

## Next Steps

After authentication is working:

1. Implement Task CRUD endpoints (depends on auth)
2. Add user profile management
3. Implement password reset functionality
4. Add refresh token rotation
5. Consider multi-factor authentication (Phase III)

## Resources

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Better Auth Documentation](https://www.better-auth.com/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)

## Support

For issues or questions:
- Check specification: `specs/002-auth-authorization/spec.md`
- Review implementation plan: `specs/002-auth-authorization/plan.md`
- Check API contracts: `specs/002-auth-authorization/contracts/`
- Review data model: `specs/002-auth-authorization/data-model.md`
