"""User model for authentication and authorization."""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    """User model with authentication fields."""
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

    # Relationship will be defined when Task model is imported
    # tasks: List["Task"] = Relationship(back_populates="user")
