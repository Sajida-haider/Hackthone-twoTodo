"""Error response schemas."""
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str
    code: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Task not found",
                "code": "TASK_NOT_FOUND"
            }
        }
