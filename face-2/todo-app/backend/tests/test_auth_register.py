"""Tests for user registration endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from app.models.verification_token import VerificationToken
from app.models.auth_event import AuthEvent


@pytest.mark.auth
def test_successful_registration(client: TestClient, session: Session):
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Registration successful. Please check your email to verify your account."
    assert data["email"] == "test@example.com"
    assert "user_id" in data

    # Verify user was created in database
    user = session.exec(select(User).where(User.email == "test@example.com")).first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.is_verified is False
    assert user.is_active is True


@pytest.mark.auth
def test_duplicate_email_rejection(client: TestClient, session: Session):
    """Test that duplicate email addresses are rejected."""
    # Create first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!"
        }
    )

    # Try to create second user with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "DifferentPass456!"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "already registered" in data["detail"].lower()


@pytest.mark.auth
def test_invalid_email_format(client: TestClient):
    """Test that invalid email formats are rejected."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.auth
def test_weak_password_rejection(client: TestClient):
    """Test that weak passwords are rejected."""
    # Password too short (less than 8 characters)
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Short1!"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.auth
def test_verification_email_sent(client: TestClient, session: Session):
    """Test that verification email is sent on registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "verify@example.com",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 201

    # Verify token was created
    user = session.exec(select(User).where(User.email == "verify@example.com")).first()
    assert user is not None

    token = session.exec(
        select(VerificationToken).where(VerificationToken.user_id == user.id)
    ).first()
    assert token is not None
    assert token.verified_at is None
    assert token.expires_at is not None


@pytest.mark.auth
def test_password_hashing_no_plaintext(client: TestClient, session: Session):
    """Test that passwords are hashed and never stored in plaintext."""
    password = "SecurePass123!"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "hash@example.com",
            "password": password
        }
    )

    assert response.status_code == 201

    # Verify password is hashed in database
    user = session.exec(select(User).where(User.email == "hash@example.com")).first()
    assert user is not None
    assert user.password_hash != password
    assert user.password_hash.startswith("$2b$")  # bcrypt hash prefix
    assert len(user.password_hash) == 60  # bcrypt hash length
