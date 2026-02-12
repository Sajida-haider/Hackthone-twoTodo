"""Unit tests for Task model (Phase III)."""
import pytest
from datetime import datetime
from sqlmodel import Session, select

from app.models import Task


def test_task_creation_with_required_fields(session: Session, test_user_id: str):
    """Test creating a task with only required fields."""
    task = Task(
        user_id=test_user_id,
        title="Test Task"
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.id is not None
    assert task.user_id == test_user_id
    assert task.title == "Test Task"
    assert task.description is None
    assert task.completed is False
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_creation_with_all_fields(session: Session, test_user_id: str):
    """Test creating a task with all fields."""
    task = Task(
        user_id=test_user_id,
        title="Complete Task",
        description="This is a detailed description",
        completed=True
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.id is not None
    assert task.user_id == test_user_id
    assert task.title == "Complete Task"
    assert task.description == "This is a detailed description"
    assert task.completed is True
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_title_max_length(session: Session, test_user_id: str):
    """Test task title respects max length of 500 characters."""
    long_title = "A" * 500
    task = Task(
        user_id=test_user_id,
        title=long_title
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    assert len(task.title) == 500
    assert task.title == long_title


def test_task_description_max_length(session: Session, test_user_id: str):
    """Test task description respects max length of 5000 characters."""
    long_description = "B" * 5000
    task = Task(
        user_id=test_user_id,
        title="Test",
        description=long_description
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    assert len(task.description) == 5000
    assert task.description == long_description


def test_task_user_isolation(session: Session, test_user_id: str, test_user_id_2: str):
    """Test that tasks are isolated by user_id."""
    # Create tasks for two different users
    task1 = Task(user_id=test_user_id, title="User 1 Task")
    task2 = Task(user_id=test_user_id_2, title="User 2 Task")
    session.add(task1)
    session.add(task2)
    session.commit()

    # Query tasks for user 1
    user1_tasks = session.exec(
        select(Task).where(Task.user_id == test_user_id)
    ).all()

    # Query tasks for user 2
    user2_tasks = session.exec(
        select(Task).where(Task.user_id == test_user_id_2)
    ).all()

    assert len(user1_tasks) == 1
    assert len(user2_tasks) == 1
    assert user1_tasks[0].title == "User 1 Task"
    assert user2_tasks[0].title == "User 2 Task"


def test_task_timestamps_auto_set(session: Session, test_user_id: str):
    """Test that timestamps are automatically set on creation."""
    before_creation = datetime.utcnow()

    task = Task(user_id=test_user_id, title="Timestamp Test")
    session.add(task)
    session.commit()
    session.refresh(task)

    after_creation = datetime.utcnow()

    assert before_creation <= task.created_at <= after_creation
    assert before_creation <= task.updated_at <= after_creation
    assert task.created_at == task.updated_at


def test_task_completed_default_false(session: Session, test_user_id: str):
    """Test that completed defaults to False."""
    task = Task(user_id=test_user_id, title="Default Completed Test")
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.completed is False


def test_task_update_changes_updated_at(session: Session, test_user_id: str):
    """Test that updating a task changes updated_at timestamp."""
    task = Task(user_id=test_user_id, title="Original Title")
    session.add(task)
    session.commit()
    session.refresh(task)

    original_updated_at = task.updated_at

    # Update the task
    task.title = "Updated Title"
    task.completed = True
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.updated_at >= original_updated_at
    assert task.title == "Updated Title"
    assert task.completed is True


def test_task_query_by_completed_status(session: Session, test_user_id: str):
    """Test querying tasks by completed status."""
    # Create completed and pending tasks
    task1 = Task(user_id=test_user_id, title="Completed Task", completed=True)
    task2 = Task(user_id=test_user_id, title="Pending Task", completed=False)
    task3 = Task(user_id=test_user_id, title="Another Pending", completed=False)

    session.add_all([task1, task2, task3])
    session.commit()

    # Query completed tasks
    completed_tasks = session.exec(
        select(Task).where(Task.user_id == test_user_id, Task.completed == True)
    ).all()

    # Query pending tasks
    pending_tasks = session.exec(
        select(Task).where(Task.user_id == test_user_id, Task.completed == False)
    ).all()

    assert len(completed_tasks) == 1
    assert len(pending_tasks) == 2
    assert completed_tasks[0].title == "Completed Task"


def test_task_deletion(session: Session, test_user_id: str):
    """Test deleting a task."""
    task = Task(user_id=test_user_id, title="Task to Delete")
    session.add(task)
    session.commit()
    session.refresh(task)

    task_id = task.id

    # Delete the task
    session.delete(task)
    session.commit()

    # Verify task is deleted
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None
