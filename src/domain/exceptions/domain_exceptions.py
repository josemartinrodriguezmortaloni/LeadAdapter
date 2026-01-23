"""Domain exceptions with structured context for LeadAdapter.

This module provides a hierarchy of domain exceptions that support:
- Structured attributes for programmatic access (e.g., field, reason)
- RFC 7807 Problem Details serialization for API responses
- Backward-compatible string representation

Architecture:
    DomainError (base)
    ├── ValidationError (field, reason) HTTP 422
    │   ├── InvalidLeadError
    │   ├── InvalidPlaybookError
    │   ├── InvalidMessageError
    │   ├── InvalidSenderError
    │   ├── InvalidProductError
    │   └── InvalidWorkExperienceError
    ├── QualityThresholdNotMetError (score, threshold) HTTP 422
    └── NoMatchingICPError (lead_criteria) HTTP 404
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar


class DomainError(Exception):
    """Base exception for all domain errors.

    Provides structured error handling with:
    - Unique instance ID for tracing
    - Timestamp for logging
    - HTTP status code mapping
    - RFC 7807 Problem Details serialization

    Attributes:
        message: Human-readable error description.
        HTTP_STATUS: HTTP status code for API responses (default 500).
        ERROR_TYPE: URI identifying the error type (RFC 7807).
        ERROR_TITLE: Short human-readable title (RFC 7807).

    Example:
        >>> e = DomainError("Something went wrong")
        >>> e.to_dict()
        {'error_code': 'DOMAIN', 'message': 'Something went wrong', ...}
    """

    HTTP_STATUS: ClassVar[int] = 500
    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/domain"
    ERROR_TITLE: ClassVar[str] = "Domain Error"

    __slots__ = ("message", "instance_id", "timestamp")

    def __init__(self, message: str = "") -> None:
        """Initialize domain exception.

        Args:
            message: Human-readable error description.
        """
        self.message = message
        self.instance_id = str(uuid.uuid4())
        self.timestamp = datetime.now(UTC).isoformat()
        super().__init__(message)

    @property
    def error_code(self) -> str:
        """Derive error code from class name.

        Returns:
            UPPER_SNAKE_CASE error code (e.g., INVALID_LEAD).
        """
        name = self.__class__.__name__.replace("Exception", "").replace("Error", "")
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON responses.

        Returns:
            Dictionary with error_code, message, and timestamp.
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp,
        }

    def to_problem_detail(self) -> dict[str, Any]:
        """Serialize to RFC 7807 Problem Details format.

        Returns:
            Dictionary conforming to RFC 7807 specification.

        Reference:
            https://datatracker.ietf.org/doc/html/rfc7807
        """
        return {
            "type": self.ERROR_TYPE,
            "title": self.ERROR_TITLE,
            "status": self.HTTP_STATUS,
            "detail": self.message,
            "instance": f"/errors/{self.instance_id}",
        }

    def __str__(self) -> str:
        """Return human-readable message."""
        return self.message

    def __repr__(self) -> str:
        """Return debug representation."""
        return f"{self.__class__.__name__}({self.error_code!r}, {self.message!r})"


class ValidationError(DomainError):
    """Base exception for validation errors.

    All validation exceptions share field and reason attributes,
    enabling structured error responses for API clients.

    Attributes:
        field: Name of the invalid field.
        reason: Description of why validation failed.

    Example:
        >>> e = ValidationError(field="email", reason="invalid format")
        >>> e.field
        'email'
        >>> str(e)
        'email: invalid format'
    """

    HTTP_STATUS: ClassVar[int] = 422
    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/validation"
    ERROR_TITLE: ClassVar[str] = "Validation Error"

    __slots__ = ("field", "reason")

    def __init__(self, field: str, reason: str) -> None:
        """Initialize validation exception.

        Args:
            field: Name of the invalid field.
            reason: Description of why validation failed.
        """
        self.field = field
        self.reason = reason
        super().__init__(f"{field}: {reason}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize with field and reason."""
        base = super().to_dict()
        base["field"] = self.field
        base["reason"] = self.reason
        return base

    def to_problem_detail(self) -> dict[str, Any]:
        """Serialize with invalid-params extension (RFC 7807)."""
        base = super().to_problem_detail()
        base["invalid-params"] = [{"name": self.field, "reason": self.reason}]
        return base


class InvalidLeadError(ValidationError):
    """Lead data is invalid or incomplete.

    Raised when Lead entity validation fails.

    Example:
        >>> raise InvalidLeadError(field="first_name", reason="cannot be empty")
    """

    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/lead-validation"


class InvalidPlaybookError(ValidationError):
    """Playbook configuration is invalid.

    Raised when Playbook entity validation fails.

    Example:
        >>> raise InvalidPlaybookError(field="products", reason="cannot be empty")
    """

    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/playbook-validation"


class InvalidMessageError(ValidationError):
    """Message data is invalid or incomplete.

    Raised when Message entity validation fails.

    Example:
        >>> raise InvalidMessageError(field="content", reason="cannot be empty")
    """

    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/message-validation"


class InvalidSenderError(ValidationError):
    """Sender data is invalid or incomplete.

    Raised when Sender entity validation fails.

    Example:
        >>> raise InvalidSenderError(field="name", reason="cannot be empty")
    """

    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/sender-validation"


class InvalidProductError(ValidationError):
    """Product data is invalid or incomplete.

    Raised when Product value object validation fails.

    Example:
        >>> raise InvalidProductError(field="name", reason="cannot be empty")
    """

    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/product-validation"


class InvalidWorkExperienceError(ValidationError):
    """Work experience data is invalid or incomplete.

    Raised when WorkExperience value object validation fails.

    Example:
        >>> raise InvalidWorkExperienceError(field="company", reason="cannot be empty")
    """

    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/work-experience-validation"


class QualityThresholdNotMetError(DomainError):
    """Message quality score below threshold.

    Raised when message generation fails to meet quality standards
    after maximum retry attempts.

    Attributes:
        score: The best score achieved.
        threshold: The minimum required score.

    Example:
        >>> e = QualityThresholdNotMetError(score=5.0, threshold=7.0)
        >>> e.score
        5.0
    """

    HTTP_STATUS: ClassVar[int] = 422
    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/quality-threshold-not-met"
    ERROR_TITLE: ClassVar[str] = "Quality Threshold Not Met"

    __slots__ = ("score", "threshold")

    def __init__(self, score: float, threshold: float, message: str = "") -> None:
        """Initialize quality threshold error.

        Args:
            score: The best score achieved.
            threshold: The minimum required score.
            message: Optional additional context.
        """
        self.score = score
        self.threshold = threshold
        full_message = f"Quality score {score} below threshold {threshold}"
        if message:
            full_message = f"{full_message}. {message}"
        super().__init__(full_message)

    def to_dict(self) -> dict[str, Any]:
        """Serialize with score and threshold."""
        base = super().to_dict()
        base["score"] = self.score
        base["threshold"] = self.threshold
        return base

    def to_problem_detail(self) -> dict[str, Any]:
        """Serialize with score extension."""
        base = super().to_problem_detail()
        base["score"] = self.score
        base["threshold"] = self.threshold
        return base


class NoMatchingICPError(DomainError):
    """No ICP matches the given lead.

    Raised when lead qualification fails to find a matching
    Ideal Customer Profile.

    Attributes:
        lead_criteria: The criteria used for matching.

    Example:
        >>> e = NoMatchingICPError(lead_criteria={"industry": "Tech"})
        >>> e.lead_criteria
        {'industry': 'Tech'}
    """

    HTTP_STATUS: ClassVar[int] = 404
    ERROR_TYPE: ClassVar[str] = "https://api.leadadapter.com/errors/no-matching-icp"
    ERROR_TITLE: ClassVar[str] = "No Matching ICP"

    __slots__ = ("lead_criteria",)

    def __init__(self, lead_criteria: dict[str, Any] | None = None, message: str = "") -> None:
        """Initialize no matching ICP error.

        Args:
            lead_criteria: The criteria used for matching.
            message: Optional custom message.
        """
        self.lead_criteria = lead_criteria or {}
        default_message = "No ICP matches the given lead criteria"
        super().__init__(message or default_message)

    def to_dict(self) -> dict[str, Any]:
        """Serialize with lead criteria."""
        base = super().to_dict()
        base["lead_criteria"] = self.lead_criteria
        return base

    def to_problem_detail(self) -> dict[str, Any]:
        """Serialize with lead criteria extension."""
        base = super().to_problem_detail()
        base["lead_criteria"] = self.lead_criteria
        return base
