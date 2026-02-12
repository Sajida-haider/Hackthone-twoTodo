# Data Model: Authentication & Authorization

**Feature**: 002-auth-authorization
**Date**: 2026-02-08
**Purpose**: Define database schema and entity relationships

## Entity Definitions

### 1. User

Represents a registered user account with authentication credentials and status.

**Table Name**: `users`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (login identifier) |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password (never store plaintext) |
| is_verified | BOOLEAN | NOT NULL, DEFAULT FALSE | Email verification status |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Account active status |
| failed_login_attempts | INTEGER | NOT NULL, DEFAULT 0 | Counter for failed login attempts |
| locked_until | TIMESTAMP | NULL | Account lock expiration timestamp (NULL if not locked) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| last_login_at | TIMESTAMP | NULL | Last successful login timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`
- INDEX on `is_verified` (for filtering unverified accounts)
- INDEX on `locked_until` (for checking locked accounts)

**Validation Rules**:
- Email must conform to RFC 5322 format
- Password must be hashed with bcrypt before storage
- failed_login_attempts resets to 0 on successful login
- locked_until is set to NOW() + 15 minutes when failed_login_attempts >= 5

**State Transitions**:
```
[Registered] → is_verified=FALSE, is_active=TRUE
    ↓ (email verification)
[Verified] → is_verified=TRUE, is_active=TRUE
    ↓ (5 failed logins)
[Locked] → locked_until=NOW()+15min
    ↓ (time expires)
[Unlocked] → locked_until=NULL, failed_login_attempts=0
```

### 2. Verification Token

Represents an email verification token with expiration.

**Table Name**: `verification_tokens`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique token identifier |
| user_id | UUID | FOREIGN KEY → users(id), NOT NULL | Associated user |
| token | VARCHAR(255) | UNIQUE, NOT NULL | URL-safe verification token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration timestamp (24 hours from creation) |
| verified_at | TIMESTAMP | NULL | Timestamp when token was used (NULL if unused) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Token creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `token`
- INDEX on `user_id` (for user lookup)
- INDEX on `expires_at` (for cleanup queries)

**Validation Rules**:
- Token generated using secrets.token_urlsafe(32)
- expires_at = created_at + 24 hours
- Token is single-use (verified_at set on first use)
- Expired tokens (expires_at < NOW()) are invalid

**Relationships**:
- FOREIGN KEY: user_id → users.id (ON DELETE CASCADE)

**State Transitions**:
```
[Created] → verified_at=NULL, expires_at=created_at+24h
    ↓ (user clicks link)
[Verified] → verified_at=NOW()
    ↓ (24 hours pass)
[Expired] → expires_at < NOW()
```

### 3. Authentication Event

Represents a security audit log entry for authentication events.

**Table Name**: `auth_events`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique event identifier |
| user_id | UUID | FOREIGN KEY → users(id), NULL | Associated user (NULL for failed registration) |
| event_type | VARCHAR(50) | NOT NULL | Event type (see enum below) |
| ip_address | VARCHAR(45) | NULL | Client IP address (IPv4 or IPv6) |
| user_agent | VARCHAR(500) | NULL | Client user agent string |
| success | BOOLEAN | NOT NULL | Event outcome (TRUE=success, FALSE=failure) |
| failure_reason | VARCHAR(255) | NULL | Reason for failure (if success=FALSE) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Event timestamp |

**Event Types** (enum):
- `registration` - User account creation
- `email_verification` - Email verification attempt
- `login` - Login attempt
- `logout` - User logout
- `failed_login` - Failed login attempt
- `account_locked` - Account locked due to failed attempts
- `token_validation` - JWT token validation (optional, high volume)

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for user audit trail)
- INDEX on `event_type` (for filtering by event)
- INDEX on `created_at` (for time-based queries)
- COMPOSITE INDEX on `(user_id, created_at)` (for user timeline)

**Validation Rules**:
- event_type must be one of the defined enum values
- failure_reason required when success=FALSE
- ip_address stored for security auditing

**Relationships**:
- FOREIGN KEY: user_id → users.id (ON DELETE SET NULL)

## Entity Relationships

```
┌─────────────────┐
│     User        │
│  (users)        │
│─────────────────│
│ id (PK)         │
│ email (UNIQUE)  │
│ password_hash   │
│ is_verified     │
│ is_active       │
│ failed_login... │
│ locked_until    │
│ created_at      │
│ updated_at      │
│ last_login_at   │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────┐
    │                          │
    ▼                          ▼
┌─────────────────┐    ┌─────────────────┐
│ VerificationToken│    │  AuthEvent      │
│ (verification_  │    │  (auth_events)  │
│  tokens)        │    │─────────────────│
│─────────────────│    │ id (PK)         │
│ id (PK)         │    │ user_id (FK)    │
│ user_id (FK)    │    │ event_type      │
│ token (UNIQUE)  │    │ ip_address      │
│ expires_at      │    │ user_agent      │
│ verified_at     │    │ success         │
│ created_at      │    │ failure_reason  │
└─────────────────┘    │ created_at      │
                       └─────────────────┘
```

## SQLModel Implementation Notes

### User Model
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    is_verified: bool = Field(default=False, index=True)
    is_active: bool = Field(default=True)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
```

### Verification Token Model
```python
class VerificationToken(SQLModel, table=True):
    __tablename__ = "verification_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    token: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime = Field(index=True)
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Authentication Event Model
```python
class AuthEvent(SQLModel, table=True):
    __tablename__ = "auth_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id", index=True, default=None)
    event_type: str = Field(max_length=50, index=True)
    ip_address: Optional[str] = Field(max_length=45, default=None)
    user_agent: Optional[str] = Field(max_length=500, default=None)
    success: bool
    failure_reason: Optional[str] = Field(max_length=255, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

## Database Migrations

### Initial Migration (Alembic)

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_verified ON users(is_verified);
CREATE INDEX idx_users_locked_until ON users(locked_until);

-- Create verification_tokens table
CREATE TABLE verification_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_verification_tokens_user_id ON verification_tokens(user_id);
CREATE INDEX idx_verification_tokens_token ON verification_tokens(token);
CREATE INDEX idx_verification_tokens_expires_at ON verification_tokens(expires_at);

-- Create auth_events table
CREATE TABLE auth_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(500) NULL,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_auth_events_user_id ON auth_events(user_id);
CREATE INDEX idx_auth_events_event_type ON auth_events(event_type);
CREATE INDEX idx_auth_events_created_at ON auth_events(created_at);
CREATE INDEX idx_auth_events_user_created ON auth_events(user_id, created_at);
```

## Data Integrity Rules

1. **Email Uniqueness**: Enforced at database level with UNIQUE constraint
2. **Password Security**: Never store plaintext passwords, always hash with bcrypt
3. **Token Expiration**: Verification tokens expire after 24 hours
4. **Account Lockout**: Automatically lock after 5 failed attempts for 15 minutes
5. **Cascade Deletion**: Verification tokens deleted when user is deleted
6. **Audit Trail**: Auth events preserved even if user is deleted (SET NULL)

## Performance Considerations

1. **Indexes**: All foreign keys and frequently queried fields are indexed
2. **Token Cleanup**: Periodic job to delete expired verification tokens
3. **Event Archival**: Consider archiving old auth_events (>90 days) to separate table
4. **Query Optimization**: Use composite indexes for common query patterns

## Security Considerations

1. **Password Storage**: bcrypt with configurable work factor (default: 12 rounds)
2. **Token Generation**: Cryptographically secure random tokens (secrets module)
3. **Audit Logging**: All authentication events logged with IP and user agent
4. **Account Lockout**: Prevents brute force attacks
5. **Token Expiration**: Time-limited tokens reduce exposure window
