"""Task CRUD API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
import uuid
from datetime import datetime

from app.api.deps import get_current_user, get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead

router = APIRouter()

@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Create a new task for the authenticated user.

    - **title**: Task title (required, 1-200 characters)
    - **description**: Optional task description (max 2000 characters)
    - **due_date**: Optional due date in ISO 8601 format

    Returns the created task with status defaulting to "pending".
    """
    # Create task with user_id from JWT token
    task = Task(
        user_id=current_user_id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        status="pending"
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/tasks", response_model=List[TaskRead])
async def list_tasks(
    current_user_id: uuid.UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Get all tasks for the authenticated user.

    Returns tasks ordered by creation date (newest first).
    Only returns tasks belonging to the authenticated user.
    """
    statement = select(Task).where(
        Task.user_id == current_user_id
    ).order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Get a single task by ID.

    Returns 404 if task doesn't exist or doesn't belong to the user.
    This prevents revealing the existence of other users' tasks.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )

    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Update an existing task.

    Only the task owner can update their tasks.
    All fields are optional - only provided fields will be updated.
    Returns 404 if task doesn't exist or doesn't belong to the user.
    """
    # Fetch task with ownership verification
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )

    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Delete a task.

    Only the task owner can delete their tasks.
    Returns 404 if task doesn't exist or doesn't belong to the user.
    Returns 204 No Content on successful deletion.
    """
    # Fetch task with ownership verification
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )

    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()

    return None
