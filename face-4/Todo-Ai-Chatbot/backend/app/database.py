"""Database configuration and session management."""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/todo_db")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)

def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    with Session(engine) as session:
        yield session
