"""Database seed script for creating test users."""
from sqlmodel import Session, create_engine
from app.models.user import User
from app.models.verification_token import VerificationToken
from app.core.security import hash_password, generate_verification_token
from datetime import datetime, timedelta
import os
import uuid

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_db")

def seed_test_users():
    """Create test users for development and testing."""
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        # Test user 1: Verified and active
        user1 = User(
            email="test@example.com",
            password_hash=hash_password("TestPass123!"),
            is_verified=True,
            is_active=True
        )
        session.add(user1)

        # Test user 2: Unverified (needs email verification)
        user2 = User(
            email="unverified@example.com",
            password_hash=hash_password("TestPass123!"),
            is_verified=False,
            is_active=True
        )
        session.add(user2)
        session.flush()

        # Create verification token for user2
        token = generate_verification_token()
        verification_token = VerificationToken(
            user_id=user2.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        session.add(verification_token)

        # Test user 3: Locked account
        user3 = User(
            email="locked@example.com",
            password_hash=hash_password("TestPass123!"),
            is_verified=True,
            is_active=True,
            failed_login_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=15)
        )
        session.add(user3)

        session.commit()

        print("✅ Test users created successfully!")
        print("\nTest Users:")
        print("1. test@example.com (verified, active) - Password: TestPass123!")
        print("2. unverified@example.com (not verified) - Password: TestPass123!")
        print(f"   Verification token: {token}")
        print("3. locked@example.com (locked for 15 min) - Password: TestPass123!")

if __name__ == "__main__":
    seed_test_users()
