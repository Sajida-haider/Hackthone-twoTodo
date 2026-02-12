"""Delete task MCP tool."""
from typing import Dict, Any
from sqlmodel import Session, select
from app.models.task import Task
from app.database import get_session


async def delete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete a task.

    Args:
        user_id: User identifier from JWT token
        task_id: ID of the task to delete

    Returns:
        Dict with result status
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

            # Store title before deletion
            title = task.title

            # Delete task
            session.delete(task)
            session.commit()

            return {
                "result": "success",
                "task_id": task_id,
                "title": title,
                "error_message": None
            }
    except Exception as e:
        return {
            "result": "error",
            "task_id": task_id,
            "error_message": f"Failed to delete task: {str(e)}"
        }
