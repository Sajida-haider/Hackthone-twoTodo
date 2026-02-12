"""Tests for JWT authentication middleware."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta
from app.models.user import User
from app.core.security import hash_password, create_access_token


@pytest.mark.auth
def test_valid_token_access(authenticated_client: TestClient, session: Session, test_user_id):
    """Test that valid JWT token grants access to protected endpoints."""
    # Create user
    user = User(
        id=test_user_id,
        email="protected@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Access protected endpoint (tasks list)
    response = authenticated_client.get("/api/v1/tasks")

    assert response.status_code == 200


@pytest.mark.auth
def test_missing_token_rejection(client: TestClient):
    """Test that requests without JWT token are rejected."""
    # Try to access protected endpoint without token
    response = client.get("/api/v1/tasks")

    assert response.status_code == 403  # Forbidden (no credentials provided)


@pytest.mark.auth
def test_invalid_token_rejection(client: TestClient):
    """Test that invalid JWT tokens are rejected."""
    # Try to access with invalid token
    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": "Bearer invalid-token-12345"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "token" in data["detail"].lower()


@pytest.mark.auth
def test_expired_token_rejection(client: TestClient, session: Session):
    """Test that expired JWT tokens are rejected."""
    # Create user
    user = User(
        email="expired@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Create expired token (expired 1 hour ago)
    expired_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(hours=-1)
    )

    # Try to access with expired token
    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()


@pytest.mark.auth
def test_tampered_token_rejection(client: TestClient, session: Session):
    """Test that tampered JWT tokens are rejected."""
    # Create user
    user = User(
        email="tamper@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Create valid token
    valid_token = create_access_token(data={"sub": str(user.id)})

    # Tamper with token (change last character)
    tampered_token = valid_token[:-1] + "X"

    # Try to access with tampered token
    response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {tampered_token}"}
    )

    assert response.status_code == 401


@pytest.mark.auth
def test_user_extraction_from_token(authenticated_client: TestClient, session: Session, test_user_id):
    """Test that user ID is correctly extracted from JWT token."""
    # Create user
    user = User(
        id=test_user_id,
        email="extract@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Create a task (which requires authenticated user)
    response = authenticated_client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description"
        }
    )

    assert response.status_code == 201
    data = response.json()
    # Verify task is associated with correct user
    assert data["user_id"] == str(test_user_id)
