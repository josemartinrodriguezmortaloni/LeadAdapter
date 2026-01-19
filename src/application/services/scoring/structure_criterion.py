"""
Structure scoring criterion implementation.

Evaluates the message structure for proper greeting, value proposition,
and call-to-action components that drive engagement.
"""

import re
from typing import Final

from domain.entities.lead import Lead

from .scoring_criterion import ScoringCriterion


class StructureCriterion(ScoringCriterion):
    """
    Strategy for scoring message structure quality (0-2 points).

    Scoring breakdown:
        - +0.50: Starts with appropriate greeting
        - +0.75: Contains value proposition keywords
        - +0.75: Has clear call-to-action

    A well-structured message guides the reader from greeting through
    value proposition to a clear next step.
    """

    MAX_SCORE: Final[float] = 2.0
    GREETING_SCORE: Final[float] = 0.5
    VALUE_PROP_SCORE: Final[float] = 0.75
    CTA_SCORE: Final[float] = 0.75

    # Valid greeting prefixes (must start the message)
    GREETING_PREFIXES: Final[tuple[str, ...]] = (
        "hola",
        "hi",
        "hey",
    )

    # Keywords indicating value proposition
    VALUE_KEYWORDS: Final[tuple[str, ...]] = (
        "ayudar",
        "mejorar",
        "optimizar",
        "help",
        "improve",
    )

    # Patterns indicating call-to-action
    CTA_PATTERNS: Final[tuple[str, ...]] = (
        r"\?$",  # Ends with a question
        r"(hablamos|conectamos|charlamos|chat|call)",  # Meeting suggestions
        r"(te parece|qué opinas|interesa)",  # Engagement prompts
    )

    @property
    def name(self) -> str:
        return "structure"

    @property
    def max_score(self) -> float:
        return self.MAX_SCORE

    def score(self, content: str, lead: Lead) -> float:
        """
        Evaluate message structure quality.

        Args:
            content: Message text to evaluate
            lead: Lead context (unused for structure, but required by interface)

        Returns:
            float: Score between 0.0 and 2.0
        """
        accumulated_score = 0.0
        content_lower = content.lower()

        accumulated_score += self._score_greeting(content_lower)
        accumulated_score += self._score_value_proposition(content_lower)
        accumulated_score += self._score_call_to_action(content_lower)

        return min(accumulated_score, self.MAX_SCORE)

    def _score_greeting(self, content_lower: str) -> float:
        """Award points if message starts with appropriate greeting."""
        for greeting in self.GREETING_PREFIXES:
            if content_lower.startswith(greeting):
                return self.GREETING_SCORE
        return 0.0

    def _score_value_proposition(self, content_lower: str) -> float:
        """Award points if message contains value proposition keywords."""
        for keyword in self.VALUE_KEYWORDS:
            if keyword in content_lower:
                return self.VALUE_PROP_SCORE
        return 0.0

    def _score_call_to_action(self, content_lower: str) -> float:
        """Award points if message contains clear call-to-action."""
        for pattern in self.CTA_PATTERNS:
            if re.search(pattern, content_lower):
                return self.CTA_SCORE
        return 0.0

    def get_structure_analysis(self, content: str) -> dict[str, bool]:
        """
        Analyze which structural elements are present.

        Useful for debugging and providing feedback to content creators.

        Args:
            content: Message text to analyze

        Returns:
            dict: Presence of each structural element
        """
        content_lower = content.lower()
        return {
            "has_greeting": self._score_greeting(content_lower) > 0,
            "has_value_proposition": self._score_value_proposition(content_lower) > 0,
            "has_cta": self._score_call_to_action(content_lower) > 0,
        }
