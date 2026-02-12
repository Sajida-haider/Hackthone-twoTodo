"""List tasks MCP tool."""
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from app.models.task import Task
from app.database import get_session


async def list_tasks(
    user_id: str,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List tasks for the user.

    Args:
        user_id: User identifier from JWT token
        status: Optional filter by status ("pending" or "completed")

    Returns:
        Dict with result status and list of tasks
    """
    try:
        with next(get_session()) as session:
            # Build query
            query = select(Task).where(Task.user_id == user_id)

            # Apply status filter if provided
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

            # Execute query
            tasks = session.exec(query).all()

            # Format tasks
            task_list = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ]

            return {
                "result": "success",
                "tasks": task_list,
                "count": len(task_list),
                "error_message": None
            }
    except Exception as e:
        return {
            "result": "error",
            "tasks": [],
            "count": 0,
            "error_message": f"Failed to list tasks: {str(e)}"
        }
