# Data Model: Todo AI Chatbot Backend

**Feature**: Todo AI Chatbot Backend
**Date**: 2026-02-10
**Perspective**: Backend (SQLModel entities and database schema)

## Overview

This document defines the data structures used in the Todo AI Chatbot Backend. These are SQLModel entities that represent database tables and their relationships. The backend owns these data models and persists them in Neon PostgreSQL.

---

## Core Entities

### Conversation

Represents a chat session between a user and the AI assistant.

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Field Descriptions**:
- `id`: Unique identifier (auto-increment primary key)
- `user_id`: Foreign key to users table (owner of conversation)
- `created_at`: Timestamp when conversation was created
- `updated_at`: Timestamp when conversation was last updated (new message added)

**Validation Rules**:
- `user_id` must reference valid user
- `created_at` and `updated_at` are automatically managed
- `id` is auto-generated on insert

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient user conversation lookups

**Example**:
```python
conversation = Conversation(
    user_id=123,
    created_at=datetime(2026, 2, 10, 10, 0, 0),
    updated_at=datetime(2026, 2, 10, 10, 5, 0)
)
```

---

### Message

Represents a single message in a conversation (user or assistant).

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column=Column(String))
    content: str = Field(max_length=10000)
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

**Field Descriptions**:
- `id`: Unique identifier (auto-increment primary key)
- `conversation_id`: Foreign key to conversations table
- `role`: Message sender (user or assistant)
- `content`: Message text content (max 10,000 chars for long responses)
- `tool_calls`: Optional JSON field storing MCP tool invocations
- `created_at`: Timestamp when message was created

**Validation Rules**:
- `conversation_id` must reference valid conversation
- `role` must be "user" or "assistant"
- `content` must not be empty
- `content` max length: 10,000 characters
- `tool_calls` is optional (only for assistant messages with tool usage)

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for efficient message retrieval
- Index on `created_at` for chronological ordering
- Composite index on `(conversation_id, created_at)` for optimized conversation history queries

**Tool Calls Structure**:
```python
tool_calls = {
    "calls": [
        {
            "tool": "add_task",
            "parameters": {"title": "Buy groceries", "description": "Milk, eggs, bread"},
            "result": "success",
            "error_message": None
        }
    ]
}
```

**Example**:
```python
user_message = Message(
    conversation_id=42,
    role=MessageRole.USER,
    content="Add a task to buy groceries",
    tool_calls=None,
    created_at=datetime(2026, 2, 10, 10, 0, 0)
)

assistant_message = Message(
    conversation_id=42,
    role=MessageRole.ASSISTANT,
    content="I've added the task 'Buy groceries' to your list.",
    tool_calls={
        "calls": [{
            "tool": "add_task",
            "parameters": {"title": "Buy groceries"},
            "result": "success"
        }]
    },
    created_at=datetime(2026, 2, 10, 10, 0, 2)
)
```

---

### Task (Existing from Phase III-A)

Represents a todo item. This model already exists from Phase III-A and is not modified in this feature.

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")  # "pending" or "completed"
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Field Descriptions**:
- `id`: Unique identifier (auto-increment primary key)
- `user_id`: Foreign key to users table (owner of task)
- `title`: Task title (required, max 200 chars)
- `description`: Optional task description (max 1000 chars)
- `status`: Task status ("pending" or "completed")
- `due_date`: Optional due date for task
- `created_at`: Timestamp when task was created
- `updated_at`: Timestamp when task was last modified

**Note**: This model is defined in Phase III-A and is used by MCP tools but not modified in this feature.

---

### User (Existing from Phase II)

Represents an authenticated user. This model already exists from Phase II authentication and is not modified in this feature.

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Note**: This model is defined in Phase II and is referenced by foreign keys but not modified in this feature.

---

## Pydantic Schemas (API Layer)

### ChatRequest

Request schema for chat endpoint.

```python
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = Field(default=None)

    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
```

**Field Descriptions**:
- `message`: User's message text (required, 1-2000 chars)
- `conversation_id`: Optional conversation ID for continuing existing conversation

**Validation**:
- Message must not be empty after stripping whitespace
- Message length: 1-2000 characters
- Conversation_id is optional (null for new conversations)

---

### ChatResponse

Response schema for chat endpoint.

```python
from pydantic import BaseModel
from typing import List, Optional

class ToolCallSchema(BaseModel):
    tool: str
    parameters: dict
    result: str  # "success" or "error"
    error_message: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[ToolCallSchema] = []
```

**Field Descriptions**:
- `conversation_id`: ID of conversation (new or existing)
- `response`: AI assistant's response text
- `tool_calls`: List of MCP tool invocations (may be empty)

---

### ConversationSchema

Schema for conversation metadata.

```python
from pydantic import BaseModel
from datetime import datetime

class ConversationSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

### MessageSchema

Schema for message representation.

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class MessageSchema(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    tool_calls: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## Relationships

```
User (1) ──── (many) Conversation
                      │
                      └──── (many) Message

User (1) ──── (many) Task
```

**Description**:
- One User has many Conversations
- One Conversation has many Messages
- One User has many Tasks
- No direct relationship between Conversation and Task (tasks referenced by ID in tool calls)

---

## Database Indexes

### Primary Keys
- `conversations.id` (auto-increment)
- `messages.id` (auto-increment)
- `tasks.id` (auto-increment, existing)
- `users.id` (auto-increment, existing)

### Foreign Key Indexes
- `conversations.user_id` → `users.id`
- `messages.conversation_id` → `conversations.id`
- `tasks.user_id` → `users.id` (existing)

### Performance Indexes
- `messages(conversation_id, created_at)` - Composite index for efficient conversation history retrieval
- `conversations(user_id)` - Index for user's conversation list
- `messages(created_at)` - Index for chronological ordering

---

## State Transitions

### Conversation Lifecycle

```
[New Request] → Create Conversation → Store User Message → Execute Agent → Store Assistant Message → Update Conversation
                                                                                                              ↓
[Follow-up]  ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

**States**:
1. **New Conversation**: conversation_id is null in request
2. **Active Conversation**: conversation_id provided in request
3. **Conversation History**: All messages persisted in database

### Message Flow

```
User Message → Validate → Store in DB → Load History → Execute Agent → Store Response → Return to Client
```

---

## Data Validation

### Conversation Validation
- User must exist (foreign key constraint)
- Timestamps are automatically managed
- Updated_at refreshed on new message

### Message Validation
- Conversation must exist (foreign key constraint)
- Role must be "user" or "assistant"
- Content must not be empty
- Content max length: 10,000 characters
- Tool_calls must be valid JSON (if provided)

### Task Validation (Existing)
- User must exist (foreign key constraint)
- Title required, max 200 characters
- Status must be "pending" or "completed"
- Due_date must be valid datetime (if provided)

---

## Migration Strategy

### New Tables
- `conversations` - New table for chat sessions
- `messages` - New table for chat messages

### Existing Tables
- `tasks` - No changes (existing from Phase III-A)
- `users` - No changes (existing from Phase II)

### Migration Steps
1. Create `conversations` table with foreign key to `users`
2. Create `messages` table with foreign key to `conversations`
3. Add indexes on `user_id`, `conversation_id`, `created_at`
4. Add composite index on `(conversation_id, created_at)`

### Alembic Migration
```python
# alembic/versions/xxx_add_conversations_messages.py
def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(length=10000), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
```

---

## Query Patterns

### Load Conversation History
```python
# Get last 50 messages for a conversation, ordered chronologically
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(50)
).all()
messages.reverse()  # Oldest first for agent context
```

### Get User's Conversations
```python
# Get all conversations for a user, ordered by most recent
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
).all()
```

### Store New Message
```python
# Create and store a new message
message = Message(
    conversation_id=conversation_id,
    role=MessageRole.USER,
    content=user_message,
    tool_calls=None
)
session.add(message)
session.commit()
session.refresh(message)
```

---

## Notes

### Database Considerations
- JSONB column for tool_calls provides flexibility without complex schema
- Composite index on (conversation_id, created_at) optimizes conversation history queries
- Limiting to 50 messages prevents performance issues with very long conversations
- Foreign key constraints ensure referential integrity

### Future Enhancements
- Add conversation title/summary field
- Add message edit history
- Add message reactions/feedback
- Add conversation archiving
- Add full-text search on message content
- Add conversation sharing between users

---

**Data Model Status**: ✅ COMPLETE - Ready for implementation
