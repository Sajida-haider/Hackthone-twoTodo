"""Pydantic schemas for Task API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and vegetables"
            }
        }

class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated task title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated task description")
    completed: Optional[bool] = Field(None, description="Task completion status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and milk",
                "completed": True
            }
        }

class TaskRead(BaseModel):
    """Schema for reading task data."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "af18c6bd-7e96-47b9-a6e4-484180b16c2e",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-08T12:00:00Z",
                "updated_at": "2026-02-08T12:00:00Z"
            }
        }
