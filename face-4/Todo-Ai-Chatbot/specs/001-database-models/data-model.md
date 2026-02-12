# Data Model: Database & Models

**Feature**: Database & Models (001-database-models)
**Date**: 2026-02-09
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the complete data model for Phase III AI Chatbot, including three core entities: Task, Conversation, and Message. All entities support user isolation, automatic timestamps, and referential integrity.

---

## Entity Definitions

### Task

**Purpose**: Represents a user's todo item with title, description, completion status, and timestamps.

**Table Name**: `task`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| user_id | String | NOT NULL, INDEXED | Owner user identifier (from JWT) |
| title | String(500) | NOT NULL | Task title |
| description | Text | NULLABLE | Optional task description (max 5000 chars) |
| completed | Boolean | NOT NULL, DEFAULT FALSE | Task completion status |
| created_at | DateTime | NOT NULL, DEFAULT UTC NOW | Creation timestamp (UTC) |
| updated_at | DateTime | NOT NULL, DEFAULT UTC NOW, ON UPDATE UTC NOW | Last modification timestamp (UTC) |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for user-specific queries)
- INDEX on `completed` (for filtering by status)
- COMPOSITE INDEX on `(user_id, completed)` (for filtered user queries)

**Validation Rules**:
- `title` must not be empty
- `title` max length: 500 characters
- `description` max length: 5000 characters
- `user_id` must be valid string (validated by application)
- `completed` defaults to `false` on creation

**Business Rules**:
- Users can only access their own tasks (enforced by `user_id` filtering)
- Deletion is permanent (hard delete)
- `updated_at` automatically updates on any field change

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False
    )
```

---

### Conversation

**Purpose**: Represents a chat session between a user and the AI assistant. Contains metadata about when the conversation started and was last updated.

**Table Name**: `conversation`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique conversation identifier |
| user_id | String | NOT NULL, INDEXED | Owner user identifier (from JWT) |
| created_at | DateTime | NOT NULL, DEFAULT UTC NOW | Creation timestamp (UTC) |
| updated_at | DateTime | NOT NULL, DEFAULT UTC NOW, ON UPDATE UTC NOW | Last modification timestamp (UTC) |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for user-specific queries)
- INDEX on `updated_at` (for sorting by recent activity)

**Relationships**:
- ONE-TO-MANY with Message (one conversation has many messages)
- CASCADE DELETE: Deleting a conversation deletes all its messages

**Validation Rules**:
- `user_id` must be valid string (validated by application)
- Conversation must have at least one message to be meaningful (enforced by application logic)

**Business Rules**:
- Users can only access their own conversations (enforced by `user_id` filtering)
- Deletion is permanent and cascades to all messages (hard delete)
- `updated_at` automatically updates when new messages are added
- Empty conversations (no messages) are allowed but may be cleaned up by background jobs

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False
    )

    # Relationship
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

---

### Message

**Purpose**: Represents a single message within a conversation, sent by either the user or the AI assistant. Contains the message content, sender role, and timestamp.

**Table Name**: `message`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| user_id | String | NOT NULL, INDEXED | Owner user identifier (from JWT) |
| conversation_id | Integer | FOREIGN KEY (conversation.id), NOT NULL, INDEXED, ON DELETE CASCADE | Parent conversation identifier |
| role | String(20) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender role |
| content | Text | NOT NULL | Message content (max 10000 chars) |
| created_at | DateTime | NOT NULL, DEFAULT UTC NOW | Creation timestamp (UTC) |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for user-specific queries)
- INDEX on `conversation_id` (for retrieving conversation messages)
- INDEX on `created_at` (for chronological ordering)
- COMPOSITE INDEX on `(conversation_id, created_at)` (for ordered conversation messages)

**Relationships**:
- MANY-TO-ONE with Conversation (many messages belong to one conversation)
- CASCADE DELETE: Deleting parent conversation deletes all messages

**Validation Rules**:
- `role` must be either "user" or "assistant"
- `content` must not be empty
- `content` max length: 10000 characters
- `user_id` must match conversation's `user_id` (enforced by application)
- `conversation_id` must reference existing conversation

**Business Rules**:
- Users can only access their own messages (enforced by `user_id` filtering)
- Messages are immutable once created (no updates allowed)
- Deletion only via parent conversation deletion (cascade)
- Messages are ordered by `created_at` within a conversation
- `role` determines message display (user messages vs assistant responses)

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    conversation_id: int = Field(foreign_key="conversation.id", index=True, nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(max_length=10000, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

## Entity Relationships

### Relationship Diagram

```
User (external, from auth system)
  |
  +-- 1:N --> Task
  |
  +-- 1:N --> Conversation
  |              |
  |              +-- 1:N --> Message
  |
  +-- 1:N --> Message (direct relationship for user isolation)
```

### Relationship Details

**User → Task (One-to-Many)**
- One user can have many tasks
- Tasks are isolated by `user_id`
- No foreign key constraint (user managed by auth system)

**User → Conversation (One-to-Many)**
- One user can have many conversations
- Conversations are isolated by `user_id`
- No foreign key constraint (user managed by auth system)

**Conversation → Message (One-to-Many, Cascade Delete)**
- One conversation contains many messages
- Foreign key: `message.conversation_id` → `conversation.id`
- Cascade delete: Deleting conversation deletes all messages
- Orphan prevention: Messages cannot exist without conversation

**User → Message (One-to-Many)**
- One user can have many messages across all conversations
- Messages are isolated by `user_id`
- No foreign key constraint (user managed by auth system)
- Used for user isolation queries

---

## Data Integrity Constraints

### Referential Integrity

1. **Message → Conversation**:
   - Foreign key constraint ensures messages reference valid conversations
   - Cascade delete ensures no orphaned messages
   - Database enforces referential integrity

2. **User Isolation**:
   - Application-level constraint: `message.user_id` must match `conversation.user_id`
   - Enforced in application code before insert
   - Prevents cross-user data leakage

### Data Validation

1. **Required Fields**:
   - All entities: `user_id`, `created_at`
   - Task: `title`, `completed`
   - Message: `conversation_id`, `role`, `content`

2. **Field Constraints**:
   - String lengths enforced at database level
   - Enum values enforced for `message.role`
   - Boolean defaults enforced for `task.completed`

3. **Timestamp Consistency**:
   - All timestamps in UTC
   - `created_at` immutable after creation
   - `updated_at` automatically maintained

---

## Query Patterns

### Common Queries

**Get User's Tasks**:
```sql
SELECT * FROM task
WHERE user_id = ?
ORDER BY created_at DESC;
```

**Get User's Conversations**:
```sql
SELECT * FROM conversation
WHERE user_id = ?
ORDER BY updated_at DESC;
```

**Get Conversation Messages**:
```sql
SELECT * FROM message
WHERE conversation_id = ? AND user_id = ?
ORDER BY created_at ASC;
```

**Get Incomplete Tasks**:
```sql
SELECT * FROM task
WHERE user_id = ? AND completed = false
ORDER BY created_at DESC;
```

### Performance Considerations

- All user-specific queries use indexed `user_id` column
- Conversation message retrieval uses composite index `(conversation_id, created_at)`
- Task filtering by completion status uses composite index `(user_id, completed)`
- Expected query performance: < 200ms for 95% of requests

---

## Migration Strategy

### Initial Schema Creation

1. Create `task` table
2. Create `conversation` table
3. Create `message` table with foreign key to `conversation`
4. Create all indexes

### Migration Order

```
1. task (no dependencies)
2. conversation (no dependencies)
3. message (depends on conversation)
```

### Rollback Strategy

Reverse order:
```
1. Drop message table
2. Drop conversation table
3. Drop task table
```

---

## Summary

This data model provides:
- ✅ User isolation via `user_id` filtering
- ✅ Referential integrity via foreign keys and cascade deletion
- ✅ Automatic timestamp management
- ✅ Efficient querying via strategic indexes
- ✅ Data validation at database and application levels
- ✅ Clear entity relationships and business rules

**Ready for**: Implementation and migration generation
