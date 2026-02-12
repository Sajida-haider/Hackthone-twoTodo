"""Logging middleware for request/response tracking."""
import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

# Configure logger
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details and response status."""
        # Start timer
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status={response.status_code} duration={duration:.3f}s"
            )

            return response

        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"error={str(e)} duration={duration:.3f}s",
                exc_info=True
            )
            raise
