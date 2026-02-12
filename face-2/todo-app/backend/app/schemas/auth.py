"""Authentication request and response schemas."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


# Registration schemas
class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class RegisterResponse(BaseModel):
    """User registration response."""
    message: str
    user_id: uuid.UUID
    email: str


# Login schemas
class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    """User information in login response."""
    id: uuid.UUID
    email: str


class LoginResponse(BaseModel):
    """User login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo


# Email verification schemas
class VerifyEmailResponse(BaseModel):
    """Email verification response."""
    message: str
    user_id: uuid.UUID


class ResendVerificationRequest(BaseModel):
    """Resend verification email request."""
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    """Resend verification email response."""
    message: str


# Logout schemas
class LogoutResponse(BaseModel):
    """Logout response."""
    message: str


# Error response schema
class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
