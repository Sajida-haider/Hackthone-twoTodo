"""Authentication event model for security audit logging."""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class AuthEvent(SQLModel, table=True):
    """Authentication event for security audit logging."""
    __tablename__ = "auth_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id", index=True, default=None)
    event_type: str = Field(max_length=50, index=True)
    ip_address: Optional[str] = Field(max_length=45, default=None)
    user_agent: Optional[str] = Field(max_length=500, default=None)
    success: bool
    failure_reason: Optional[str] = Field(max_length=255, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
