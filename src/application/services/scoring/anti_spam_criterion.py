"""
Anti-spam scoring criterion implementation.

Evaluates the message for absence of generic, spammy phrases that reduce
credibility and engagement. Uses a penalty-based scoring approach.
"""

from typing import Final

from domain.entities.lead import Lead

from .scoring_criterion import ScoringCriterion


class AntiSpamCriterion(ScoringCriterion):
    """
    Strategy for scoring anti-spam quality (0-3 points).

    Scoring approach:
        - Starts at max_score (3.0)
        - Deducts 0.5 points for each spam phrase found
        - Minimum score is 0.0

    The penalty-based approach ensures clean messages get full marks,
    while spammy content is progressively penalized.
    """

    MAX_SCORE: Final[float] = 3.0
    PENALTY_PER_PHRASE: Final[float] = 0.5

    # Phrases that trigger spam detection and reduce score
    SPAM_PHRASES: Final[tuple[str, ...]] = (
        "revolucionar",
        "game changer",
        "best in class",
        "líder del mercado",
        "solución integral",
        "no te arrepentirás",
        "oferta limitada",
        "actúa ahora",
    )

    @property
    def name(self) -> str:
        return "anti_spam"

    @property
    def max_score(self) -> float:
        return self.MAX_SCORE

    def score(self, content: str, lead: Lead) -> float:
        """
        Evaluate message for spam indicators.

        Starts with maximum score and deducts for each spam phrase found.

        Args:
            content: Message text to evaluate
            lead: Lead context (unused for anti-spam, but required by interface)

        Returns:
            float: Score between 0.0 and 3.0
        """
        penalty = self._calculate_spam_penalty(content.lower())
        final_score = self.MAX_SCORE - penalty

        return max(final_score, 0.0)

    def _calculate_spam_penalty(self, content_lower: str) -> float:
        """
        Calculate total penalty based on spam phrases found.

        Args:
            content_lower: Lowercased message content

        Returns:
            float: Total penalty to subtract from max score
        """
        penalty = 0.0

        for phrase in self.SPAM_PHRASES:
            if phrase.lower() in content_lower:
                penalty += self.PENALTY_PER_PHRASE

        return penalty

    def get_detected_spam_phrases(self, content: str) -> list[str]:
        """
        Identify which spam phrases were detected in the content.

        Useful for debugging and providing feedback to content creators.

        Args:
            content: Message text to analyze

        Returns:
            list[str]: Spam phrases found in the content
        """
        content_lower = content.lower()
        return [phrase for phrase in self.SPAM_PHRASES if phrase.lower() in content_lower]
