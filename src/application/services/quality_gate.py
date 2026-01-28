import logging
from dataclasses import dataclass

from application.services.message_scorer import MessageScorer
from application.services.prompt_chain_orchestrator import PromptChainOrchestrator
from domain.entities.lead import Lead
from domain.entities.message import Message
from domain.entities.playbook import Playbook
from domain.entities.sender import Sender
from domain.enums.channel import Channel
from domain.enums.message_strategy import MessageStrategy
from domain.enums.seniority import Seniority
from domain.enums.sequence_step import SequenceStep
from domain.exceptions.domain_exceptions import QualityThresholdNotMetError
from domain.value_objects.icp_profile import ICPProfile

logger = logging.getLogger(__name__)


@dataclass
class QualityGate:
    """Controla calidad de mensajes y regenera si es necesario."""

    orchestrator: PromptChainOrchestrator
    scorer: MessageScorer
    threshold: float = 6.0
    max_attempts: int = 3

    async def generate_with_retry(
        self,
        lead: Lead,
        sender: Sender,
        playbook: Playbook,
        channel: Channel,
        sequence_step: SequenceStep,
        strategy: MessageStrategy,
        matched_icp: ICPProfile | None,
        seniority: Seniority,
    ) -> tuple[Message, int]:
        """
        Genera mensaje con reintentos si no pasa quality gate.

        Returns:
            tuple[Message, int]: (mensaje, número_de_intentos)

        Raises:
            QualityThresholdNotMetError: Si después de max_attempts no se logra
        """
        attempts = 0
        best_message: Message | None = None
        best_score = 0.0

        while attempts < self.max_attempts:
            attempts += 1

            # Generar mensaje
            content, tokens, model_used = await self.orchestrator.execute_chain(
                lead=lead,
                sender=sender,
                playbook=playbook,
                channel=channel,
                sequence_step=sequence_step,
                strategy=strategy,
                matched_icp=matched_icp,
                seniority=seniority,
            )

            # Calcular score
            score_breakdown = self.scorer.score(content, lead)
            total_score = score_breakdown.total

            # Crear mensaje
            message = Message(
                content=content,
                channel=channel,
                sequence_step=sequence_step,
                strategy_used=strategy,
                quality_score=total_score,
                quality_breakdown={
                    "personalization": score_breakdown.personalization,
                    "anti_spam": score_breakdown.anti_spam,
                    "structure": score_breakdown.structure,
                    "tone": score_breakdown.tone,
                },
                tokens_used=tokens,
                model_used=model_used,
            )

            # Guardar mejor intento
            if total_score > best_score:
                best_score = total_score
                best_message = message

            # Si pasa threshold, retornar
            if message.passes_quality_gate(self.threshold):
                logger.info(f"Message passed quality gate on attempt {attempts}")
                return message, attempts

            logger.warning(
                f"Attempt {attempts}: score {total_score} below threshold {self.threshold}"
            )

        # Si llegamos aquí, retornar el mejor intento con warning
        if best_message:
            logger.warning(
                f"Returning best effort message with score {best_score} "
                f"after {self.max_attempts} attempts"
            )
            return best_message, attempts

        raise QualityThresholdNotMetError(
            score=best_score,
            threshold=self.threshold,
            message="Could not generate message meeting quality standards",
        )
