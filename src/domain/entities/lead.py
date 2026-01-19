from dataclasses import dataclass, field
from typing import Optional

from domain.exceptions.domain_exceptions import InvalidLeadError
from domain.value_objects.campaign_history import CampaignHistory
from domain.value_objects.work_experience import WorkExperience


@dataclass
class Lead:
    first_name: str
    job_title: str
    company_name: str
    last_name: Optional[str] = None
    work_experience: list[WorkExperience] = field(default_factory=list)
    campaign_history: Optional[CampaignHistory] = None
    bio: Optional[str] = None
    skills: list[str] = field(default_factory=list)
    linkedin_url: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.first_name.strip():
            raise InvalidLeadError(field="first_name", reason="cannot be empty")
        if not self.job_title.strip():
            raise InvalidLeadError(field="job_title", reason="cannot be empty")
        if not self.company_name.strip():
            raise InvalidLeadError(field="company_name", reason="cannot be empty")

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def years_in_current_role(self) -> Optional[int]:
        """Calcula años en el rol actual desde work_experience"""
        if not self.work_experience:
            return None
        # Asume que esta ordenado por fecha
        current = self.work_experience[0]
        return current.duration_years()

    def has_previous_contact(self) -> bool:
        """Verifica si ya fue contactado anteriormente"""
        if not self.campaign_history:
            return False
        return self.campaign_history.total_attempts > 0
