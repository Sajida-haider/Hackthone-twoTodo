"""Update task MCP tool."""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from app.models.task import Task
from app.database import get_session


async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Update an existing task.

    Args:
        user_id: User identifier from JWT token
        task_id: ID of the task to update
        title: Optional new title
        description: Optional new description
        due_date: Optional new due date

    Returns:
        Dict with result status and task details
    """
    try:
        with next(get_session()) as session:
            # Find task
            task = session.exec(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
            ).first()

            if not task:
                return {
                    "result": "error",
                    "task_id": task_id,
                    "error_message": "Task not found"
                }

            # Update fields if provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

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
            "task_id": task_id,
            "error_message": f"Failed to update task: {str(e)}"
        }
