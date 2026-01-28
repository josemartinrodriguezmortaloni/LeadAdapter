"""
Use Case para generación de mensajes personalizados.

Este módulo contiene el caso de uso principal para generar mensajes
de outreach personalizados basados en leads, playbooks y estrategias.
"""

import hashlib
import logging
import time
from dataclasses import dataclass

from application.dtos.requests import GenerateMessageRequest
from application.dtos.responses import (
    GenerateMessageResponse,
    MetadataDTO,
    QualityBreakdownDTO,
    QualityDTO,
)
from application.mappers.entity_mapper import EntityMapper
from application.ports.cache_port import CachePort
from application.ports.llm_port import LLMPort
from application.services.prompt_chain_orchestrator import PromptChainOrchestrator
from application.services.quality_gate import QualityGate
from domain.enums.channel import Channel
from domain.enums.sequence_step import SequenceStep
from domain.services.icp_matcher import ICPMatcher
from domain.services.seniority_inferrer import SeniorityInferrer
from domain.services.strategy_selector import StrategySelector

logger = logging.getLogger(__name__)

# Cache TTL constants
CACHE_TTL_SECONDS = 3600  # 1 hour


@dataclass
class GenerateMessageUseCase:
    """
    Caso de uso: Generar mensaje personalizado de outreach.

    Orquesta la generación de mensajes coordinando:
    - Inferencia de seniority del lead
    - Matching con ICP profiles
    - Selección de estrategia de comunicación
    - Generación con control de calidad
    - Cache-aside pattern para optimizar respuestas

    Attributes:
        llm: Puerto para interactuar con el LLM.
        cache: Puerto para caching de resultados.
        prompt_orchestrator: Orquestador de cadena de prompts.
        quality_gate: Gate de calidad para validar mensajes.
        strategy_selector: Selector de estrategia de comunicación.
        seniority_inferrer: Inferidor de nivel de seniority.
        icp_matcher: Matcher de ICP profiles.
        entity_mapper: Mapper para conversión DTO a entidades.
    """

    llm: LLMPort
    cache: CachePort
    prompt_orchestrator: PromptChainOrchestrator
    quality_gate: QualityGate
    strategy_selector: StrategySelector
    seniority_inferrer: SeniorityInferrer
    icp_matcher: ICPMatcher
    entity_mapper: EntityMapper

    async def execute(self, request: GenerateMessageRequest) -> GenerateMessageResponse:
        """
        Ejecuta la generación de un mensaje personalizado.

        Implementa cache-aside pattern: verifica cache antes de generar
        y almacena respuestas exitosas para futuras consultas.

        Args:
            request: Request con datos del lead, sender y playbook.

        Returns:
            Response con el mensaje generado y metadatos de calidad.
        """
        start_time = time.time()

        logger.info(
            "Starting message generation",
            extra={
                "lead_name": request.lead.first_name,
                "company": request.lead.company_name,
                "channel": request.channel,
                "sequence_step": request.sequence_step,
            },
        )

        # Cache-aside: check cache first
        cache_key = self._build_cache_key(request)
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(
                "Cache hit for message generation",
                extra={"cache_key": cache_key},
            )
            return GenerateMessageResponse(**cached)

        # Cache miss: proceed with generation
        logger.debug(
            "Cache miss, generating message",
            extra={"cache_key": cache_key},
        )

        lead = self.entity_mapper.to_lead(request.lead)
        sender = self.entity_mapper.to_sender(request.sender)
        playbook = self.entity_mapper.to_playbook(request.playbook)
        channel = Channel(request.channel)
        sequence_step = SequenceStep(request.sequence_step)

        seniority = self.seniority_inferrer.infer(lead.job_title)
        matched_icp = self.icp_matcher.match(lead, playbook)

        logger.debug(
            "Context resolved",
            extra={
                "seniority": seniority.value,
                "icp_matched": matched_icp.name if matched_icp else None,
            },
        )

        strategy = self.strategy_selector.select(
            lead=lead,
            channel=channel,
            sequence_step=sequence_step,
            playbook=playbook,
            seniority=seniority.value,
        )

        message, attempts = await self.quality_gate.generate_with_retry(
            lead=lead,
            sender=sender,
            playbook=playbook,
            channel=channel,
            sequence_step=sequence_step,
            strategy=strategy,
            matched_icp=matched_icp,
            seniority=seniority,
        )

        generation_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Message generated successfully",
            extra={
                "message_id": message.message_id,
                "strategy": strategy.value,
                "quality_score": message.quality_score,
                "attempts": attempts,
                "generation_time_ms": generation_time_ms,
            },
        )

        response = GenerateMessageResponse(
            message_id=message.message_id,
            content=message.content,
            quality=QualityDTO(
                score=message.quality_score,
                breakdown=QualityBreakdownDTO(**message.quality_breakdown),
                passes_threshold=message.passes_quality_gate(),
            ),
            strategy_used=strategy.value,
            metadata=MetadataDTO(
                tokens_used=message.tokens_used,
                generation_time_ms=generation_time_ms,
                model_used=message.model_used,
                attempts=attempts,
            ),
        )

        # Cache successful response
        await self.cache.set(cache_key, response.model_dump(), ttl_seconds=CACHE_TTL_SECONDS)
        logger.debug(
            "Response cached",
            extra={"cache_key": cache_key, "ttl_seconds": CACHE_TTL_SECONDS},
        )

        return response

    def _build_cache_key(self, request: GenerateMessageRequest) -> str:
        """
        Construye una clave de cache determinística basada en inputs del request.

        La clave se genera a partir de los atributos que determinan
        unívocamente el mensaje a generar, hasheados para mantener
        un tamaño fijo y evitar caracteres problemáticos.

        Args:
            request: Request con datos del lead y contexto.

        Returns:
            Clave de cache en formato "msg:{hash_12_chars}".
        """
        key_parts = [
            request.lead.first_name,
            request.lead.job_title,
            request.lead.company_name,
            request.channel,
            request.sequence_step,
        ]
        key_string = "|".join(key_parts)
        hash_suffix = hashlib.md5(key_string.encode()).hexdigest()[:12]
        return f"msg:{hash_suffix}"
