"""Tests for user logout endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User
from app.core.security import hash_password


@pytest.mark.auth
def test_successful_logout(authenticated_client: TestClient, session: Session, test_user_id):
    """Test successful user logout."""
    # Create user
    user = User(
        id=test_user_id,
        email="logout@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Logout
    response = authenticated_client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    data = response.json()
    assert "logout successful" in data["message"].lower()


@pytest.mark.auth
def test_logout_requires_authentication(client: TestClient):
    """Test that logout requires valid JWT token."""
    # Try to logout without token
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 403  # Forbidden (no credentials)


@pytest.mark.auth
def test_logout_with_invalid_token(client: TestClient):
    """Test that logout with invalid token is rejected."""
    # Try to logout with invalid token
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid-token-12345"}
    )

    assert response.status_code == 401
