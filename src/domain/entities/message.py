import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from domain.enums.channel import Channel
from domain.enums.message_strategy import MessageStrategy
from domain.enums.sequence_step import SequenceStep
from domain.exceptions.domain_exceptions import InvalidMessageError


@dataclass(frozen=False)
class Message:
    content: str
    channel: Channel
    sequence_step: SequenceStep
    strategy_used: MessageStrategy
    quality_score: float
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    quality_breakdown: dict = field(default_factory=dict)
    tokens_used: int = 0
    generation_time_ms: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise InvalidMessageError(field="content", reason="cannot be empty")
        if not 0 <= self.quality_score <= 10:
            raise InvalidMessageError(field="quality_score", reason="must be between 0 and 10")

    def passes_quality_gate(self, threshold: float = 6.0) -> bool:
        """Verifica si el mensaje pasa el umbral de calidad"""
        return self.quality_score >= threshold

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def char_count(self) -> int:
        return len(self.content)
