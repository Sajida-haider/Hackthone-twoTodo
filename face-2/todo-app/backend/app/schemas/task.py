"""Pydantic schemas for Task API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    due_date: Optional[datetime] = Field(None, description="Optional due date")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and vegetables",
                "due_date": "2026-02-15T10:00:00Z"
            }
        }

class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated task title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated task description")
    status: Optional[str] = Field(None, pattern="^(pending|completed)$", description="Task status")
    due_date: Optional[datetime] = Field(None, description="Updated due date")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and milk",
                "status": "completed"
            }
        }

class TaskRead(BaseModel):
    """Schema for reading task data."""
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "pending",
                "due_date": "2026-02-15T10:00:00Z",
                "created_at": "2026-02-08T12:00:00Z",
                "updated_at": "2026-02-08T12:00:00Z"
            }
        }
