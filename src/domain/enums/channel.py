from enum import Enum


class Channel(str, Enum):
    """Canales de comunicación para mensajes."""

    LINKEDIN = "linkedin"
    EMAIL = "email"

    @property
    def max_length(self) -> int:
        """Longitud máxima recomendada por canal."""
        limits = {
            Channel.LINKEDIN: 300,  # Caracteres para InMail/conexión
            Channel.EMAIL: 500,  # Más espacio en email
        }
        return limits.get(self, 300)

    @property
    def requires_subject(self) -> bool:
        """Si el canal requiere asunto."""
        return self == Channel.EMAIL
