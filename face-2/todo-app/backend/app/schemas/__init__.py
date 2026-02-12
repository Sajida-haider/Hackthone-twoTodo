"""Package initialization for schemas."""
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.schemas.error import ErrorResponse
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse, UserInfo,
    VerifyEmailResponse, ResendVerificationRequest, ResendVerificationResponse,
    LogoutResponse
)
from app.schemas.user import UserBase, UserCreate, UserResponse, UserInDB

__all__ = [
    "TaskCreate", "TaskUpdate", "TaskRead", "ErrorResponse",
    "RegisterRequest", "RegisterResponse",
    "LoginRequest", "LoginResponse", "UserInfo",
    "VerifyEmailResponse", "ResendVerificationRequest", "ResendVerificationResponse",
    "LogoutResponse",
    "UserBase", "UserCreate", "UserResponse", "UserInDB"
]
