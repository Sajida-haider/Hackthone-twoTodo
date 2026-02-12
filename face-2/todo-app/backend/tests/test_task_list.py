"""Tests for task list and get endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
import uuid

def test_list_tasks_returns_only_user_tasks(
    authenticated_client: TestClient,
    test_user_id: uuid.UUID,
    session: Session
):
    """Test list returns only authenticated user's tasks."""
    # Create tasks for test user
    authenticated_client.post("/api/v1/tasks", json={"title": "Task 1"})
    authenticated_client.post("/api/v1/tasks", json={"title": "Task 2"})
    authenticated_client.post("/api/v1/tasks", json={"title": "Task 3"})

    response = authenticated_client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(task["user_id"] == str(test_user_id) for task in data)

def test_list_tasks_returns_empty_array_for_no_tasks(authenticated_client: TestClient):
    """Test list returns empty array for user with no tasks."""
    response = authenticated_client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert data == []

def test_list_tasks_without_token_returns_401(client: TestClient):
    """Test list without token returns 401."""
    response = client.get("/api/v1/tasks")

    assert response.status_code == 401

def test_get_task_returns_200_for_owned_task(authenticated_client: TestClient):
    """Test get task returns 200 for owned task."""
    # Create a task
    create_response = authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Test task"}
    )
    task_id = create_response.json()["id"]

    # Get the task
    response = authenticated_client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test task"

def test_get_task_returns_404_for_nonexistent_task(authenticated_client: TestClient):
    """Test get task returns 404 for non-existent task."""
    fake_id = str(uuid.uuid4())
    response = authenticated_client.get(f"/api/v1/tasks/{fake_id}")

    assert response.status_code == 404

def test_get_task_without_token_returns_401(client: TestClient):
    """Test get task without token returns 401."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/tasks/{fake_id}")

    assert response.status_code == 401

def test_list_tasks_ordered_by_created_at(authenticated_client: TestClient):
    """Test tasks are ordered by creation date (newest first)."""
    # Create tasks in sequence
    authenticated_client.post("/api/v1/tasks", json={"title": "First"})
    authenticated_client.post("/api/v1/tasks", json={"title": "Second"})
    authenticated_client.post("/api/v1/tasks", json={"title": "Third"})

    response = authenticated_client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    # Newest first
    assert data[0]["title"] == "Third"
    assert data[1]["title"] == "Second"
    assert data[2]["title"] == "First"
