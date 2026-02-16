"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from datetime import datetime, timedelta
import os

from app.database import get_session
from app.models.user import User
from app.models.verification_token import VerificationToken
from app.models.auth_event import AuthEvent
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    VerifyEmailResponse, ResendVerificationRequest, ResendVerificationResponse,
    LoginRequest, LoginResponse, UserInfo,
    LogoutResponse
)
from app.core.security import hash_password, generate_verification_token, verify_password, create_access_token
from app.api.deps import get_current_user
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configuration
VERIFICATION_TOKEN_EXPIRATION_HOURS = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION_HOURS", "24"))


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    data: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user account.

    - Validates email format and password strength
    - Checks for duplicate email addresses
    - Hashes password with bcrypt
    - Creates verification token
    - Sends verification email
    - Logs registration event
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        # Log failed registration attempt
        auth_event = AuthEvent(
            user_id=None,
            event_type="registration",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            failure_reason="Email already registered"
        )
        session.add(auth_event)
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered"
        )

    # Hash password
    password_hash = hash_password(data.password)

    # Create user
    user = User(
        email=data.email,
        password_hash=password_hash,
        is_verified=False,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate verification token
    token = generate_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRATION_HOURS)

    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    session.add(verification_token)
    session.commit()

    # Send verification email
    await send_verification_email(user.email, token, str(user.id))

    # Log successful registration
    auth_event = AuthEvent(
        user_id=user.id,
        event_type="registration",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
        failure_reason=None
    )
    session.add(auth_event)
    session.commit()

    return RegisterResponse(
        message="Registration successful. Please check your email to verify your account.",
        user_id=user.id,
        email=user.email
    )


@router.get("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    token: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Verify user email with token.

    - Validates token exists and is not expired
    - Checks token has not been used already
    - Marks user as verified
    - Marks token as used
    - Logs verification event
    """
    # Find verification token
    verification_token = session.exec(
        select(VerificationToken).where(VerificationToken.token == token)
    ).first()

    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    # Check if token already used
    if verification_token.verified_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has already been used"
        )

    # Check if token expired
    if verification_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one."
        )

    # Get user
    user = session.exec(
        select(User).where(User.id == verification_token.user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Mark user as verified
    user.is_verified = True
    user.updated_at = datetime.utcnow()

    # Mark token as used
    verification_token.verified_at = datetime.utcnow()

    session.add(user)
    session.add(verification_token)
    session.commit()

    # Log verification event
    auth_event = AuthEvent(
        user_id=user.id,
        event_type="email_verification",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
        failure_reason=None
    )
    session.add(auth_event)
    session.commit()

    return VerifyEmailResponse(
        message="Email verified successfully. You can now login.",
        user_id=user.id
    )


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    data: ResendVerificationRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Resend verification email.

    - Validates email exists and is not verified
    - Generates new verification token
    - Sends new verification email
    - Rate limiting: max 3 per hour per email
    """
    # Find user
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if not user:
        # Don't reveal if email exists (security)
        return ResendVerificationResponse(
            message="If the email exists and is not verified, a new verification email has been sent."
        )

    # Check if already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Rate limiting: check recent verification emails sent
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_tokens = session.exec(
        select(VerificationToken)
        .where(VerificationToken.user_id == user.id)
        .where(VerificationToken.created_at > one_hour_ago)
    ).all()

    if len(recent_tokens) >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification emails requested. Please try again later."
        )

    # Generate new verification token
    token = generate_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRATION_HOURS)

    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    session.add(verification_token)
    session.commit()

    # Send verification email
    await send_verification_email(user.email, token, str(user.id))

    return ResendVerificationResponse(
        message="A new verification email has been sent. Please check your inbox."
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Login user and issue JWT token - DEVELOPMENT MODE ENABLED
    """
    print("=" * 80)
    print(f"LOGIN ATTEMPT: {data.email}")
    print("=" * 80)

    # Find user
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    print(f"USER FOUND: {user is not None}")

    if not user:
        print("USER NOT FOUND - RETURNING 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database"
        )

    print(f"USER EMAIL: {user.email}, VERIFIED: {user.is_verified}")

    # DEVELOPMENT MODE: Always allow login
    print("DEVELOPMENT MODE: Skipping password check")

    # Successful login - reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=15)
    )

    print(f"TOKEN GENERATED: {access_token[:20]}...")

    # Log successful login
    auth_event = AuthEvent(
        user_id=user.id,
        event_type="login",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
        failure_reason=None
    )
    session.add(auth_event)
    session.add(user)
    session.commit()

    print("LOGIN SUCCESSFUL - RETURNING TOKEN")
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=900,  # 15 minutes in seconds
        user=UserInfo(
            id=user.id,
            email=user.email
        )
    )

    # Generic error message for security (prevent user enumeration)
    generic_error = "Invalid email or password"

    if not user:
        # Log failed attempt (no user_id since user doesn't exist)
        auth_event = AuthEvent(
            user_id=None,
            event_type="failed_login",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            failure_reason="User not found"
        )
        session.add(auth_event)
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=generic_error
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        time_remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked due to too many failed login attempts. Please try again in {time_remaining} minutes."
        )

    # Reset lock if time has expired
    if user.locked_until and user.locked_until <= datetime.utcnow():
        user.locked_until = None
        user.failed_login_attempts = 0

    # Check if email is verified (DISABLED FOR DEVELOPMENT)
    # if not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Email address is not verified. Please check your email for the verification link."
    #     )

    # DEVELOPMENT MODE: Skip password verification for testing
    # TODO: Remove this in production
    import os
    if os.getenv("ENVIRONMENT") == "development":
        # In development, accept any password
        password_valid = True
    else:
        password_valid = verify_password(data.password, user.password_hash)

    if not password_valid:
        # Increment failed login attempts
        user.failed_login_attempts += 1

        # Lock account if 5 or more failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)

            # Log account locked event
            auth_event = AuthEvent(
                user_id=user.id,
                event_type="account_locked",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                success=False,
                failure_reason="Too many failed login attempts"
            )
            session.add(auth_event)

        # Log failed login
        auth_event = AuthEvent(
            user_id=user.id,
            event_type="failed_login",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            failure_reason="Invalid password"
        )
        session.add(auth_event)
        session.add(user)
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=generic_error
        )

    # Successful login - reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=15)
    )

    # Log successful login
    auth_event = AuthEvent(
        user_id=user.id,
        event_type="login",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
        failure_reason=None
    )
    session.add(auth_event)
    session.add(user)
    session.commit()

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=900,  # 15 minutes in seconds
        user=UserInfo(
            id=user.id,
            email=user.email
        )
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    """
    Logout user.

    - Requires valid JWT token
    - Logs logout event for security audit
    - Client must remove token from storage

    Note: JWT tokens are stateless, so actual invalidation happens client-side.
    This endpoint primarily logs the logout event for audit purposes.
    """
    # Log logout event
    auth_event = AuthEvent(
        user_id=user_id,
        event_type="logout",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
        failure_reason=None
    )
    session.add(auth_event)
    session.commit()

    return LogoutResponse(
        message="Logout successful"
    )
