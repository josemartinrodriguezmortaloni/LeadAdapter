"""
Personalization scoring criterion implementation.

Evaluates how well the message is personalized to the specific lead,
checking for name mentions, company references, and contextual specificity.
"""

import re
from typing import Final

from domain.entities.lead import Lead

from .scoring_criterion import ScoringCriterion


class PersonalizationCriterion(ScoringCriterion):
    """
    Strategy for scoring message personalization (0-3 points).

    Scoring breakdown:
        - +1.0: Lead's first name mentioned
        - +1.0: Lead's company name mentioned
        - +0.33: Each specific pattern match (years, observations, job title)

    The score is capped at max_score (3.0) even if more patterns match.
    """

    MAX_SCORE: Final[float] = 3.0
    NAME_MATCH_SCORE: Final[float] = 1.0
    COMPANY_MATCH_SCORE: Final[float] = 1.0
    PATTERN_MATCH_SCORE: Final[float] = 0.33

    # Patterns indicating specific, personalized observations
    SPECIFIC_PATTERNS: Final[tuple[str, ...]] = (
        r"\d+\s*(años|years)",  # References to years of experience
        r"(vi que|noté que|me llamó la atención)",  # Specific observations
    )

    @property
    def name(self) -> str:
        return "personalization"

    @property
    def max_score(self) -> float:
        return self.MAX_SCORE

    def score(self, content: str, lead: Lead) -> float:
        """
        Evaluate personalization level of the message.

        Args:
            content: Message text to evaluate
            lead: Lead context for personalization checks

        Returns:
            float: Score between 0.0 and 3.0
        """
        accumulated_score = 0.0
        content_lower = content.lower()

        accumulated_score += self._score_name_mention(content_lower, lead)
        accumulated_score += self._score_company_mention(content_lower, lead)
        accumulated_score += self._score_specific_patterns(content_lower, lead)

        return min(accumulated_score, self.MAX_SCORE)

    def _score_name_mention(self, content_lower: str, lead: Lead) -> float:
        """Award points if lead's first name is mentioned."""
        if lead.first_name.lower() in content_lower:
            return self.NAME_MATCH_SCORE
        return 0.0

    def _score_company_mention(self, content_lower: str, lead: Lead) -> float:
        """Award points if lead's company name is mentioned."""
        if lead.company_name.lower() in content_lower:
            return self.COMPANY_MATCH_SCORE
        return 0.0

    def _score_specific_patterns(self, content_lower: str, lead: Lead) -> float:
        """
        Award points for specific, personalized content patterns.

        Checks for:
        - References to years/experience
        - Specific observation phrases
        - Job title relevance
        """
        pattern_score = 0.0

        # Check predefined specific patterns
        for pattern in self.SPECIFIC_PATTERNS:
            if re.search(pattern, content_lower):
                pattern_score += self.PATTERN_MATCH_SCORE

        # Check for job title first word (indicates role-specific personalization)
        job_title_keyword = self._extract_job_title_keyword(lead.job_title)
        if job_title_keyword and job_title_keyword in content_lower:
            pattern_score += self.PATTERN_MATCH_SCORE

        return pattern_score

    def _extract_job_title_keyword(self, job_title: str) -> str:
        """
        Extract the first word of job title as a keyword.

        Args:
            job_title: Full job title string

        Returns:
            str: Lowercase first word, or empty string if not available
        """
        parts = job_title.split()
        return parts[0].lower() if parts else ""
