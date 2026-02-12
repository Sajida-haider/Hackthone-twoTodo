# Quickstart: Database & Models

**Feature**: Database & Models (001-database-models)
**Date**: 2026-02-09
**Phase**: Phase 1 - Design & Contracts

## Overview

This guide provides step-by-step instructions for setting up and using the database models for Phase III AI Chatbot.

---

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Neon Serverless or local)
- pip package manager
- Virtual environment (recommended)

---

## Installation

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install sqlmodel==0.0.14
pip install psycopg2-binary==2.9.9
pip install alembic==1.13.1
pip install python-dotenv==1.0.0
```

Or use requirements.txt:

```bash
pip install -r backend/requirements.txt
```

### 3. Configure Database Connection

Create a `.env` file in the backend directory:

```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/database_name

# For Neon PostgreSQL:
# DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Important**: Never commit `.env` files to version control!

---

## Database Setup

### 1. Initialize Alembic

```bash
cd backend
alembic init alembic
```

### 2. Configure Alembic

Edit `alembic/env.py` to import models:

```python
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata
```

Edit `alembic.ini` to use environment variable:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
# This will be overridden by env.py using DATABASE_URL
```

### 3. Create Initial Migration

```bash
# Generate migration from models
alembic revision --autogenerate -m "Initial schema: task, conversation, message"

# Review the generated migration in alembic/versions/
```

### 4. Apply Migration

```bash
# Apply all migrations
alembic upgrade head

# Verify tables were created
psql $DATABASE_URL -c "\dt"
```

---

## Usage Examples

### Basic Setup

```python
from sqlmodel import create_engine, Session, select
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
import os

# Create engine
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, echo=True)

# Create session
session = Session(engine)
```

### Create a Task

```python
# Create new task
task = Task(
    user_id="user_abc123",
    title="Buy groceries",
    description="Milk, eggs, bread"
)

# Add to session and commit
session.add(task)
session.commit()
session.refresh(task)

print(f"Created task with ID: {task.id}")
```

### Query User's Tasks

```python
# Get all tasks for a user
statement = select(Task).where(Task.user_id == "user_abc123")
tasks = session.exec(statement).all()

for task in tasks:
    print(f"Task: {task.title} - Completed: {task.completed}")
```

### Filter Tasks by Status

```python
# Get incomplete tasks
statement = select(Task).where(
    Task.user_id == "user_abc123",
    Task.completed == False
)
incomplete_tasks = session.exec(statement).all()

print(f"You have {len(incomplete_tasks)} incomplete tasks")
```

### Update a Task

```python
# Get task by ID
task = session.get(Task, task_id)

if task and task.user_id == "user_abc123":
    # Update fields
    task.completed = True

    # Commit changes (updated_at automatically updated)
    session.commit()
    session.refresh(task)

    print(f"Task completed at: {task.updated_at}")
```

### Delete a Task

```python
# Get task by ID
task = session.get(Task, task_id)

if task and task.user_id == "user_abc123":
    # Delete task
    session.delete(task)
    session.commit()

    print("Task deleted successfully")
```

### Create Conversation with Messages

```python
# Create conversation
conversation = Conversation(user_id="user_abc123")
session.add(conversation)
session.commit()
session.refresh(conversation)

# Add user message
user_message = Message(
    user_id="user_abc123",
    conversation_id=conversation.id,
    role="user",
    content="Hello! Can you help me with my tasks?"
)
session.add(user_message)
session.commit()

# Add assistant response
assistant_message = Message(
    user_id="user_abc123",
    conversation_id=conversation.id,
    role="assistant",
    content="Of course! I'd be happy to help you manage your tasks."
)
session.add(assistant_message)
session.commit()

print(f"Conversation {conversation.id} has {len(conversation.messages)} messages")
```

### Retrieve Conversation History

```python
# Get conversation with messages
conversation = session.get(Conversation, conversation_id)

if conversation and conversation.user_id == "user_abc123":
    # Messages are ordered by created_at
    for message in conversation.messages:
        print(f"[{message.role}]: {message.content}")
```

### Delete Conversation (Cascade Delete Messages)

```python
# Get conversation
conversation = session.get(Conversation, conversation_id)

if conversation and conversation.user_id == "user_abc123":
    # Delete conversation (messages automatically deleted via cascade)
    session.delete(conversation)
    session.commit()

    print("Conversation and all messages deleted")
```

---

## Context Manager Pattern (Recommended)

```python
from contextlib import contextmanager

@contextmanager
def get_db_session():
    """Context manager for database sessions with automatic commit/rollback."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage
with get_db_session() as session:
    task = Task(user_id="user_abc123", title="New Task")
    session.add(task)
    # Automatically commits on success, rolls back on error
```

---

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/unit/test_models.py -v

# Run specific test
pytest tests/unit/test_models.py::test_create_task -v
```

### Run Integration Tests

```bash
# Run integration tests (requires test database)
pytest tests/integration/test_database.py -v
```

### Test Coverage

```bash
# Run tests with coverage
pytest --cov=app/models tests/

# Generate HTML coverage report
pytest --cov=app/models --cov-report=html tests/
```

---

## Migration Commands

### Create New Migration

```bash
# After modifying models, generate migration
alembic revision --autogenerate -m "Add priority field to tasks"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>
```

### Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### View Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

---

## Common Issues and Solutions

### Issue: Connection Refused

**Problem**: Cannot connect to database

**Solution**:
```bash
# Verify DATABASE_URL is set
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check if database exists
psql $DATABASE_URL -c "\l"
```

### Issue: Migration Conflicts

**Problem**: Alembic detects conflicting changes

**Solution**:
```bash
# Resolve conflicts manually in migration file
# Then apply migration
alembic upgrade head

# Or create new migration
alembic revision --autogenerate -m "Resolve conflicts"
```

### Issue: Orphaned Messages

**Problem**: Messages exist without parent conversation

**Solution**:
```sql
-- Find orphaned messages
SELECT * FROM message
WHERE conversation_id NOT IN (SELECT id FROM conversation);

-- Delete orphaned messages
DELETE FROM message
WHERE conversation_id NOT IN (SELECT id FROM conversation);
```

### Issue: Timestamp Timezone Issues

**Problem**: Timestamps not in UTC

**Solution**:
```python
# Always use datetime.utcnow()
from datetime import datetime

task.created_at = datetime.utcnow()

# Verify timezone
print(task.created_at.tzinfo)  # Should be None (UTC)
```

---

## Performance Tips

### 1. Use Indexes Effectively

```python
# Queries automatically use indexes on user_id
statement = select(Task).where(Task.user_id == "user_abc123")

# Composite index used for filtered queries
statement = select(Task).where(
    Task.user_id == "user_abc123",
    Task.completed == False
)
```

### 2. Batch Operations

```python
# Add multiple tasks at once
tasks = [
    Task(user_id="user_abc123", title=f"Task {i}")
    for i in range(10)
]
session.add_all(tasks)
session.commit()
```

### 3. Eager Loading

```python
# Load conversation with messages in one query
from sqlmodel import select
from sqlalchemy.orm import selectinload

statement = select(Conversation).options(
    selectinload(Conversation.messages)
).where(Conversation.id == conversation_id)

conversation = session.exec(statement).first()
# Messages already loaded, no additional query
for message in conversation.messages:
    print(message.content)
```

---

## Next Steps

1. **Implement API Endpoints**: Create FastAPI routes that use these models
2. **Add Authentication**: Integrate JWT token validation to extract user_id
3. **Implement MCP Tools**: Create stateless tools that use these models
4. **Add Caching**: Implement Redis caching for frequently accessed data
5. **Monitor Performance**: Add logging and metrics for database queries

---

## Additional Resources

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

## Support

For issues or questions:
1. Check the [data-model.md](./data-model.md) for entity definitions
2. Review the [research.md](./research.md) for design decisions
3. Consult the [plan.md](./plan.md) for implementation strategy
