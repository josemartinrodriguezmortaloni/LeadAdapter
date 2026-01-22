from dataclasses import dataclass

from domain.exceptions.domain_exceptions import InvalidSenderError


@dataclass
class Sender:
    name: str
    company_name: str
    job_title: str | None = None
    email: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidSenderError(field="name", reason="cannot be empty")
        if not self.company_name.strip():
            raise InvalidSenderError(field="company_name", reason="cannot be empty")

    @property
    def signature(self) -> str:
        """Genera firma para mensajes."""
        if self.job_title:
            return f"{self.name}, {self.job_title} @ {self.company_name}"
        return f"{self.name} @ {self.company_name}"
