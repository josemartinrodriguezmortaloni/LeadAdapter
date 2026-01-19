"""
Abstract base class for scoring criteria using Strategy Pattern.

This module defines the contract that all scoring criteria must follow,
enabling extensibility without modification (OCP compliance).

Design Pattern: Strategy
GRASP: Protected Variations - scoring algorithms are encapsulated behind stable interface
"""

from abc import ABC, abstractmethod

from domain.entities.lead import Lead


class ScoringCriterion(ABC):
    """
    Abstract strategy for evaluating a specific quality dimension of a message.

    Each criterion encapsulates its own scoring algorithm, max score, and name.
    New scoring criteria can be added by implementing this interface without
    modifying existing code.

    Attributes:
        name: Unique identifier for this criterion (used in ScoreBreakdown)
        max_score: Maximum points this criterion can award

    Example:
        >>> class CustomCriterion(ScoringCriterion):
        ...     @property
        ...     def name(self) -> str:
        ...         return "custom"
        ...
        ...     @property
        ...     def max_score(self) -> float:
        ...         return 5.0
        ...
        ...     def score(self, content: str, lead: Lead) -> float:
        ...         # Custom scoring logic
        ...         return 3.5
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this scoring criterion.

        This name is used as a key in the ScoreBreakdown dataclass.
        Must be unique across all registered criteria.

        Returns:
            str: The criterion name (e.g., 'personalization', 'anti_spam')
        """
        ...

    @property
    @abstractmethod
    def max_score(self) -> float:
        """
        Maximum score this criterion can award.

        The score() method must never return a value exceeding max_score.
        This value is used for normalization and validation.

        Returns:
            float: Maximum possible score for this criterion
        """
        ...

    @abstractmethod
    def score(self, content: str, lead: Lead) -> float:
        """
        Evaluate the message content against this criterion.

        Args:
            content: The message text to evaluate
            lead: The lead context for personalization-aware scoring

        Returns:
            float: Score between 0.0 and max_score (inclusive)

        Note:
            Implementations must ensure the returned value is clamped
            to the range [0.0, max_score].
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', max_score={self.max_score})"
