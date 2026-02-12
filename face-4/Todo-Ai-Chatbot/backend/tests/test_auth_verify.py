"""Tests for email verification endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.user import User
from app.models.verification_token import VerificationToken
from app.core.security import hash_password, generate_verification_token


@pytest.mark.auth
def test_successful_verification(client: TestClient, session: Session):
    """Test successful email verification."""
    # Create user
    user = User(
        email="verify@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=False,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create verification token
    token = generate_verification_token()
    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    session.add(verification_token)
    session.commit()

    # Verify email
    response = client.get(f"/api/v1/auth/verify-email?token={token}")

    assert response.status_code == 200
    data = response.json()
    assert "verified successfully" in data["message"].lower()
    assert data["user_id"] == str(user.id)

    # Check user is verified
    session.refresh(user)
    assert user.is_verified is True

    # Check token is marked as used
    session.refresh(verification_token)
    assert verification_token.verified_at is not None


@pytest.mark.auth
def test_invalid_token_rejection(client: TestClient):
    """Test that invalid tokens are rejected."""
    response = client.get("/api/v1/auth/verify-email?token=invalid-token-12345")

    assert response.status_code == 400
    data = response.json()
    assert "invalid" in data["detail"].lower() or "not found" in data["detail"].lower()


@pytest.mark.auth
def test_expired_token_rejection(client: TestClient, session: Session):
    """Test that expired tokens are rejected."""
    # Create user
    user = User(
        email="expired@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=False,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create expired verification token
    token = generate_verification_token()
    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    )
    session.add(verification_token)
    session.commit()

    # Try to verify with expired token
    response = client.get(f"/api/v1/auth/verify-email?token={token}")

    assert response.status_code == 400
    data = response.json()
    assert "expired" in data["detail"].lower()

    # User should still be unverified
    session.refresh(user)
    assert user.is_verified is False


@pytest.mark.auth
def test_already_verified_account(client: TestClient, session: Session):
    """Test verification of already verified account."""
    # Create verified user
    user = User(
        email="already@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=True,  # Already verified
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create verification token
    token = generate_verification_token()
    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        verified_at=datetime.utcnow()  # Already used
    )
    session.add(verification_token)
    session.commit()

    # Try to verify again
    response = client.get(f"/api/v1/auth/verify-email?token={token}")

    assert response.status_code == 400
    data = response.json()
    assert "already" in data["detail"].lower()


@pytest.mark.auth
def test_token_single_use_enforcement(client: TestClient, session: Session):
    """Test that tokens can only be used once."""
    # Create user
    user = User(
        email="singleuse@example.com",
        password_hash=hash_password("SecurePass123!"),
        is_verified=False,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create verification token
    token = generate_verification_token()
    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    session.add(verification_token)
    session.commit()

    # First verification - should succeed
    response1 = client.get(f"/api/v1/auth/verify-email?token={token}")
    assert response1.status_code == 200

    # Second verification with same token - should fail
    response2 = client.get(f"/api/v1/auth/verify-email?token={token}")
    assert response2.status_code == 400
    data = response2.json()
    assert "already" in data["detail"].lower()
