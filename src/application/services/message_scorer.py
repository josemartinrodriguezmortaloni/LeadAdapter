"""
Message quality scorer using Strategy Pattern for extensible evaluation.

This module provides a flexible scoring system where each quality dimension
is evaluated by a pluggable ScoringCriterion strategy. New criteria can be
added without modifying the MessageScorer class (OCP compliance).

Design Patterns:
    - Strategy: Scoring criteria are interchangeable algorithms
    - Dependency Injection: Criteria are injected via constructor

GRASP Principles:
    - Low Coupling: MessageScorer depends on abstraction, not implementations
    - High Cohesion: Each criterion focuses on one quality dimension
    - Protected Variations: New criteria don't affect existing code
"""

from dataclasses import dataclass, field
from typing import Any

from domain.entities.lead import Lead

from .scoring import (
    ScoringCriterion,
    create_default_criteria,
)


@dataclass
class ScoreBreakdown:
    """
    Desglose del score de calidad de un mensaje.

    Cada dimensión evalúa un aspecto específico de la calidad:
    - personalization (0-3): Uso de nombre, empresa, contexto específico
    - anti_spam (0-3): Ausencia de frases genéricas y spam
    - structure (0-2): Hook, propuesta de valor, CTA
    - tone (0-2): Adecuación al contexto y seniority

    El total máximo es 10 puntos. El threshold por defecto es 6.0.

    This dataclass supports dynamic scores from any registered criteria
    via the extra_scores field for extensibility.
    """

    personalization: float = 0.0
    anti_spam: float = 0.0
    structure: float = 0.0
    tone: float = 0.0
    extra_scores: dict[str, float] = field(default_factory=dict)

    @property
    def total(self) -> float:
        """Calculate total score from all dimensions."""
        base_total = self.personalization + self.anti_spam + self.structure + self.tone
        extra_total = sum(self.extra_scores.values())
        return base_total + extra_total

    def get_score(self, criterion_name: str) -> float:
        """
        Get score for a specific criterion by name.

        Args:
            criterion_name: Name of the criterion

        Returns:
            float: Score for the criterion, or 0.0 if not found
        """
        # Check standard fields first
        if hasattr(self, criterion_name) and criterion_name != "extra_scores":
            return getattr(self, criterion_name)
        # Check extra scores
        return self.extra_scores.get(criterion_name, 0.0)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert score breakdown to dictionary format.

        Returns:
            dict: All scores including extras, plus total
        """
        result = {
            "personalization": self.personalization,
            "anti_spam": self.anti_spam,
            "structure": self.structure,
            "tone": self.tone,
            "total": self.total,
        }
        result.update(self.extra_scores)
        return result


class MessageScorer:
    """
    Evaluates message quality using pluggable scoring criteria.

    This class uses the Strategy Pattern to delegate scoring to
    independent criterion objects. Each criterion evaluates one
    quality dimension (personalization, anti-spam, structure, tone).

    The design follows:
    - OCP: Add new criteria without modifying this class
    - DIP: Depends on ScoringCriterion abstraction
    - SRP: This class only orchestrates scoring, not the algorithms

    Example:
        # Use default criteria
        scorer = MessageScorer()
        breakdown = scorer.score(message_content, lead)

        # Use custom criteria
        from application.services.scoring import (
            PersonalizationCriterion,
            AntiSpamCriterion,
        )
        custom_scorer = MessageScorer(
            criteria=[PersonalizationCriterion(), AntiSpamCriterion()]
        )

        # Extend with new criterion
        class UrgencyCriterion(ScoringCriterion):
            ...
        scorer = MessageScorer(
            criteria=create_default_criteria() + [UrgencyCriterion()]
        )

    Attributes:
        _criteria: List of scoring criterion strategies
    """

    # Standard criterion names that map to ScoreBreakdown fields
    STANDARD_CRITERIA: frozenset[str] = frozenset(
        {
            "personalization",
            "anti_spam",
            "structure",
            "tone",
        }
    )

    def __init__(self, criteria: list[ScoringCriterion] | None = None) -> None:
        """
        Initialize MessageScorer with scoring criteria.

        Args:
            criteria: List of scoring criteria to use. If None, uses
                     default criteria (personalization, anti_spam,
                     structure, tone).
        """
        self._criteria = criteria if criteria is not None else create_default_criteria()
        self._validate_criteria()

    def _validate_criteria(self) -> None:
        """
        Validate that all criteria are properly configured.

        Raises:
            ValueError: If duplicate criterion names are detected
        """
        names = [c.name for c in self._criteria]
        if len(names) != len(set(names)):
            duplicates = [n for n in names if names.count(n) > 1]
            raise ValueError(f"Duplicate criterion names detected: {set(duplicates)}")

    @property
    def criteria(self) -> list[ScoringCriterion]:
        """Get the list of registered scoring criteria."""
        return list(self._criteria)

    @property
    def max_possible_score(self) -> float:
        """Calculate maximum possible score from all criteria."""
        return sum(c.max_score for c in self._criteria)

    def score(self, message_content: str, lead: Lead) -> ScoreBreakdown:
        """
        Evaluate message quality across all registered criteria.

        Args:
            message_content: The message text to evaluate
            lead: The lead context for personalization-aware scoring

        Returns:
            ScoreBreakdown: Detailed breakdown of scores per criterion
        """
        scores: dict[str, float] = {}
        extra_scores: dict[str, float] = {}

        for criterion in self._criteria:
            criterion_score = criterion.score(message_content, lead)

            if criterion.name in self.STANDARD_CRITERIA:
                scores[criterion.name] = criterion_score
            else:
                extra_scores[criterion.name] = criterion_score

        return ScoreBreakdown(
            personalization=scores.get("personalization", 0.0),
            anti_spam=scores.get("anti_spam", 0.0),
            structure=scores.get("structure", 0.0),
            tone=scores.get("tone", 0.0),
            extra_scores=extra_scores,
        )

    def get_criterion(self, name: str) -> ScoringCriterion | None:
        """
        Get a specific criterion by name.

        Args:
            name: The criterion name to look up

        Returns:
            ScoringCriterion or None if not found
        """
        for criterion in self._criteria:
            if criterion.name == name:
                return criterion
        return None

    def __repr__(self) -> str:
        criteria_names = [c.name for c in self._criteria]
        return f"MessageScorer(criteria={criteria_names})"
