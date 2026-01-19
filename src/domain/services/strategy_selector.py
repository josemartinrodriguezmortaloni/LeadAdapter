from domain.entities.lead import Lead
from domain.entities.playbook import Playbook
from domain.enums.channel import Channel
from domain.enums.message_strategy import MessageStrategy
from domain.enums.sequence_step import SequenceStep


class StrategySelector:
    """Selecciona la estrategia óptima"""

    def select(
        self,
        lead: Lead,
        channel: Channel,
        sequence_step: SequenceStep,
        playbook: Playbook,
        seniority: str,
    ) -> MessageStrategy:
        """
        Selecciona estrategia basada en:
        1. Seniority del lead
        2. Canal de comunicación
        3. Paso en la secuencia
        4. Historial de contacto
        """
        # Obtener estrategias base por seniority
        candidates = MessageStrategy.for_seniority(seniority)

        # Ajustar por historial
        if lead.has_previous_contact() and MessageStrategy.PROBLEM_SOLUTION in candidates:
            return MessageStrategy.PROBLEM_SOLUTION

        # Ajustar paso por secuencia
        if sequence_step == SequenceStep.BREAKUP:
            return MessageStrategy.CURIOSITY_HOOK

        if sequence_step == SequenceStep.FIRST_CONTACT:
            if channel == Channel.LINKEDIN:
                return MessageStrategy.MUTUAL_CONNECTION
            return candidates[0]

        return candidates[0] if candidates else MessageStrategy.PROBLEM_SOLUTION
