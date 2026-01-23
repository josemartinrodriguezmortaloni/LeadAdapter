"""
Composition Root for dependency injection.

This module serves as the single location where the entire object graph
is assembled. It creates and wires all dependencies required by use cases,
following the Dependency Inversion Principle.

The container uses factory functions compatible with FastAPI's Depends()
system, enabling automatic dependency injection in route handlers.

Example:
    >>> from fastapi import Depends
    >>> from api.dependencies.container import get_generate_message_use_case
    >>>
    >>> @router.post("/generate")
    >>> async def generate(use_case = Depends(get_generate_message_use_case)):
    ...     return await use_case.execute(request)

Note:
    Infrastructure adapters (LLM, Cache) are cached with @lru_cache to
    maintain singleton behavior and avoid recreating expensive connections.
"""

from functools import lru_cache

from application.mappers.entity_mapper import EntityMapper
from application.services.message_scorer import MessageScorer
from application.services.prompt_chain_orchestrator import PromptChainOrchestrator
from application.services.quality_gate import QualityGate
from application.use_cases.generate_message import GenerateMessageUseCase
from domain.services.icp_matcher import ICPMatcher
from domain.services.seniority_inferrer import SeniorityInferrer
from domain.services.strategy_selector import StrategySelector
from infrastructure.adapters.memory_cache_adapter import MemoryCacheAdapter
from infrastructure.adapters.openai_adapter import OpenAIAdapter
from infrastructure.config.settings import get_setting


@lru_cache
def get_llm_adapter() -> OpenAIAdapter:
    """
    Provide a singleton OpenAI adapter instance.

    Uses lru_cache to ensure only one adapter is created per process,
    avoiding redundant API client initialization.

    Returns:
        Configured OpenAI adapter ready for LLM operations.
    """
    return OpenAIAdapter(get_setting())


@lru_cache
def get_cache_adapter() -> MemoryCacheAdapter:
    """
    Provide a singleton in-memory cache adapter instance.

    Uses lru_cache to maintain a single cache instance across requests,
    ensuring cached data persists for the process lifetime.

    Returns:
        In-memory cache adapter for response caching.
    """
    return MemoryCacheAdapter()


def get_generate_message_use_case() -> GenerateMessageUseCase:
    """
    Assemble and provide the GenerateMessageUseCase with all dependencies.

    This is the main factory function that wires together:
    - Infrastructure adapters (LLM, Cache)
    - Domain services (StrategySelector, SeniorityInferrer, ICPMatcher)
    - Application services (PromptOrchestrator, QualityGate, EntityMapper)

    A new use case instance is created per request to ensure thread safety
    and isolation, while infrastructure adapters are reused via caching.

    Returns:
        Fully configured GenerateMessageUseCase ready for execution.

    Example:
        >>> use_case = get_generate_message_use_case()
        >>> response = await use_case.execute(request)
    """
    settings = get_setting()
    llm = get_llm_adapter()
    cache = get_cache_adapter()

    strategy_selector = StrategySelector()
    seniority_inferrer = SeniorityInferrer()
    icp_matcher = ICPMatcher()
    entity_mapper = EntityMapper()

    prompt_orchestrator = PromptChainOrchestrator(llm=llm)
    scorer = MessageScorer()
    quality_gate = QualityGate(
        orchestrator=prompt_orchestrator,
        scorer=scorer,
        threshold=settings.quality_threshold,
        max_attempts=settings.max_generation_attempts,
    )

    return GenerateMessageUseCase(
        llm=llm,
        cache=cache,
        prompt_orchestrator=prompt_orchestrator,
        quality_gate=quality_gate,
        strategy_selector=strategy_selector,
        seniority_inferrer=seniority_inferrer,
        icp_matcher=icp_matcher,
        entity_mapper=entity_mapper,
    )
