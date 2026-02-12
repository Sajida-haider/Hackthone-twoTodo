# SQLModel Mapping

## Purpose
Map database schema to Python ORM models using SQLModel for clean and maintainable data layer.

## Steps
1. Define SQLModel classes for each entity
2. Configure fields and types with proper validation
3. Add relationships and constraints
4. Implement query methods and utilities

## Output
Clean and maintainable SQLModel models with proper typing and relationships

## Implementation Details

### SQLModel Class Definition

#### Basic Model Structure
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Model Inheritance
- Use `SQLModel` base class with `table=True` for database tables
- Use `SQLModel` without `table=True` for Pydantic schemas
- Create base classes for common fields
- Implement mixins for reusable functionality

### Field Types and Configuration

#### Python to PostgreSQL Type Mapping
```python
from sqlmodel import Field, Column
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, JSON
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import uuid

class Task(SQLModel, table=True):
    # UUID - PostgreSQL UUID
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # String - PostgreSQL VARCHAR
    title: str = Field(max_length=200)

    # Optional String - PostgreSQL VARCHAR NULL
    subtitle: Optional[str] = Field(default=None, max_length=200)

    # Text - PostgreSQL TEXT
    description: Optional[str] = Field(default=None)

    # Boolean - PostgreSQL BOOLEAN
    completed: bool = Field(default=False)

    # Integer - PostgreSQL INTEGER
    priority: int = Field(default=0, ge=0, le=5)

    # Float - PostgreSQL DOUBLE PRECISION
    progress: float = Field(default=0.0, ge=0.0, le=100.0)

    # Decimal - PostgreSQL NUMERIC
    estimated_hours: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)

    # DateTime - PostgreSQL TIMESTAMP WITH TIME ZONE
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Date - PostgreSQL DATE
    start_date: Optional[date] = None

    # JSON - PostgreSQL JSONB
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
```

#### Field Configuration Options
```python
from sqlmodel import Field

class Example(SQLModel, table=True):
    # Primary key
    id: int = Field(primary_key=True)

    # Auto-increment
    id: int = Field(default=None, primary_key=True)

    # Unique constraint
    email: str = Field(unique=True)

    # Index
    username: str = Field(index=True)

    # Not nullable (default)
    required_field: str

    # Nullable
    optional_field: Optional[str] = None

    # Default value
    status: str = Field(default="pending")

    # Default factory (for dynamic defaults)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # String length constraint
    name: str = Field(max_length=100)

    # Numeric constraints
    age: int = Field(ge=0, le=150)  # greater/equal, less/equal
    rating: float = Field(gt=0, lt=5)  # greater than, less than

    # Foreign key
    user_id: uuid.UUID = Field(foreign_key="users.id")

    # Custom column name
    internal_id: int = Field(sa_column_kwargs={"name": "id"})
```

### Relationships

#### One-to-Many Relationship
```python
from sqlmodel import Relationship
from typing import List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)

    # One user has many tasks
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str

    # Many tasks belong to one user
    user: User = Relationship(back_populates="tasks")
```

#### Many-to-Many Relationship
```python
from sqlmodel import Relationship
from typing import List, Optional

# Junction/Link table
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: uuid.UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str

    # Many tasks have many tags
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model=TaskTag
    )

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, max_length=50)

    # Many tags belong to many tasks
    tasks: List[Task] = Relationship(
        back_populates="tags",
        link_model=TaskTag
    )
```

#### One-to-One Relationship
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str

    # One user has one profile
    profile: Optional["UserProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )

class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    bio: Optional[str] = None

    # One profile belongs to one user
    user: User = Relationship(back_populates="profile")
```

### Pydantic Integration

#### Separate Read/Write Models
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

# Database model (table=True)
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Create schema (for API input)
class TaskCreate(SQLModel):
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = None
    completed: bool = False

# Update schema (for API input)
class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=200, min_length=1)
    description: Optional[str] = None
    completed: Optional[bool] = None

# Read schema (for API output)
class TaskRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

#### Model Configuration
```python
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int = Field(primary_key=True)
    title: str

    class Config:
        # Allow ORM mode for FastAPI response models
        orm_mode = True

        # Validate on assignment
        validate_assignment = True

        # Use enum values instead of enum objects
        use_enum_values = True

        # JSON schema customization
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Sample task"
            }
        }
```

### Constraints and Validation

#### Field Validators
```python
from sqlmodel import SQLModel, Field
from pydantic import validator, root_validator
from datetime import datetime

class Task(SQLModel, table=True):
    title: str = Field(max_length=200)
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v

    @root_validator
    def check_dates(cls, values):
        start = values.get('start_date')
        due = values.get('due_date')
        if start and due and start > due:
            raise ValueError('Start date must be before due date')
        return values
```

#### Database Constraints
```python
from sqlmodel import SQLModel, Field, Column, CheckConstraint
from sqlalchemy import UniqueConstraint, Index

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        # Unique constraint on multiple columns
        UniqueConstraint('user_id', 'title', name='unique_user_task'),

        # Check constraint
        CheckConstraint('priority >= 0 AND priority <= 5', name='valid_priority'),

        # Composite index
        Index('idx_user_completed', 'user_id', 'completed'),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    title: str = Field(max_length=200)
    priority: int = Field(default=0)
    completed: bool = Field(default=False)
```

### Database Session Management

#### Session Creation
```python
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator

# Database URL
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max connections beyond pool_size
)

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Session dependency for FastAPI
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

### Query Patterns

#### Basic CRUD Operations
```python
from sqlmodel import Session, select
from typing import List, Optional

# Create
def create_task(session: Session, task: TaskCreate, user_id: uuid.UUID) -> Task:
    db_task = Task(**task.dict(), user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# Read one
def get_task(session: Session, task_id: uuid.UUID) -> Optional[Task]:
    return session.get(Task, task_id)

# Read many
def get_tasks(session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
    return session.exec(statement).all()

# Update
def update_task(session: Session, task_id: uuid.UUID, task_update: TaskUpdate) -> Optional[Task]:
    db_task = session.get(Task, task_id)
    if not db_task:
        return None

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# Delete
def delete_task(session: Session, task_id: uuid.UUID) -> bool:
    db_task = session.get(Task, task_id)
    if not db_task:
        return False

    session.delete(db_task)
    session.commit()
    return True
```

#### Advanced Queries
```python
from sqlmodel import select, and_, or_, func

# Filter with multiple conditions
def get_completed_tasks(session: Session, user_id: uuid.UUID) -> List[Task]:
    statement = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True
        )
    )
    return session.exec(statement).all()

# Order by
def get_tasks_ordered(session: Session, user_id: uuid.UUID) -> List[Task]:
    statement = select(Task).where(
        Task.user_id == user_id
    ).order_by(Task.due_date.desc(), Task.created_at.desc())
    return session.exec(statement).all()

# Count
def count_user_tasks(session: Session, user_id: uuid.UUID) -> int:
    statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    return session.exec(statement).one()

# Join with relationships
def get_tasks_with_user(session: Session) -> List[Task]:
    statement = select(Task).join(User).where(User.is_active == True)
    return session.exec(statement).all()
```

### Best Practices

#### Model Organization
- Keep models in separate files by domain
- Use base classes for common fields
- Implement `__repr__` for debugging
- Add type hints for all fields
- Document complex relationships

#### Performance
- Use `select()` instead of `query()` for SQLModel 0.0.8+
- Eager load relationships when needed
- Use indexes on foreign keys
- Batch operations when possible
- Use `session.exec()` for queries

#### Security
- Never expose database models directly in APIs
- Use separate read/write schemas
- Validate all input data
- Sanitize user input
- Use parameterized queries (automatic with SQLModel)

#### Testing
- Use in-memory SQLite for tests
- Create fixtures for common models
- Test validators and constraints
- Mock database sessions
- Test relationship loading

## Complete Example

```python
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select
from typing import Optional, List
from datetime import datetime
import uuid

# Models
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="tasks")

# Schemas
class TaskCreate(SQLModel):
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# Database setup
DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# CRUD operations
def create_task(session: Session, task: TaskCreate, user_id: uuid.UUID) -> Task:
    db_task = Task(**task.dict(), user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def get_user_tasks(session: Session, user_id: uuid.UUID) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()
```

## Validation Checklist
- [ ] All database tables have corresponding SQLModel classes
- [ ] Field types match PostgreSQL column types
- [ ] Relationships properly configured with back_populates
- [ ] Foreign keys defined with proper indexes
- [ ] Validators added for business logic
- [ ] Separate schemas for create/read/update operations
- [ ] Session management properly implemented
- [ ] CRUD operations follow best practices
- [ ] Models are properly typed with type hints
- [ ] Documentation added for complex logic
