"""API dependencies for authentication and database sessions."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Generator
import uuid

from app.database import get_session
from app.core.security import verify_token

# HTTP Bearer token security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> uuid.UUID:
    """
    Extract and validate user ID from JWT token.

    This dependency validates the JWT token and extracts the user_id.
    User isolation is enforced by using this user_id in all database queries.

    Args:
        credentials: HTTP Bearer credentials containing JWT token

    Returns:
        user_id: UUID of the authenticated user

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    token = credentials.credentials
    user_id_str = verify_token(token)

    try:
        user_id = uuid.UUID(user_id_str)
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    Yields:
        Database session
    """
    yield from get_session()
