from dataclasses import dataclass

from application.ports.llm_port import LLMPort
from domain.entities.lead import Lead
from domain.entities.playbook import Playbook
from domain.entities.sender import Sender
from domain.enums.channel import Channel
from domain.enums.message_strategy import MessageStrategy
from domain.enums.seniority import Seniority
from domain.enums.sequence_step import SequenceStep
from domain.value_objects.icp_profile import ICPProfile


@dataclass()
class LeadClassification:
    role_type: str
    confidence: float


@dataclass()
class InferredContext:
    pain_points: list[str]
    hooks: list[str]
    talking_points: list[str]


@dataclass()
class PromptChainOrchestrator:
    llm: LLMPort

    async def execute_chain(
        self,
        lead: Lead,
        sender: Sender,
        playbook: Playbook,
        channel: Channel,
        sequence_step: SequenceStep,
        strategy: MessageStrategy,
        matched_icp: ICPProfile | None,
        seniority: Seniority,
    ) -> tuple[str, int]:
        """
        Execute the full prompt chain pipeline.

        Returns:
            Tuple of (generated_message, total_tokens_used).
        """
        total_tokens = 0

        # Step 1: Classify lead role
        classification, step1_tokens = await self._classify_lead(lead)
        total_tokens += step1_tokens

        # Step 2: Infer context (pain points, hooks)
        context, step2_tokens = await self._infer_context(
            lead=lead,
            classification=classification,
            playbook=playbook,
            matched_icp=matched_icp,
        )
        total_tokens += step2_tokens

        # Step 3: Generate final message
        message_content, step3_tokens = await self._generate_message(
            lead=lead,
            sender=sender,
            playbook=playbook,
            channel=channel,
            sequence_step=sequence_step,
            strategy=strategy,
            context=context,
            seniority=seniority,
        )
        total_tokens += step3_tokens

        return message_content, total_tokens

    async def _classify_lead(self, lead: Lead) -> tuple[LeadClassification, int]:
        """Step 1: Classify the lead's role type."""
        # TODO: Implement LLM call with classification prompt
        ...

    async def _infer_context(
        self,
        lead: Lead,
        classification: LeadClassification,
        playbook: Playbook,
        matched_icp: ICPProfile | None,
    ) -> tuple[InferredContext, int]:
        """Step 2: Infer pain points and hooks for personalization."""
        # TODO: Implement LLM call with inference prompt
        ...

    async def _generate_message(
        self,
        lead: Lead,
        sender: Sender,
        playbook: Playbook,
        channel: Channel,
        sequence_step: SequenceStep,
        strategy: MessageStrategy,
        context: InferredContext,
        seniority: Seniority,
    ) -> tuple[str, int]:
        """Step 3: Generate the final personalized message."""
        # TODO: Implement LLM call with generation prompt
        ...
