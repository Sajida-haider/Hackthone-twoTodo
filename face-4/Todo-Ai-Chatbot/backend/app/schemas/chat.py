"""Pydantic schemas for chat API."""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    conversation_id: Optional[int] = Field(default=None, description="Optional conversation ID to continue")

    @validator('message')
    def message_not_empty(cls, v):
        """Validate message is not empty after stripping."""
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ToolCallSchema(BaseModel):
    """Schema for MCP tool call result."""
    tool: str = Field(..., description="Tool name that was invoked")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to the tool")
    result: str = Field(..., description="Result status (success or error)")
    error_message: Optional[str] = Field(default=None, description="Error message if result is error")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: int = Field(..., description="Conversation ID (new or existing)")
    response: str = Field(..., description="AI assistant's response text")
    tool_calls: List[ToolCallSchema] = Field(default_factory=list, description="List of tool invocations")


class ConversationSchema(BaseModel):
    """Schema for conversation metadata."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    """Schema for message representation."""
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
