"""Complete task MCP tool."""
from typing import Dict, Any
from sqlmodel import Session, select
from app.models.task import Task
from app.database import get_session


async def complete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        user_id: User identifier from JWT token
        task_id: ID of the task to complete

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

            # Check if already completed
            if task.completed:
                return {
                    "result": "success",
                    "task_id": task.id,
                    "title": task.title,
                    "message": "Task was already completed",
                    "error_message": None
                }

            # Mark as completed
            task.completed = True
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
            "error_message": f"Failed to complete task: {str(e)}"
        }
