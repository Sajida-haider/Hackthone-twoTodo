"""Verification token model for email verification."""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class VerificationToken(SQLModel, table=True):
    """Verification token for email verification."""
    __tablename__ = "verification_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    token: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime = Field(index=True)
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
