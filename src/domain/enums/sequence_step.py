from enum import Enum


class SequenceStep(str, Enum):
    """Paso en la secuencia de contacto."""

    FIRST_CONTACT = "first_contact"
    FOLLOW_UP_1 = "follow_up_1"
    FOLLOW_UP_2 = "follow_up_2"
    BREAKUP = "breakup"

    @property
    def message_tone(self) -> str:
        """Tono sugerido según el paso."""
        tones = {
            SequenceStep.FIRST_CONTACT: "introductorio y curioso",
            SequenceStep.FOLLOW_UP_1: "recordatorio amigable",
            SequenceStep.FOLLOW_UP_2: "valor adicional",
            SequenceStep.BREAKUP: "última oportunidad, sin presión",
        }
        return tones.get(self, "profesional")

    @property
    def urgency_level(self) -> int:
        """Nivel de urgencia (1-4)."""
        levels = {
            SequenceStep.FIRST_CONTACT: 1,
            SequenceStep.FOLLOW_UP_1: 2,
            SequenceStep.FOLLOW_UP_2: 3,
            SequenceStep.BREAKUP: 4,
        }
        return levels.get(self, 1)
