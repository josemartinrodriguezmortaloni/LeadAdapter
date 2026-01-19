"""Domain exceptions for LeadAdapter."""

from domain.exceptions.domain_exceptions import (
    DomainException,
    InvalidLeadError,
    InvalidMessageError,
    InvalidPlaybookError,
    InvalidProductError,
    InvalidSenderError,
    InvalidWorkExperienceError,
    NoMatchingICPError,
    QualityThresholdNotMetError,
    ValidationException,
)

__all__ = [
    "DomainException",
    "InvalidLeadError",
    "InvalidMessageError",
    "InvalidPlaybookError",
    "InvalidProductError",
    "InvalidSenderError",
    "InvalidWorkExperienceError",
    "NoMatchingICPError",
    "QualityThresholdNotMetError",
    "ValidationException",
]
