"""Tests for task delete endpoint."""
import pytest
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.models.task import Task
from tests.conftest import create_test_user, create_test_task, get_auth_headers


client = TestClient(app)


def test_delete_task_success(test_db, test_user):
    """Test successfully deleting a task."""
    # Create a task
    task = create_test_task(test_db, test_user["id"], title="Task to Delete")

    # Delete the task
    response = client.delete(
        f"/api/v1/tasks/{task.id}",
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 204
    assert response.content == b''

    # Verify task is deleted
    from sqlmodel import select
    statement = select(Task).where(Task.id == task.id)
    deleted_task = test_db.exec(statement).first()
    assert deleted_task is None


def test_delete_task_not_found(test_db, test_user):
    """Test deleting non-existent task returns 404."""
    fake_id = uuid.uuid4()

    response = client.delete(
        f"/api/v1/tasks/{fake_id}",
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_task_unauthorized(test_db, test_user):
    """Test deleting task without authentication returns 403."""
    task = create_test_task(test_db, test_user["id"])

    response = client.delete(f"/api/v1/tasks/{task.id}")

    assert response.status_code == 403


def test_delete_other_user_task(test_db, test_user):
    """Test user cannot delete another user's task."""
    # Create task for first user
    task = create_test_task(test_db, test_user["id"])

    # Try to delete with different user's token
    other_user_id = uuid.uuid4()

    response = client.delete(
        f"/api/v1/tasks/{task.id}",
        headers=get_auth_headers(other_user_id)
    )

    assert response.status_code == 404

    # Verify task still exists
    from sqlmodel import select
    statement = select(Task).where(Task.id == task.id)
    existing_task = test_db.exec(statement).first()
    assert existing_task is not None


def test_delete_task_invalid_uuid(test_db, test_user):
    """Test deleting task with invalid UUID format returns 422."""
    response = client.delete(
        "/api/v1/tasks/not-a-uuid",
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 422


def test_delete_multiple_tasks(test_db, test_user):
    """Test deleting multiple tasks sequentially."""
    # Create multiple tasks
    task1 = create_test_task(test_db, test_user["id"], title="Task 1")
    task2 = create_test_task(test_db, test_user["id"], title="Task 2")
    task3 = create_test_task(test_db, test_user["id"], title="Task 3")

    # Delete first task
    response1 = client.delete(
        f"/api/v1/tasks/{task1.id}",
        headers=get_auth_headers(test_user["id"])
    )
    assert response1.status_code == 204

    # Delete second task
    response2 = client.delete(
        f"/api/v1/tasks/{task2.id}",
        headers=get_auth_headers(test_user["id"])
    )
    assert response2.status_code == 204

    # Verify only task3 remains
    from sqlmodel import select
    statement = select(Task).where(Task.user_id == test_user["id"])
    remaining_tasks = test_db.exec(statement).all()
    assert len(remaining_tasks) == 1
    assert remaining_tasks[0].id == task3.id


def test_delete_task_idempotent(test_db, test_user):
    """Test deleting same task twice returns 404 on second attempt."""
    task = create_test_task(test_db, test_user["id"])

    # First delete succeeds
    response1 = client.delete(
        f"/api/v1/tasks/{task.id}",
        headers=get_auth_headers(test_user["id"])
    )
    assert response1.status_code == 204

    # Second delete returns 404
    response2 = client.delete(
        f"/api/v1/tasks/{task.id}",
        headers=get_auth_headers(test_user["id"])
    )
    assert response2.status_code == 404


def test_delete_completed_task(test_db, test_user):
    """Test deleting a completed task works correctly."""
    task = create_test_task(test_db, test_user["id"], status="completed")

    response = client.delete(
        f"/api/v1/tasks/{task.id}",
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 204

    # Verify task is deleted
    from sqlmodel import select
    statement = select(Task).where(Task.id == task.id)
    deleted_task = test_db.exec(statement).first()
    assert deleted_task is None
