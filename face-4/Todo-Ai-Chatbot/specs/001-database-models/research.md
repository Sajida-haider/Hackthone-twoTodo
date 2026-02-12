# Research: Database & Models

**Feature**: Database & Models (001-database-models)
**Date**: 2026-02-09
**Phase**: Phase 0 - Research & Technology Validation

## Research Overview

This document consolidates research findings for implementing database models using SQLModel ORM with Neon PostgreSQL for the Phase III AI Chatbot.

---

## R1: SQLModel Best Practices for Multi-User Systems

### User Isolation Patterns

**Decision**: Implement user_id filtering at the query level using SQLModel's `select()` with `where()` clauses.

**Pattern**:
```python
from sqlmodel import select, Session

def get_user_tasks(session: Session, user_id: str):
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()
```

**Rationale**:
- Explicit filtering prevents accidental data leakage
- Works seamlessly with SQLModel's type-safe query builder
- Easy to audit and test

**Alternatives Considered**:
- Row-level security in PostgreSQL (more complex, harder to test)
- Application-level middleware (less explicit, harder to trace)

### Automatic Timestamp Handling

**Decision**: Use `datetime.utcnow` as default value with `sa_column_kwargs` for auto-update.

**Pattern**:
```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func

class BaseModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False
    )
```

**Rationale**:
- Automatic timestamp management reduces errors
- UTC ensures consistency across timezones
- `onupdate` automatically updates `updated_at` on modifications

**Alternatives Considered**:
- Manual timestamp management (error-prone)
- Database triggers (less portable, harder to test)

### Foreign Key Relationships and Cascade Deletion

**Decision**: Use SQLModel's `Relationship` with SQLAlchemy's `ForeignKey` and cascade options.

**Pattern**:
```python
from sqlmodel import Field, Relationship
from typing import Optional, List

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

**Rationale**:
- Cascade deletion ensures referential integrity
- `delete-orphan` prevents orphaned messages
- Bidirectional relationships enable easy navigation

**Alternatives Considered**:
- Manual deletion (error-prone, requires multiple queries)
- Database-level cascades only (less explicit in code)

### Index Optimization for user_id Filtering

**Decision**: Add indexes on all `user_id` columns and foreign key columns.

**Pattern**:
```python
user_id: str = Field(index=True)  # Creates B-tree index
conversation_id: int = Field(foreign_key="conversation.id", index=True)
```

**Rationale**:
- Dramatically improves query performance for user-specific data
- Foreign key indexes speed up joins and cascade operations
- Minimal storage overhead for significant performance gain

**Performance Impact**:
- Without index: O(n) table scan
- With index: O(log n) lookup
- Expected 10-100x speedup for user queries

---

## R2: Neon PostgreSQL Connection Patterns

### Connection Pooling with Neon Serverless

**Decision**: Use SQLAlchemy's connection pooling with psycopg2 driver.

**Configuration**:
```python
from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    echo=False,  # Set to True for SQL logging in development
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Additional connections when pool is full
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    poolclass=QueuePool
)
```

**Rationale**:
- Neon supports standard PostgreSQL protocol
- Connection pooling reduces latency and resource usage
- QueuePool is thread-safe and production-ready

**Neon-Specific Considerations**:
- Neon auto-scales, so connection pooling is still beneficial
- Use reasonable pool sizes (5-10) to avoid overwhelming Neon
- Neon has built-in connection pooling, but application-level pooling still helps

**Alternatives Considered**:
- No pooling (poor performance, connection overhead)
- PgBouncer (additional infrastructure complexity)

### Environment Variable Configuration

**Decision**: Load DATABASE_URL from environment with validation.

**Pattern**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**Rationale**:
- Environment variables prevent hardcoded credentials
- Pydantic validates configuration at startup
- Easy to override for different environments (dev, test, prod)

**Security Best Practices**:
- Never commit .env files to version control
- Use different credentials for each environment
- Rotate credentials regularly

### Connection Retry and Error Handling

**Decision**: Implement retry logic with exponential backoff for transient errors.

**Pattern**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.exc import OperationalError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(OperationalError)
)
def get_session():
    return Session(engine)
```

**Rationale**:
- Handles transient network issues gracefully
- Exponential backoff prevents overwhelming the database
- Fails fast after reasonable attempts

**Common Errors to Handle**:
- Connection timeout
- Connection refused
- Too many connections
- Network interruption

### Transaction Management for Data Integrity

**Decision**: Use context managers for automatic transaction handling.

**Pattern**:
```python
from contextlib import contextmanager

@contextmanager
def get_db_session():
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
    task = Task(user_id="user123", title="Test")
    session.add(task)
    # Automatically commits on success, rolls back on error
```

**Rationale**:
- Ensures transactions are always committed or rolled back
- Prevents partial updates and data corruption
- Automatic cleanup of database connections

---

## R3: Alembic Migration Strategy

### Alembic Setup with SQLModel

**Decision**: Use Alembic with auto-generation from SQLModel models.

**Setup Steps**:
1. Initialize Alembic: `alembic init alembic`
2. Configure `alembic/env.py` to import SQLModel models
3. Set `target_metadata` to SQLModel metadata
4. Configure `sqlalchemy.url` from environment

**Configuration** (`alembic/env.py`):
```python
from app.models import *  # Import all models
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata
```

**Rationale**:
- Auto-generation reduces manual migration writing
- SQLModel metadata provides complete schema information
- Standard tool with excellent documentation

### Auto-Generation of Migrations

**Decision**: Use `alembic revision --autogenerate` for migration creation.

**Workflow**:
```bash
# 1. Make changes to SQLModel models
# 2. Generate migration
alembic revision --autogenerate -m "Add conversation and message models"

# 3. Review generated migration
# 4. Apply migration
alembic upgrade head
```

**Rationale**:
- Detects schema changes automatically
- Generates both upgrade and downgrade scripts
- Reduces human error in migration writing

**Limitations**:
- Cannot detect all changes (e.g., data migrations)
- Requires manual review before applying
- May need manual adjustments for complex changes

### Migration Rollback Strategies

**Decision**: Always test rollback before deploying migrations.

**Best Practices**:
```bash
# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1

# Re-apply
alembic upgrade head
```

**Rationale**:
- Ensures migrations are reversible
- Enables safe rollback in production
- Catches migration errors early

**Rollback Considerations**:
- Data loss: Some rollbacks may lose data (e.g., dropping columns)
- Document irreversible migrations clearly
- Consider data backups before major migrations

### Data Migration for Existing Users

**Decision**: Use Alembic's `op.execute()` for data migrations when needed.

**Pattern**:
```python
def upgrade():
    # Schema change
    op.add_column('task', sa.Column('priority', sa.Integer(), nullable=True))

    # Data migration
    op.execute("UPDATE task SET priority = 1 WHERE priority IS NULL")

    # Make column non-nullable
    op.alter_column('task', 'priority', nullable=False)
```

**Rationale**:
- Combines schema and data changes in single migration
- Ensures data consistency during migration
- Atomic operation (all or nothing)

---

## R4: Testing Strategy for Database Models

### pytest Fixtures for Database Testing

**Decision**: Use pytest fixtures for test database setup and teardown.

**Pattern**:
```python
import pytest
from sqlmodel import create_engine, Session, SQLModel

@pytest.fixture(scope="function")
def test_db():
    # Use in-memory SQLite for fast tests
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)

def test_create_task(test_db):
    task = Task(user_id="user123", title="Test Task")
    test_db.add(task)
    test_db.commit()

    assert task.id is not None
```

**Rationale**:
- Each test gets fresh database (isolation)
- Fast execution with in-memory SQLite
- Automatic cleanup after each test

### Test Database Setup/Teardown

**Decision**: Use SQLite for unit tests, PostgreSQL for integration tests.

**Strategy**:
- **Unit Tests**: SQLite in-memory (fast, isolated)
- **Integration Tests**: PostgreSQL test database (realistic)

**Configuration**:
```python
# conftest.py
@pytest.fixture(scope="session")
def integration_db():
    # Use separate test database
    test_db_url = "postgresql://user:pass@localhost:5432/test_db"
    engine = create_engine(test_db_url)

    # Create tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup
    SQLModel.metadata.drop_all(engine)
```

**Rationale**:
- Unit tests run quickly with SQLite
- Integration tests catch PostgreSQL-specific issues
- Separate test database prevents data corruption

### Mocking vs Real Database for Tests

**Decision**: Use real database (SQLite/PostgreSQL) for model tests, mocking for service tests.

**Guidelines**:
- **Model Tests**: Real database (test actual SQL behavior)
- **Service Tests**: Mock database (test business logic)
- **API Tests**: Real database (test end-to-end)

**Rationale**:
- Model tests need real database to verify SQL correctness
- Service tests focus on logic, not database behavior
- API tests verify complete integration

### Testing Cascade Deletion and Constraints

**Decision**: Write explicit tests for cascade behavior and constraints.

**Test Examples**:
```python
def test_cascade_delete_messages(test_db):
    # Create conversation with messages
    conv = Conversation(user_id="user123")
    test_db.add(conv)
    test_db.commit()

    msg = Message(
        user_id="user123",
        conversation_id=conv.id,
        role="user",
        content="Hello"
    )
    test_db.add(msg)
    test_db.commit()

    # Delete conversation
    test_db.delete(conv)
    test_db.commit()

    # Verify message was deleted
    messages = test_db.exec(select(Message)).all()
    assert len(messages) == 0

def test_user_isolation(test_db):
    # Create tasks for two users
    task1 = Task(user_id="user1", title="Task 1")
    task2 = Task(user_id="user2", title="Task 2")
    test_db.add_all([task1, task2])
    test_db.commit()

    # Query user1's tasks
    user1_tasks = test_db.exec(
        select(Task).where(Task.user_id == "user1")
    ).all()

    # Verify isolation
    assert len(user1_tasks) == 1
    assert user1_tasks[0].title == "Task 1"
```

**Rationale**:
- Explicit tests document expected behavior
- Catches regressions in cascade logic
- Verifies user isolation works correctly

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| ORM | SQLModel 0.0.14+ | Type-safe, FastAPI integration, Pydantic validation |
| Database | Neon PostgreSQL | Serverless, auto-scaling, standard PostgreSQL |
| Migrations | Alembic with auto-generation | Industry standard, reversible migrations |
| Testing | pytest with SQLite/PostgreSQL | Fast unit tests, realistic integration tests |
| Timestamps | UTC with auto-update | Consistency, automatic management |
| User Isolation | Query-level filtering | Explicit, auditable, type-safe |
| Cascade Deletion | SQLAlchemy cascade options | Referential integrity, automatic cleanup |
| Connection Pooling | SQLAlchemy QueuePool | Performance, resource efficiency |

---

## Next Steps

All research complete. Proceed to Phase 1: Design & Contracts.
