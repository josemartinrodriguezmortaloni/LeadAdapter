"""Global exception handler middleware for FastAPI.

Transforms domain exceptions into RFC 7807 Problem Details responses.

Reference:
    https://datatracker.ietf.org/doc/html/rfc7807

Example response:
    {
        "type": "https://api.leadadapter.com/errors/validation",
        "title": "Validation Error",
        "status": 422,
        "detail": "first_name: cannot be empty",
        "instance": "/errors/abc123-def456",
        "invalid-params": [{"name": "first_name", "reason": "cannot be empty"}]
    }
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.exceptions import DomainException, ValidationException

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

# RFC 7807 media type
PROBLEM_JSON_MEDIA_TYPE = "application/problem+json"


async def domain_exception_handler(
    request: Request,
    exc: DomainException,
) -> JSONResponse:
    """Handle domain exceptions and return RFC 7807 Problem Details.

    Args:
        request: The incoming request that caused the exception.
        exc: The domain exception to handle.

    Returns:
        JSONResponse with RFC 7807 Problem Details format.
    """
    # Log with context for debugging (internal details only)
    logger.warning(
        "Domain exception occurred",
        extra={
            "error_code": exc.error_code,
            "instance_id": exc.instance_id,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.HTTP_STATUS,
        content=exc.to_problem_detail(),
        media_type=PROBLEM_JSON_MEDIA_TYPE,
    )


async def validation_exception_handler(
    request: Request,
    exc: ValidationException,
) -> JSONResponse:
    """Handle validation exceptions with field-level details.

    Args:
        request: The incoming request that caused the exception.
        exc: The validation exception to handle.

    Returns:
        JSONResponse with RFC 7807 Problem Details including invalid-params.
    """
    logger.info(
        "Validation failed",
        extra={
            "field": exc.field,
            "reason": exc.reason,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=exc.HTTP_STATUS,
        content=exc.to_problem_detail(),
        media_type=PROBLEM_JSON_MEDIA_TYPE,
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions safely.

    Never exposes internal details to the client.

    Args:
        request: The incoming request that caused the exception.
        exc: The unhandled exception.

    Returns:
        Generic 500 error response.
    """
    logger.exception(
        "Unhandled exception occurred",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "type": "https://api.leadadapter.com/errors/internal",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred. Please try again later.",
        },
        media_type=PROBLEM_JSON_MEDIA_TYPE,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application.

    Args:
        app: The FastAPI application instance.

    Example:
        >>> from fastapi import FastAPI
        >>> from api.middleware.error_handler import register_exception_handlers
        >>> app = FastAPI()
        >>> register_exception_handlers(app)
    """
    # Order matters: more specific handlers first
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


def create_error_handling_middleware(
    app: FastAPI,
) -> Callable[[Request, Callable], Awaitable[JSONResponse]]:
    """Create middleware for consistent error handling.

    This is an alternative to exception handlers that catches errors
    at the middleware level, useful for logging and tracing.

    Args:
        app: The FastAPI application instance.

    Returns:
        Middleware function.
    """

    async def error_handling_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[JSONResponse]],
    ) -> JSONResponse:
        try:
            return await call_next(request)
        except DomainException as exc:
            return await domain_exception_handler(request, exc)
        except Exception as exc:
            return await unhandled_exception_handler(request, exc)

    return error_handling_middleware
