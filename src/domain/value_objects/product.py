from dataclasses import dataclass, field

from domain.exceptions.domain_exceptions import InvalidProductError


@dataclass(frozen=True)
class Product:
    name: str
    description: str
    key_benefits: list[str] = field(default_factory=list)
    target_problems: list[str] = field(default_factory=list)
    differentiators: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidProductError(field="name", reason="cannot be empty")

    def get_benefit_for_pain(self, pain_point: str) -> str | None:
        """Encuentra el beneficio que resuelve un pain point"""
        pain_lower = pain_point.lower()

        for i, problem in enumerate(self.target_problems):
            if pain_lower in problem.lower() and i < len(self.key_benefits):
                return self.key_benefits[i]
        return self.key_benefits[0] if self.key_benefits else None
