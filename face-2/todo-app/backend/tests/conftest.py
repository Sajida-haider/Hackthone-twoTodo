"""Pytest configuration and fixtures."""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.database import get_session
from app.api.deps import get_current_user

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
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    """Create test database session."""
    with Session(engine) as session:
        yield session

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
    """Generate test user ID."""
    return uuid.uuid4()

@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(client: TestClient, test_user_id: uuid.UUID):
    """Create authenticated test client."""
    def get_current_user_override():
        return test_user_id

    app.dependency_overrides[get_current_user] = get_current_user_override
    yield client
    app.dependency_overrides.clear()
