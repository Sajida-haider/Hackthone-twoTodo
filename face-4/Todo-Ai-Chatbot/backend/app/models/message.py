"""Message model for Phase III AI Chatbot."""
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message sender role enum."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message model representing a single message within a conversation.

    Phase III specification:
    - Integer ID (auto-increment)
    - String user_id (from JWT token)
    - Foreign key to conversation (cascade delete)
    - Role enum (user or assistant)
    - Message content
    - Creation timestamp in UTC
    """
    __tablename__ = "message"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="Owner user identifier from JWT")
    conversation_id: int = Field(
        foreign_key="conversation.id",
        index=True,
        nullable=False,
        description="Parent conversation identifier"
    )
    role: MessageRole = Field(nullable=False, description="Message sender role (user or assistant)")
    content: str = Field(max_length=10000, nullable=False, description="Message content")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"index": True},
        description="Creation timestamp in UTC"
    )

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "conversation_id": 1,
                "role": "user",
                "content": "Hello! Can you help me with my tasks?"
            }
        }
