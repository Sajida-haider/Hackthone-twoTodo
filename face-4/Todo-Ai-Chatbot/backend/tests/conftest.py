"""Pytest configuration and fixtures."""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.database import get_session
from app.api.deps import get_current_user
from app.models import User, Task

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="engine")
def engine_fixture():
    """Create test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign key constraints for SQLite
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    """Create test database session."""
    with Session(engine) as session:
        yield session

# Alias for backward compatibility with Phase II tests
@pytest.fixture(name="test_db")
def test_db_fixture(session):
    """Alias for session fixture (Phase II compatibility)."""
    return session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user_id")
def test_user_id_fixture():
    """Generate test user ID (string for Phase III JWT tokens)."""
    return f"user_{uuid.uuid4().hex[:12]}"

@pytest.fixture(name="test_user_id_2")
def test_user_id_2_fixture():
    """Generate second test user ID for isolation tests."""
    return f"user_{uuid.uuid4().hex[:12]}"

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user (Phase II compatibility)."""
    user = User(
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="hashed_password_here",
        is_verified=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": str(user.id), "email": user.email}

@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(client: TestClient, test_user_id: str):
    """Create authenticated test client."""
    def get_current_user_override():
        return test_user_id

    app.dependency_overrides[get_current_user] = get_current_user_override
    yield client
    app.dependency_overrides.clear()

# Helper functions for Phase II tests
def create_test_user(session: Session, email: str = None) -> dict:
    """Create a test user and return user data."""
    if email is None:
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    user = User(
        email=email,
        password_hash="hashed_password_here",
        is_verified=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": str(user.id), "email": user.email}

def create_test_task(session: Session, user_id: str, title: str = "Test Task",
                     description: str = None, completed: bool = False) -> Task:
    """Create a test task and return the task object."""
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=completed
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_auth_headers(user_id: str) -> dict:
    """Get authorization headers for a user ID."""
    # In real tests, this would generate a proper JWT token
    # For now, we'll use a mock token since the test client overrides auth
    return {"Authorization": f"Bearer mock_token_for_{user_id}"}

