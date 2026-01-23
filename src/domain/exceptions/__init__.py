"""Domain exceptions for LeadAdapter."""

from domain.exceptions.domain_exceptions import (
    DomainError,
    InvalidLeadError,
    InvalidMessageError,
    InvalidPlaybookError,
    InvalidProductError,
    InvalidSenderError,
    InvalidWorkExperienceError,
    NoMatchingICPError,
    QualityThresholdNotMetError,
    ValidationError,
)

__all__ = [
    "DomainError",
    "InvalidLeadError",
    "InvalidMessageError",
    "InvalidPlaybookError",
    "InvalidProductError",
    "InvalidSenderError",
    "InvalidWorkExperienceError",
    "NoMatchingICPError",
    "QualityThresholdNotMetError",
    "ValidationError",
]
