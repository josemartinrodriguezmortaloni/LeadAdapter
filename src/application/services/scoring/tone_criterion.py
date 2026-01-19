"""
Tone scoring criterion implementation.

Evaluates the message tone for appropriateness, checking for proper
length and absence of excessively formal or informal markers.
"""

from typing import Final

from domain.entities.lead import Lead

from .scoring_criterion import ScoringCriterion


class ToneCriterion(ScoringCriterion):
    """
    Strategy for scoring message tone appropriateness (0-2 points).

    Scoring breakdown:
        - Base: 1.0 points
        - +0.5: Appropriate length (50-150 words)
        - +0.5: No excessively formal or informal markers

    Professional but approachable tone is rewarded, while extremes
    in formality or casual language are penalized.
    """

    MAX_SCORE: Final[float] = 2.0
    BASE_SCORE: Final[float] = 1.0
    LENGTH_BONUS: Final[float] = 0.5
    TONE_BALANCE_BONUS: Final[float] = 0.5

    # Optimal word count range
    MIN_WORD_COUNT: Final[int] = 50
    MAX_WORD_COUNT: Final[int] = 150

    # Markers indicating overly formal tone
    FORMAL_MARKERS: Final[tuple[str, ...]] = (
        "estimado",
        "distinguido",
        "por medio de la presente",
    )

    # Markers indicating overly informal tone
    INFORMAL_MARKERS: Final[tuple[str, ...]] = (
        "bro",
        "crack",
        "genio",
    )

    @property
    def name(self) -> str:
        return "tone"

    @property
    def max_score(self) -> float:
        return self.MAX_SCORE

    def score(self, content: str, lead: Lead) -> float:
        """
        Evaluate message tone appropriateness.

        Args:
            content: Message text to evaluate
            lead: Lead context (unused for tone, but required by interface)

        Returns:
            float: Score between 0.0 and 2.0
        """
        accumulated_score = self.BASE_SCORE

        accumulated_score += self._score_length(content)
        accumulated_score += self._score_tone_balance(content.lower())

        return min(accumulated_score, self.MAX_SCORE)

    def _score_length(self, content: str) -> float:
        """Award bonus for appropriate message length."""
        word_count = len(content.split())

        if self.MIN_WORD_COUNT <= word_count <= self.MAX_WORD_COUNT:
            return self.LENGTH_BONUS

        return 0.0

    def _score_tone_balance(self, content_lower: str) -> float:
        """
        Award bonus if message avoids extreme formality or informality.

        A balanced, professional tone is preferred over either extreme.
        """
        has_formal_markers = any(marker in content_lower for marker in self.FORMAL_MARKERS)
        has_informal_markers = any(marker in content_lower for marker in self.INFORMAL_MARKERS)

        if not has_formal_markers and not has_informal_markers:
            return self.TONE_BALANCE_BONUS

        return 0.0

    def get_word_count(self, content: str) -> int:
        """
        Get the word count of the message.

        Args:
            content: Message text to analyze

        Returns:
            int: Number of words in the message
        """
        return len(content.split())

    def get_tone_analysis(self, content: str) -> dict[str, bool | int]:
        """
        Analyze tone characteristics of the message.

        Useful for debugging and providing feedback to content creators.

        Args:
            content: Message text to analyze

        Returns:
            dict: Tone analysis with word count and marker detection
        """
        content_lower = content.lower()
        word_count = self.get_word_count(content)

        return {
            "word_count": word_count,
            "optimal_length": self.MIN_WORD_COUNT <= word_count <= self.MAX_WORD_COUNT,
            "has_formal_markers": any(m in content_lower for m in self.FORMAL_MARKERS),
            "has_informal_markers": any(m in content_lower for m in self.INFORMAL_MARKERS),
        }
