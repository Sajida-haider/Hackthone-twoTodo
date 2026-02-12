"""Tests for task creation endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
import uuid

def test_create_task_with_valid_data(authenticated_client: TestClient, test_user_id: uuid.UUID):
    """Test task creation with valid data returns 201."""
    response = authenticated_client.post(
        "/api/v1/tasks",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "due_date": "2026-02-15T10:00:00Z"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["status"] == "pending"
    assert data["user_id"] == str(test_user_id)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_task_without_token_returns_401(client: TestClient):
    """Test task creation without token returns 401."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Buy groceries"}
    )

    assert response.status_code == 401

def test_create_task_with_empty_title_returns_400(authenticated_client: TestClient):
    """Test task creation with empty title returns 400."""
    response = authenticated_client.post(
        "/api/v1/tasks",
        json={"title": ""}
    )

    assert response.status_code == 422  # Pydantic validation error

def test_create_task_defaults_to_pending_status(authenticated_client: TestClient):
    """Test task defaults to 'pending' status."""
    response = authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Test task"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"

def test_create_task_associates_with_authenticated_user(
    authenticated_client: TestClient,
    test_user_id: uuid.UUID
):
    """Test task associates with authenticated user."""
    response = authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Test task"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(test_user_id)

def test_create_task_with_only_title(authenticated_client: TestClient):
    """Test task creation with only required title field."""
    response = authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Minimal task"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal task"
    assert data["description"] is None
    assert data["due_date"] is None
