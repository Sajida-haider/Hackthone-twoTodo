"""Tests for user login endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.user import User
from app.core.security import hash_password


@pytest.mark.auth
def test_successful_login(client: TestClient, session: Session):
    """Test successful user login."""
    # Create verified user
    user = User(
        email="login@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 900  # 15 minutes in seconds
    assert data["user"]["email"] == "login@example.com"


@pytest.mark.auth
def test_invalid_credentials_rejection(client: TestClient, session: Session):
    """Test that invalid credentials are rejected."""
    # Create verified user
    user = User(
        email="test@example.com",
        password_hash=hash_password("CorrectPass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPass123!"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "incorrect" in data["detail"].lower()


@pytest.mark.auth
def test_unverified_email_rejection(client: TestClient, session: Session):
    """Test that unverified users cannot login."""
    # Create unverified user
    user = User(
        email="unverified@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=False,  # Not verified
        is_active=True
    )
    session.add(user)
    session.commit()

    # Try to login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unverified@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 403
    data = response.json()
    assert "verify" in data["detail"].lower() or "not verified" in data["detail"].lower()


@pytest.mark.auth
def test_account_lockout_after_5_failures(client: TestClient, session: Session):
    """Test that account is locked after 5 failed login attempts."""
    # Create verified user
    user = User(
        email="lockout@example.com",
        password_hash=hash_password("CorrectPass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Make 5 failed login attempts
    for i in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "lockout@example.com",
                "password": "WrongPass123!"
            }
        )
        assert response.status_code == 401

    # 6th attempt should return locked status
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "lockout@example.com",
            "password": "CorrectPass123!"  # Even with correct password
        }
    )

    assert response.status_code == 403
    data = response.json()
    assert "locked" in data["detail"].lower()

    # Verify user is locked in database
    session.refresh(user)
    assert user.failed_login_attempts >= 5
    assert user.locked_until is not None


@pytest.mark.auth
def test_locked_account_rejection(client: TestClient, session: Session):
    """Test that locked accounts cannot login."""
    # Create locked user
    user = User(
        email="locked@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True,
        failed_login_attempts=5,
        locked_until=datetime.utcnow() + timedelta(minutes=15)
    )
    session.add(user)
    session.commit()

    # Try to login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "locked@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 403
    data = response.json()
    assert "locked" in data["detail"].lower()


@pytest.mark.auth
def test_failed_attempt_counter_reset_on_success(client: TestClient, session: Session):
    """Test that failed login attempts counter resets on successful login."""
    # Create verified user with some failed attempts
    user = User(
        email="reset@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True,
        failed_login_attempts=3
    )
    session.add(user)
    session.commit()

    # Successful login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "reset@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200

    # Verify counter was reset
    session.refresh(user)
    assert user.failed_login_attempts == 0
    assert user.last_login_at is not None


@pytest.mark.auth
def test_jwt_token_structure_and_expiration(client: TestClient, session: Session):
    """Test JWT token structure and expiration."""
    # Create verified user
    user = User(
        email="jwt@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,
        is_active=True
    )
    session.add(user)
    session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "jwt@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify token structure
    token = data["access_token"]
    assert isinstance(token, str)
    assert len(token) > 0
    assert token.count('.') == 2  # JWT has 3 parts separated by dots

    # Verify expiration
    assert data["expires_in"] == 900  # 15 minutes
    assert data["token_type"] == "bearer"
