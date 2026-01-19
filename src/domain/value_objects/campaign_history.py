from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


# inmutable
@dataclass(frozen=True)
class CampaignHistory:
    total_attempts: int = 0
    last_contact_date: Optional[datetime] = None
    last_channel: Optional[str] = None
    responses_received: int = 0
    last_response_sentiment: Optional[str] = None

    @property
    def has_responded(self) -> bool:
        return self.responses_received > 0

    @property
    def response_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.responses_received / self.total_attempts

    def days_since_last_contact(self) -> Optional[int]:
        if not self.last_contact_date:
            return None
        delta = datetime.now(timezone.utc) - self.last_contact_date
        return delta.days
