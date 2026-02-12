"""User schemas."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import uuid


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserResponse(UserBase):
    """User response schema."""
    id: uuid.UUID
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """User in database schema."""
    id: uuid.UUID
    password_hash: str
    is_verified: bool
    is_active: bool
    failed_login_attempts: int
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True
