"""
Enums del dominio para LeadAdapter.

Estos enums definen los valores permitidos para los campos
criticos del sistema de generacion de mensajes.
"""

from domain.enums.channel import Channel
from domain.enums.message_strategy import MessageStrategy
from domain.enums.seniority import Seniority
from domain.enums.sequence_step import SequenceStep

__all__ = [
    "Channel",
    "MessageStrategy",
    "Seniority",
    "SequenceStep",
]
