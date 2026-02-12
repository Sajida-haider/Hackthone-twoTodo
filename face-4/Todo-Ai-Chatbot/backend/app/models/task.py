"""Task model for Phase III AI Chatbot."""
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    Phase III specification:
    - Integer ID (auto-increment)
    - String user_id (from JWT token)
    - Title and optional description
    - Boolean completion status
    - Automatic timestamps in UTC
    """
    __tablename__ = "task"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="Owner user identifier from JWT")
    title: str = Field(max_length=500, nullable=False, description="Task title")
    description: Optional[str] = Field(default=None, max_length=5000, description="Optional task description")
    completed: bool = Field(default=False, nullable=False, description="Task completion status")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp in UTC"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False,
        description="Last modification timestamp in UTC"
    )

    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False
            }
        }
