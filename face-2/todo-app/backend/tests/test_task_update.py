"""Tests for task update endpoint."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.models.task import Task
from tests.conftest import create_test_user, create_test_task, get_auth_headers


client = TestClient(app)


def test_update_task_title(test_db, test_user):
    """Test updating task title."""
    # Create a task
    task = create_test_task(test_db, test_user["id"], title="Original Title")

    # Update the task
    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Updated Title"},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == task.description
    assert data["status"] == task.status


def test_update_task_status(test_db, test_user):
    """Test updating task status to completed."""
    task = create_test_task(test_db, test_user["id"], status="pending")

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"status": "completed"},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["title"] == task.title


def test_update_task_multiple_fields(test_db, test_user):
    """Test updating multiple fields at once."""
    task = create_test_task(test_db, test_user["id"])

    new_due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={
            "title": "New Title",
            "description": "New Description",
            "status": "completed",
            "due_date": new_due_date
        },
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "New Description"
    assert data["status"] == "completed"
    assert data["due_date"] is not None


def test_update_task_partial_fields(test_db, test_user):
    """Test updating only some fields leaves others unchanged."""
    task = create_test_task(
        test_db,
        test_user["id"],
        title="Original",
        description="Original Description"
    )

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Updated"},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "Original Description"


def test_update_task_not_found(test_db, test_user):
    """Test updating non-existent task returns 404."""
    fake_id = uuid.uuid4()

    response = client.patch(
        f"/api/v1/tasks/{fake_id}",
        json={"title": "Updated"},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_task_unauthorized(test_db, test_user):
    """Test updating task without authentication returns 401."""
    task = create_test_task(test_db, test_user["id"])

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Updated"}
    )

    assert response.status_code == 403


def test_update_other_user_task(test_db, test_user):
    """Test user cannot update another user's task."""
    # Create task for first user
    task = create_test_task(test_db, test_user["id"])

    # Try to update with different user's token
    other_user_id = uuid.uuid4()

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Hacked"},
        headers=get_auth_headers(other_user_id)
    )

    assert response.status_code == 404


def test_update_task_invalid_status(test_db, test_user):
    """Test updating task with invalid status returns 422."""
    task = create_test_task(test_db, test_user["id"])

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"status": "invalid_status"},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 422


def test_update_task_empty_title(test_db, test_user):
    """Test updating task with empty title returns 422."""
    task = create_test_task(test_db, test_user["id"])

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"title": ""},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 422


def test_update_task_title_too_long(test_db, test_user):
    """Test updating task with title exceeding max length returns 422."""
    task = create_test_task(test_db, test_user["id"])

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"title": "x" * 201},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 422


def test_update_task_updates_timestamp(test_db, test_user):
    """Test that updating a task updates the updated_at timestamp."""
    task = create_test_task(test_db, test_user["id"])
    original_updated_at = task.updated_at

    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(0.1)

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Updated"},
        headers=get_auth_headers(test_user["id"])
    )

    assert response.status_code == 200
    data = response.json()
    updated_at = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))

    # The updated_at should be more recent
    assert updated_at > original_updated_at
