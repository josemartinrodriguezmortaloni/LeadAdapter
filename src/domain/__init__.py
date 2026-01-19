"""
Domain Layer for LeadAdapter.

This layer contains the core business logic and is independent of
any external frameworks or libraries.
"""

from domain.entities.lead import Lead
from domain.entities.message import Message
from domain.entities.playbook import Playbook
from domain.entities.sender import Sender
from domain.enums import Channel, MessageStrategy, Seniority, SequenceStep
from domain.services.icp_matcher import ICPMatcher
from domain.services.seniority_inferrer import SeniorityInferrer
from domain.services.strategy_selector import StrategySelector

__all__ = [
    # Entities
    "Lead",
    "Message",
    "Playbook",
    "Sender",
    # Enums
    "Channel",
    "MessageStrategy",
    "Seniority",
    "SequenceStep",
    # Services
    "ICPMatcher",
    "SeniorityInferrer",
    "StrategySelector",
]
