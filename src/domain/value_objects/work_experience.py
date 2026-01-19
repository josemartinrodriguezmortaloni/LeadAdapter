from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.exceptions.domain_exceptions import InvalidWorkExperienceError


# inmutable
@dataclass(frozen=True)
class WorkExperience:
    company: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.company.strip():
            raise InvalidWorkExperienceError(field="company", reason="cannot be empty")
        if not self.title.strip():
            raise InvalidWorkExperienceError(field="title", reason="cannot be empty")

    @property
    def is_current(self) -> bool:
        return self.end_date is None

    def duration_years(self) -> int:
        """Calcula duración del trabajo en años"""
        end = self.end_date or date.today()
        delta = end - self.start_date
        return delta.days // 365

    def duration_months(self) -> int:
        """Calcula duración del trabajo en meses"""
        end = self.end_date or date.today()
        delta = end - self.start_date
        return delta.days // 30
