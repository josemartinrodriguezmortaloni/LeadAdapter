from enum import Enum


class MessageStrategy(str, Enum):
    """Estrategia de aproximación al lead."""

    TECHNICAL_PEER = "technical_peer"  # Dev a Dev
    BUSINESS_VALUE = "business_value"  # ROI, métricas
    PROBLEM_SOLUTION = "problem_solution"  # Pain point directo
    SOCIAL_PROOF = "social_proof"  # Casos de éxito
    CURIOSITY_HOOK = "curiosity_hook"  # Pregunta intrigante
    MUTUAL_CONNECTION = "mutual_connection"  # Conexión en común

    @property
    def description(self) -> str:
        descriptions = {
            MessageStrategy.TECHNICAL_PEER: "Hablar como un par técnico, usar jerga del sector",
            MessageStrategy.BUSINESS_VALUE: "Enfocarse en ROI y métricas de negocio",
            MessageStrategy.PROBLEM_SOLUTION: "Atacar un pain point específico",
            MessageStrategy.SOCIAL_PROOF: "Usar casos de éxito y testimonios",
            MessageStrategy.CURIOSITY_HOOK: "Generar curiosidad con una pregunta",
            MessageStrategy.MUTUAL_CONNECTION: "Mencionar conexiones o contexto común",
        }
        return descriptions.get(self, "")

    @classmethod
    def for_seniority(cls, seniority: str) -> list["MessageStrategy"]:
        """Estrategias recomendadas según seniority."""
        mapping = {
            "C_LEVEL": [cls.BUSINESS_VALUE, cls.SOCIAL_PROOF],
            "VP": [cls.BUSINESS_VALUE, cls.PROBLEM_SOLUTION],
            "DIRECTOR": [cls.PROBLEM_SOLUTION, cls.BUSINESS_VALUE],
            "MANAGER": [cls.PROBLEM_SOLUTION, cls.TECHNICAL_PEER],
            "SENIOR": [cls.TECHNICAL_PEER, cls.PROBLEM_SOLUTION],
            "MID": [cls.TECHNICAL_PEER, cls.CURIOSITY_HOOK],
            "JUNIOR": [cls.CURIOSITY_HOOK, cls.TECHNICAL_PEER],
        }
        return mapping.get(seniority, [cls.PROBLEM_SOLUTION])
