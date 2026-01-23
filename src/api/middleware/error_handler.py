"""Global exception handler middleware for FastAPI.

Transforms domain exceptions into RFC 7807 Problem Details responses.

This module provides the ErrorHandlerMiddleware class that centralizes
all exception handling logic, converting domain-specific exceptions
into standardized API error responses.

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

Example usage:
    >>> from fastapi import FastAPI
    >>> from api.middleware.error_handler import ErrorHandlerMiddleware
    >>>
    >>> app = FastAPI()
    >>> error_handler = ErrorHandlerMiddleware()
    >>> error_handler.register(app)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.exceptions import DomainError, ValidationError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.responses import Response

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """Centralized exception handling for FastAPI applications.

    This class provides RFC 7807 Problem Details compliant error responses
    for all exceptions, with specific handling for domain and validation
    exceptions.

    The middleware supports two modes of operation:
    1. Exception handlers: Registered via FastAPI's add_exception_handler
    2. Middleware mode: Wraps the entire request/response cycle

    Attributes:
        PROBLEM_JSON_MEDIA_TYPE: RFC 7807 standard media type for error responses.

    Example:
        >>> app = FastAPI()
        >>> error_handler = ErrorHandlerMiddleware()
        >>> error_handler.register(app)  # Register exception handlers
        >>>
        >>> # Or use as middleware
        >>> app.middleware("http")(error_handler.as_middleware())
    """

    PROBLEM_JSON_MEDIA_TYPE: str = "application/problem+json"

    async def handle_domain_exception(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle domain exceptions and return RFC 7807 Problem Details.

        Args:
            request: The incoming request that caused the exception.
            exc: The domain exception (typed as Exception for FastAPI compatibility).

        Returns:
            JSONResponse with RFC 7807 Problem Details format.
        """
        domain_exc = exc if isinstance(exc, DomainError) else DomainError(str(exc))

        logger.warning(
            "Domain exception occurred",
            extra={
                "error_code": domain_exc.error_code,
                "instance_id": domain_exc.instance_id,
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=domain_exc.HTTP_STATUS,
            content=domain_exc.to_problem_detail(),
            media_type=self.PROBLEM_JSON_MEDIA_TYPE,
        )

    async def handle_validation_exception(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle validation exceptions with field-level details.

        Args:
            request: The incoming request that caused the exception.
            exc: The validation exception (typed as Exception for FastAPI compatibility).

        Returns:
            JSONResponse with RFC 7807 Problem Details including invalid-params.
        """
        validation_exc = (
            exc
            if isinstance(exc, ValidationError)
            else ValidationError(field="unknown", reason=str(exc))
        )

        logger.info(
            "Validation failed",
            extra={
                "field": validation_exc.field,
                "reason": validation_exc.reason,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=validation_exc.HTTP_STATUS,
            content=validation_exc.to_problem_detail(),
            media_type=self.PROBLEM_JSON_MEDIA_TYPE,
        )

    async def handle_unhandled_exception(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions safely.

        Never exposes internal details to the client. Logs full exception
        details for debugging while returning a generic error message.

        Args:
            request: The incoming request that caused the exception.
            exc: The unhandled exception.

        Returns:
            Generic 500 error response in RFC 7807 format.
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
            media_type=self.PROBLEM_JSON_MEDIA_TYPE,
        )

    def register(self, app: FastAPI) -> None:
        """Register all exception handlers with the FastAPI application.

        Handlers are registered in order of specificity (most specific first)
        to ensure proper exception routing by FastAPI.

        Args:
            app: The FastAPI application instance.

        Example:
            >>> from fastapi import FastAPI
            >>> from api.middleware.error_handler import ErrorHandlerMiddleware
            >>>
            >>> app = FastAPI()
            >>> ErrorHandlerMiddleware().register(app)
        """
        app.add_exception_handler(
            ValidationError,
            self.handle_validation_exception,
        )
        app.add_exception_handler(
            DomainError,
            self.handle_domain_exception,
        )
        app.add_exception_handler(
            Exception,
            self.handle_unhandled_exception,
        )

    def as_middleware(
        self,
    ) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
        """Return a middleware function for HTTP error handling.

        This is an alternative to exception handlers that catches errors
        at the middleware level, useful when you need to intercept errors
        before they reach FastAPI's exception handling.

        Returns:
            Async middleware function compatible with FastAPI's middleware system.

        Example:
            >>> app = FastAPI()
            >>> error_handler = ErrorHandlerMiddleware()
            >>> app.middleware("http")(error_handler.as_middleware())
        """

        async def middleware(
            request: Request,
            call_next: Callable[[Request], Awaitable[Response]],
        ) -> Response:
            try:
                return await call_next(request)
            except ValidationError as exc:
                return await self.handle_validation_exception(request, exc)
            except DomainError as exc:
                return await self.handle_domain_exception(request, exc)
            except Exception as exc:
                return await self.handle_unhandled_exception(request, exc)

        return middleware
