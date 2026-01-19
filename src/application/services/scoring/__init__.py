"""
Scoring criteria module for message quality evaluation.

This module provides a Strategy Pattern implementation for scoring
message quality across multiple dimensions. Each criterion is an
independent, pluggable strategy that can be composed into a scorer.

Usage:
    from application.services.scoring import (
        ScoringCriterion,
        PersonalizationCriterion,
        AntiSpamCriterion,
        StructureCriterion,
        ToneCriterion,
        DEFAULT_CRITERIA,
    )

    # Use default criteria
    scorer = MessageScorer(criteria=DEFAULT_CRITERIA)

    # Or customize criteria
    custom_criteria = [PersonalizationCriterion(), AntiSpamCriterion()]
    scorer = MessageScorer(criteria=custom_criteria)

Design Patterns:
    - Strategy: Each criterion encapsulates a scoring algorithm
    - Dependency Injection: MessageScorer receives criteria list

SOLID Compliance:
    - OCP: Add new criteria without modifying existing code
    - SRP: Each criterion handles one scoring dimension
    - DIP: MessageScorer depends on ScoringCriterion abstraction
    - LSP: All criteria are interchangeable through base class
"""

from .scoring_criterion import ScoringCriterion
from .personalization_criterion import PersonalizationCriterion
from .anti_spam_criterion import AntiSpamCriterion
from .structure_criterion import StructureCriterion
from .tone_criterion import ToneCriterion


def create_default_criteria() -> list[ScoringCriterion]:
    """
    Factory function to create the default set of scoring criteria.

    Returns:
        list[ScoringCriterion]: Default criteria for message scoring
    """
    return [
        PersonalizationCriterion(),
        AntiSpamCriterion(),
        StructureCriterion(),
        ToneCriterion(),
    ]


# Default criteria instance for convenience
DEFAULT_CRITERIA: list[ScoringCriterion] = create_default_criteria()


__all__ = [
    # Abstract base class
    "ScoringCriterion",
    # Concrete implementations
    "PersonalizationCriterion",
    "AntiSpamCriterion",
    "StructureCriterion",
    "ToneCriterion",
    # Factory and defaults
    "create_default_criteria",
    "DEFAULT_CRITERIA",
]
