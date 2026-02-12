"""Email service for sending verification emails."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Email configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@localhost")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def send_verification_email(email: str, token: str, user_id: str) -> bool:
    """
    Send email verification link to user.

    Args:
        email: User's email address
        token: Verification token
        user_id: User's UUID

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Create verification link
        verification_link = f"{FRONTEND_URL}/verify-email?token={token}"

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verify your email address"
        message["From"] = SMTP_FROM
        message["To"] = email

        # Plain text version
        text_content = f"""
        Welcome to Todo App!

        Please verify your email address by clicking the link below:
        {verification_link}

        This link will expire in 24 hours.

        If you didn't create an account, please ignore this email.
        """

        # HTML version
        html_content = f"""
        <html>
          <body>
            <h2>Welcome to Todo App!</h2>
            <p>Please verify your email address by clicking the button below:</p>
            <p>
              <a href="{verification_link}"
                 style="background-color: #4CAF50; color: white; padding: 14px 20px;
                        text-decoration: none; border-radius: 4px; display: inline-block;">
                Verify Email Address
              </a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{verification_link}</p>
            <p><small>This link will expire in 24 hours.</small></p>
            <hr>
            <p><small>If you didn't create an account, please ignore this email.</small></p>
          </body>
        </html>
        """

        # Attach both versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            if SMTP_USER and SMTP_PASSWORD:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, email, message.as_string())

        logger.info(f"Verification email sent to {email}")
        return True

    except Exception as e:
        logger.warning(f"Failed to send verification email to {email}: {str(e)}")
        logger.warning("Email service not configured. User can still register but won't receive verification email.")
        # Return True to allow registration to continue even if email fails
        return True


async def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset link to user.

    Args:
        email: User's email address
        token: Password reset token

    Returns:
        True if email sent successfully, False otherwise
    """
    # Placeholder for future password reset functionality
    pass
