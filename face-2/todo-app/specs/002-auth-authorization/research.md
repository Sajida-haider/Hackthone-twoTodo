# Research: Authentication & Authorization

**Feature**: 002-auth-authorization
**Date**: 2026-02-08
**Purpose**: Resolve technical unknowns and document technology choices

## Research Tasks

### 1. Email Service Provider Selection

**Question**: Which email service should be used for verification emails?

**Options Evaluated**:

1. **SendGrid**
   - Pros: Reliable delivery, good free tier (100 emails/day), easy API, email templates
   - Cons: Requires API key management, external dependency
   - Cost: Free tier sufficient for development/small scale

2. **AWS SES (Simple Email Service)**
   - Pros: Highly scalable, pay-per-use, integrates with AWS ecosystem
   - Cons: Requires AWS account, more complex setup, sandbox mode restrictions
   - Cost: $0.10 per 1,000 emails

3. **Local SMTP (Development)**
   - Pros: No external dependencies, works offline, free
   - Cons: Not suitable for production, emails may go to spam, no delivery guarantees
   - Cost: Free

**Decision**: Use **python-multipart with email-validator** for email validation, and support **configurable SMTP** via environment variables. This allows:
- Development: Local SMTP server (MailHog, Mailtrap) or console logging
- Production: Any SMTP provider (SendGrid, AWS SES, Gmail SMTP, etc.)

**Rationale**:
- Flexibility: Teams can choose their preferred email provider
- No vendor lock-in: Easy to switch providers
- Development-friendly: Can use local SMTP or mock services
- Production-ready: Supports enterprise email services

**Implementation Approach**:
```python
# Environment variables
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<api-key>
SMTP_FROM=noreply@example.com
```

### 2. JWT Token Library Selection

**Question**: Which JWT library should be used for token generation and validation?

**Options Evaluated**:

1. **python-jose[cryptography]**
   - Pros: Pure Python, supports multiple algorithms (HS256, RS256), well-maintained
   - Cons: Slightly slower than PyJWT
   - Used by: FastAPI documentation examples

2. **PyJWT**
   - Pros: Faster, widely used, simple API
   - Cons: Fewer algorithm options out of the box
   - Used by: Many production applications

**Decision**: **python-jose[cryptography]**

**Rationale**:
- Recommended by FastAPI documentation
- Supports both HS256 (shared secret) and RS256 (public/private key)
- Better integration with FastAPI security utilities
- Cryptography backend provides better security

### 3. Password Hashing Algorithm

**Question**: Which password hashing algorithm should be used?

**Options Evaluated**:

1. **bcrypt** (via passlib)
   - Pros: Industry standard, configurable work factor, resistant to GPU attacks
   - Cons: Slower than some alternatives (this is actually a feature)
   - Recommended by: OWASP, security experts

2. **argon2** (via passlib)
   - Pros: Winner of Password Hashing Competition, memory-hard, modern
   - Cons: Less widely adopted, requires additional dependencies
   - Recommended by: Security researchers

3. **scrypt** (via passlib)
   - Pros: Memory-hard, good security properties
   - Cons: Less common than bcrypt, complex parameter tuning

**Decision**: **bcrypt via passlib[bcrypt]**

**Rationale**:
- Industry standard with proven track record
- Widely supported and understood
- Configurable work factor allows future-proofing
- Excellent library support (passlib)
- Recommended by OWASP and FastAPI documentation

**Implementation**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)
verified = pwd_context.verify(plain_password, hashed)
```

### 4. Token Storage Strategy

**Question**: How should JWT tokens be stored on the frontend?

**Options Evaluated**:

1. **localStorage**
   - Pros: Simple, persists across sessions
   - Cons: Vulnerable to XSS attacks, accessible to all scripts
   - Security: Medium risk

2. **sessionStorage**
   - Pros: Cleared on tab close, simple
   - Cons: Vulnerable to XSS, doesn't persist across tabs
   - Security: Medium risk

3. **httpOnly Cookies**
   - Pros: Not accessible to JavaScript (XSS protection), automatic inclusion in requests
   - Cons: Vulnerable to CSRF (requires CSRF tokens), more complex setup
   - Security: Higher security

4. **Better Auth Default (Memory + Refresh Token in httpOnly Cookie)**
   - Pros: Access token in memory (XSS protection), refresh token in httpOnly cookie
   - Cons: Access token lost on page refresh (requires refresh flow)
   - Security: Best practice

**Decision**: **Better Auth Default Strategy**

**Rationale**:
- Access tokens stored in memory (cleared on page refresh)
- Refresh tokens in httpOnly cookies (secure, persistent)
- Automatic token refresh handled by Better Auth
- Follows OAuth 2.0 best practices
- Balances security and user experience

### 5. Account Lockout Implementation

**Question**: How should account lockout be implemented?

**Options Evaluated**:

1. **Database Counter**
   - Track failed_login_attempts and locked_until timestamp in User table
   - Pros: Simple, persistent across server restarts
   - Cons: Database write on every failed attempt

2. **Redis/Cache**
   - Store failed attempts in Redis with TTL
   - Pros: Fast, automatic expiration, reduces database load
   - Cons: Requires Redis, lost on cache clear

3. **Hybrid Approach**
   - Track in database, cache in memory for performance
   - Pros: Persistent and fast
   - Cons: More complex

**Decision**: **Database Counter (Option 1)**

**Rationale**:
- Simpler implementation (no additional infrastructure)
- Persistent across restarts (important for security)
- Database writes are acceptable for failed login attempts (infrequent)
- Aligns with constitution (SQLModel for all data)
- Can optimize later if needed

**Implementation**:
```python
# User model fields
failed_login_attempts: int = 0
locked_until: Optional[datetime] = None

# Lock logic
if user.failed_login_attempts >= 5:
    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
```

### 6. Email Verification Token Generation

**Question**: How should verification tokens be generated?

**Options Evaluated**:

1. **UUID4**
   - Pros: Simple, built-in, sufficient randomness
   - Cons: Predictable format, longer strings

2. **secrets.token_urlsafe()**
   - Pros: Cryptographically secure, URL-safe, configurable length
   - Cons: None significant
   - Recommended by: Python security documentation

3. **JWT with Expiration**
   - Pros: Self-contained, includes expiration
   - Cons: Longer tokens, requires JWT validation

**Decision**: **secrets.token_urlsafe(32)**

**Rationale**:
- Cryptographically secure random generation
- URL-safe (no encoding needed for email links)
- 32 bytes = 256 bits of entropy (highly secure)
- Simple to implement and validate
- Recommended by Python security best practices

**Implementation**:
```python
import secrets
token = secrets.token_urlsafe(32)
```

## Technology Stack Summary

### Backend Dependencies
```
fastapi>=0.104.0
sqlmodel>=0.0.14
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
email-validator>=2.1.0
python-dotenv>=1.0.0
```

### Frontend Dependencies
```
next@16+
better-auth
typescript
tailwindcss
```

### Environment Variables Required
```
# Database
DATABASE_URL=postgresql://user:pass@host/db

# JWT
BETTER_AUTH_SECRET=<secure-random-string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# Email (SMTP)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=username
SMTP_PASSWORD=password
SMTP_FROM=noreply@example.com

# Verification
VERIFICATION_TOKEN_EXPIRATION_HOURS=24
FRONTEND_URL=http://localhost:3000
```

## Best Practices Applied

1. **Security**
   - bcrypt for password hashing (industry standard)
   - secrets module for token generation (cryptographically secure)
   - JWT with expiration claims (time-limited access)
   - Generic error messages (prevent user enumeration)

2. **Performance**
   - Database indexes on user_id, email, token fields
   - Token validation caching (if needed)
   - Async/await for I/O operations

3. **Maintainability**
   - Environment variables for configuration
   - Centralized security utilities
   - Clear separation of concerns (models, services, API)

4. **Testing**
   - Mock email service for tests
   - Test fixtures for users and tokens
   - Integration tests for full auth flows

## Alternatives Considered and Rejected

1. **OAuth 2.0 Social Login** - Out of scope for Phase II
2. **Multi-factor Authentication** - Out of scope for Phase II
3. **Password Reset** - Out of scope for Phase II
4. **Redis for Session Storage** - Unnecessary complexity for Phase II
5. **Refresh Token Rotation** - Better Auth handles this automatically

## Open Questions

None - all technical unknowns resolved.

## References

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Better Auth Documentation](https://www.better-auth.com/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Python secrets Module](https://docs.python.org/3/library/secrets.html)
