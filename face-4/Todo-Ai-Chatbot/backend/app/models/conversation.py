"""Conversation model for Phase III AI Chatbot."""
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between user and AI assistant.

    Phase III specification:
    - Integer ID (auto-increment)
    - String user_id (from JWT token)
    - Automatic timestamps in UTC
    - One-to-many relationship with messages (cascade delete)
    """
    __tablename__ = "conversation"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="Owner user identifier from JWT")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp in UTC"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False,
        description="Last modification timestamp in UTC (updates when messages added)"
    )

    # Relationship to messages (cascade delete)
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "user_id": "user_abc123"
            }
        }
