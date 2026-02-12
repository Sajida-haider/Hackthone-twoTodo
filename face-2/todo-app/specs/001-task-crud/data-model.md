# Data Model: Task CRUD

**Feature**: Task CRUD (001-task-crud)
**Date**: 2026-02-08
**Phase**: Phase 1 - Design

## Overview

This document defines the data model for the Task CRUD feature, including entity definitions, relationships, validation rules, and database schema.

---

## Entities

### Task Entity

**Purpose**: Represents a todo item that belongs to a user.

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | Primary Key, Not Null | Unique identifier for the task |
| user_id | UUID | Foreign Key (users.id), Not Null, Indexed | Owner of the task |
| title | String | Not Null, Length: 1-200 chars | Task title |
| description | String | Nullable, Max Length: 2000 chars | Optional task description |
| status | Enum | Not Null, Values: "pending" \| "completed", Default: "pending" | Task completion status |
| due_date | DateTime | Nullable, Timezone: UTC | Optional due date |
| created_at | DateTime | Not Null, Default: UTC now | Creation timestamp |
| updated_at | DateTime | Not Null, Default: UTC now, Auto-update | Last modification timestamp |

**Validation Rules**:
- `title`: Must not be empty, must be 1-200 characters
- `description`: If provided, must be 0-2000 characters
- `status`: Must be exactly "pending" or "completed"
- `due_date`: If provided, must be valid ISO 8601 datetime
- `user_id`: Must reference an existing user

**Indexes**:
- Primary index on `id` (automatic)
- Index on `user_id` (for filtering by owner)
- Index on `status` (for filtering by completion status)
- Composite index on `(user_id, created_at DESC)` (for sorted user task lists)

---

### User Entity (Reference Only)

**Purpose**: Represents an authenticated user. Defined in authentication feature, referenced here.

**Attributes** (relevant to Task CRUD):

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | Primary Key, Not Null | Unique identifier for the user |

**Note**: Full user entity definition is out of scope for this feature. Task CRUD only references user by ID.

---

## Relationships

### User → Tasks (One-to-Many)

- **Cardinality**: One User has Many Tasks
- **Foreign Key**: `task.user_id` → `user.id`
- **Cascade**: ON DELETE CASCADE (when user is deleted, all their tasks are deleted)
- **Referential Integrity**: Enforced at database level

**SQLModel Representation**:
```python
class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    user: User = Relationship(back_populates="tasks")
```

---

## Database Schema (PostgreSQL)

### Tasks Table

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL CHECK (length(title) >= 1),
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Trigger for automatic updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Pydantic Schemas

### TaskCreate (Request Schema)

Used when creating a new task.

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
```

**Validation**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 2000 characters
- `due_date`: Optional, valid datetime

---

### TaskUpdate (Request Schema)

Used when updating an existing task.

```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, pattern="^(pending|completed)$")
    due_date: Optional[datetime] = None
```

**Validation**:
- All fields optional (partial update)
- `title`: If provided, 1-200 characters
- `description`: If provided, max 2000 characters
- `status`: If provided, must be "pending" or "completed"
- `due_date`: If provided, valid datetime

---

### TaskRead (Response Schema)

Used when returning task data to client.

```python
class TaskRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows creation from ORM models
```

**Note**: Includes all task fields for complete representation.

---

## State Transitions

### Task Status State Machine

```
┌─────────┐
│ pending │ ◄──┐
└────┬────┘    │
     │         │
     │ update  │ update
     │ status  │ status
     │         │
     ▼         │
┌───────────┐ │
│ completed ├─┘
└───────────┘
```

**Valid Transitions**:
- `pending` → `completed`: User marks task as done
- `completed` → `pending`: User reopens task
- `pending` → `pending`: No change (idempotent)
- `completed` → `completed`: No change (idempotent)

**Business Rules**:
- Any authenticated user can change status of their own tasks
- Status changes are immediate (no approval workflow)
- Status changes update the `updated_at` timestamp

---

## Data Integrity Rules

### Referential Integrity
- `task.user_id` MUST reference an existing `user.id`
- Enforced by foreign key constraint
- Cascade delete: When user is deleted, all their tasks are deleted

### Data Validation
- Performed at multiple layers:
  1. **Pydantic Schema**: Validates request data before processing
  2. **SQLModel Field**: Validates data before database insertion
  3. **Database Constraints**: Final validation at storage layer

### Concurrency
- **Optimistic Locking**: Not implemented in MVP (single-user operations)
- **Last Write Wins**: If concurrent updates occur, last update prevails
- **Timestamp Tracking**: `updated_at` reflects last modification time

---

## Query Patterns

### Common Queries

**1. Get all tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1
ORDER BY created_at DESC;
```

**2. Get single task by ID (with ownership check)**:
```sql
SELECT * FROM tasks
WHERE id = $1 AND user_id = $2;
```

**3. Get pending tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND status = 'pending'
ORDER BY created_at DESC;
```

**4. Get completed tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND status = 'completed'
ORDER BY created_at DESC;
```

**5. Get overdue tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND status = 'pending'
  AND due_date < NOW()
ORDER BY due_date ASC;
```

---

## Performance Considerations

### Index Strategy
- **Primary Key (id)**: Automatic B-tree index for fast lookups
- **Foreign Key (user_id)**: Index for efficient user-based filtering
- **Status**: Index for filtering by completion status
- **Composite (user_id, created_at)**: Optimizes sorted user task lists

### Query Optimization
- All queries filter by `user_id` first (indexed)
- Use `LIMIT` for pagination (future enhancement)
- Avoid N+1 queries by using joins when fetching related data

### Scalability
- UUID primary keys support distributed systems
- Indexes support up to millions of tasks per user
- No full table scans (all queries use indexes)

---

## Migration Strategy

### Initial Migration

```python
# alembic/versions/001_create_tasks_table.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("length(title) >= 1", name='check_title_not_empty'),
        sa.CheckConstraint("status IN ('pending', 'completed')", name='check_valid_status')
    )

    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_user_created', 'tasks', ['user_id', 'created_at'])

def downgrade():
    op.drop_table('tasks')
```

---

## Data Model Validation

✅ **Completeness**: All attributes from spec.md are included
✅ **Constraints**: All validation rules from spec.md are enforced
✅ **Relationships**: User-Task relationship properly defined
✅ **Indexes**: Performance-critical queries are indexed
✅ **Security**: User isolation enforced at query level
✅ **Scalability**: UUID keys support distributed systems
✅ **Maintainability**: Clear schema with proper constraints

**Status**: Data model design complete and ready for implementation.
