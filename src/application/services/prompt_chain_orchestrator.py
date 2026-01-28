import json
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
from domain.value_objects.product import Product
from infrastructure.prompts.classify_lead import (
    CLASSIFY_LEAD_SYSTEM,
    build_classify_lead_prompt,
)
from infrastructure.prompts.generate_message import (
    GENERATE_MESSAGE_SYSTEM,
    build_generate_message_prompt,
)
from infrastructure.prompts.infer_context import INFER_CONTEXT_SYSTEM, build_infer_context_prompt


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
    ) -> tuple[str, int, str]:
        """
        Execute the full prompt chain pipeline.

        Returns:
            Tuple of (generated_message, total_tokens_used, model_used).
        """
        total_tokens = 0
        model_used = ""

        # Step 1: Classify lead role
        classification, step1_tokens = await self._classify_lead(lead, seniority)
        total_tokens += step1_tokens

        # Get product for ICP (used in steps 2 and 3)
        product = playbook.get_product_for_icp(matched_icp) if matched_icp else None

        # Step 2: Infer context (pain points, hooks)
        context, step2_tokens = await self._infer_context(
            lead=lead,
            classification=classification,
            playbook=playbook,
            matched_icp=matched_icp,
            product=product,
        )
        total_tokens += step2_tokens

        # Step 3: Generate final message
        message_content, step3_tokens, model_used = await self._generate_message(
            lead=lead,
            sender=sender,
            playbook=playbook,
            channel=channel,
            sequence_step=sequence_step,
            strategy=strategy,
            context=context,
            seniority=seniority,
            product=product,
        )
        total_tokens += step3_tokens

        return message_content, total_tokens, model_used

    async def _classify_lead(
        self, lead: Lead, seniority: Seniority
    ) -> tuple[LeadClassification, int]:
        """Step 1: Classify the lead's role type."""
        prompt = build_classify_lead_prompt(
            job_title=lead.job_title,
            company_name=lead.company_name,
            seniority=seniority.value,
        )

        response = await self.llm.complete_json(
            prompt=prompt,
            system_prompt=CLASSIFY_LEAD_SYSTEM,
            temperature=0.1,  # Low temperature for consistent classification
        )

        parsed = json.loads(response.content)
        classification = LeadClassification(
            role_type=parsed["role_type"],
            confidence=float(parsed["confidence"]),
        )

        return classification, response.total_tokens

    async def _infer_context(
        self,
        lead: Lead,
        classification: LeadClassification,
        playbook: Playbook,
        matched_icp: ICPProfile | None,
        product: Product | None,
    ) -> tuple[InferredContext, int]:
        """Step 2: Infer pain points and hooks for personalization."""
        industry = (
            matched_icp.target_industries[0]
            if matched_icp and matched_icp.target_industries
            else None
        )
        company_size = (
            f"{matched_icp.company_size_range[0]} - {matched_icp.company_size_range[1]}"
            if matched_icp
            else None
        )
        product_category = product.category if product else playbook.products[0].category
        prompt = build_infer_context_prompt(
            job_title=lead.job_title,
            company_name=lead.company_name,
            industry=industry,
            role_type=classification.role_type,
            product_category=product_category,
            years_in_role=lead.years_in_current_role(),
            company_size=company_size,
        )
        response = await self.llm.complete_json(
            prompt=prompt, system_prompt=INFER_CONTEXT_SYSTEM, temperature=0.1
        )
        parsed = json.loads(response.content)
        inferred_context = InferredContext(
            pain_points=parsed["pain_points"],
            hooks=parsed["hooks"],
            talking_points=parsed["talking_points"],
        )
        return inferred_context, response.total_tokens

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
        product: Product | None,
    ) -> tuple[str, int, str]:
        """Step 3: Generate the final personalized message."""
        product_name = product.name if product else playbook.products[0].name
        product_benefit = (
            product.key_benefits[0]
            if product and product.key_benefits
            else "mejora tu productividad"
        )

        prompt = build_generate_message_prompt(
            lead_name=lead.first_name,
            lead_title=lead.job_title,
            lead_company=lead.company_name,
            sender_name=sender.name,
            sender_company=sender.company_name,
            channel=channel,
            sequence_step=sequence_step,
            strategy=strategy,
            pain_points=context.pain_points,
            hooks=context.hooks,
            product_name=product_name,
            product_benefit=product_benefit,
            communication_style=playbook.communication_style,
            years_in_role=lead.years_in_current_role(),
            seniority_tone=seniority.communication_tone,
        )

        response = await self.llm.complete(
            prompt=prompt, system_prompt=GENERATE_MESSAGE_SYSTEM, temperature=0.5
        )
        return response.content, response.total_tokens, response.model
