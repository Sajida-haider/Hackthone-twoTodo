"""Add task MCP tool."""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from app.models.task import Task
from app.database import get_session


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Add a new task for the user.

    Args:
        user_id: User identifier from JWT token
        title: Task title
        description: Optional task description
        due_date: Optional due date

    Returns:
        Dict with result status and task details
    """
    try:
        with next(get_session()) as session:
            # Create new task (ensure user_id is string)
            task = Task(
                user_id=str(user_id),
                title=title,
                description=description,
                completed=False
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "result": "success",
                "task_id": task.id,
                "title": task.title,
                "error_message": None
            }
    except Exception as e:
        return {
            "result": "error",
            "task_id": None,
            "title": title,
            "error_message": f"Failed to create task: {str(e)}"
        }
