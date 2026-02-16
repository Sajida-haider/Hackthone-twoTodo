"""Environment variable validation on application startup."""
import os
import sys
from typing import List, Tuple

def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate required environment variables are set.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Required variables
    required_vars = {
        "DATABASE_URL": "Database connection string",
        "BETTER_AUTH_SECRET": "JWT signing secret (min 32 characters)",
    }

    # Optional but recommended variables
    recommended_vars = {
        "SMTP_HOST": "Email server host",
        "SMTP_PORT": "Email server port",
        "SMTP_FROM": "Email sender address",
        "FRONTEND_URL": "Frontend application URL",
    }

    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"[X] Missing required variable: {var} ({description})")
        elif var == "BETTER_AUTH_SECRET" and len(value) < 32:
            errors.append(f"[X] {var} must be at least 32 characters long")

    # Check recommended variables (warnings only)
    warnings = []
    for var, description in recommended_vars.items():
        if not os.getenv(var):
            warnings.append(f"[!] Missing recommended variable: {var} ({description})")

    # Print results
    if errors:
        print("\n[ERROR] Environment Validation Failed:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print("\n[WARNING] Environment Warnings:")
        for warning in warnings:
            print(f"  {warning}")

    if not errors and not warnings:
        print("[OK] Environment validation passed!")

    return len(errors) == 0, errors

def check_environment_on_startup():
    """Check environment variables on application startup."""
    is_valid, errors = validate_environment()

    if not is_valid:
        print("\n[WARNING] Some required environment variables are missing.")
        print("The application will start but some features may not work correctly.")
        print("Please set the following environment variables:")
        for error in errors:
            print(f"  {error}")
        # Don't exit in production - let the app start with warnings
        # sys.exit(1)

if __name__ == "__main__":
    check_environment_on_startup()
