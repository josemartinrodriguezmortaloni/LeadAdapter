from dataclasses import dataclass
from datetime import UTC, datetime


# inmutable
@dataclass(frozen=True)
class CampaignHistory:
    total_attempts: int = 0
    last_contact_date: datetime | None = None
    last_channel: str | None = None
    responses_received: int = 0
    last_response_sentiment: str | None = None

    @property
    def has_responded(self) -> bool:
        return self.responses_received > 0

    @property
    def response_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.responses_received / self.total_attempts

    def days_since_last_contact(self) -> int | None:
        if not self.last_contact_date:
            return None
        delta = datetime.now(UTC) - self.last_contact_date
        return delta.days
