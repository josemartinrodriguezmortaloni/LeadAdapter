"""
Tests para PromptChainOrchestrator.

Testea el pipeline de 3 pasos:
1. Clasificar lead (role_type)
2. Inferir contexto (pain_points, hooks)
3. Generar mensaje personalizado
"""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

# Agregar src al path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from application.ports.llm_port import LLMPort, LLMResponse
from application.services.prompt_chain_orchestrator import (
    InferredContext,
    LeadClassification,
    PromptChainOrchestrator,
)
from domain.entities.lead import Lead
from domain.entities.playbook import Playbook
from domain.entities.sender import Sender
from domain.enums.channel import Channel
from domain.enums.message_strategy import MessageStrategy
from domain.enums.seniority import Seniority
from domain.enums.sequence_step import SequenceStep
from domain.value_objects.icp_profile import ICPProfile
from domain.value_objects.product import Product
from domain.value_objects.work_experience import WorkExperience


# ============================================================================
# FIXTURES
# ============================================================================


class MockLLM(LLMPort):
    """Mock LLM que retorna respuestas predefinidas."""

    def __init__(self, responses: list[str] | None = None):
        self._responses = responses or []
        self._call_index = 0
        self.calls: list[dict] = []

    def set_responses(self, responses: list[str]) -> None:
        """Configura las respuestas que el mock retornara."""
        self._responses = responses
        self._call_index = 0

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1000,
    ) -> LLMResponse:
        self.calls.append(
            {
                "method": "complete",
                "prompt": prompt,
                "system_prompt": system_prompt,
                "temperature": temperature,
            }
        )
        content = self._get_next_response()
        return LLMResponse(
            content=content,
            prompt_tokens=100,
            response_tokens=50,
            model="mock-model",
        )

    async def complete_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> LLMResponse:
        self.calls.append(
            {
                "method": "complete_json",
                "prompt": prompt,
                "system_prompt": system_prompt,
                "temperature": temperature,
            }
        )
        content = self._get_next_response()
        return LLMResponse(
            content=content,
            prompt_tokens=100,
            response_tokens=50,
            model="mock-model",
        )

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def _get_next_response(self) -> str:
        if self._call_index >= len(self._responses):
            raise ValueError(
                f"MockLLM: No hay mas respuestas configuradas. "
                f"Se esperaba respuesta #{self._call_index + 1}"
            )
        response = self._responses[self._call_index]
        self._call_index += 1
        return response


@pytest.fixture
def mock_llm() -> MockLLM:
    """Fixture para MockLLM."""
    return MockLLM()


@pytest.fixture
def sample_lead() -> Lead:
    """Lead de ejemplo para tests."""
    return Lead(
        first_name="Juan",
        last_name="Perez",
        job_title="CTO",
        company_name="TechStartup",
        work_experience=[
            WorkExperience(
                company="TechStartup",
                title="CTO",
                start_date=date(2020, 1, 1),
                end_date=None,
            ),
        ],
    )


@pytest.fixture
def sample_sender() -> Sender:
    """Sender de ejemplo para tests."""
    return Sender(
        name="Maria Garcia",
        company_name="SalesTools Inc",
        job_title="Account Executive",
    )


@pytest.fixture
def sample_product() -> Product:
    """Producto de ejemplo para tests."""
    return Product(
        name="LeadAdapter Pro",
        description="Plataforma de personalizacion de mensajes",
        category="Sales Automation",
        key_benefits=[
            "Aumenta tasa de respuesta 3x",
            "Reduce tiempo de prospecting 50%",
        ],
        target_problems=[
            "Baja tasa de respuesta en cold outreach",
            "Tiempo excesivo en personalizacion manual",
        ],
    )


@pytest.fixture
def sample_playbook(sample_product: Product) -> Playbook:
    """Playbook de ejemplo para tests."""
    return Playbook(
        communication_style="profesional pero cercano",
        products=[sample_product],
        icp_profiles=[],
        success_cases=["Cliente X aumento conversiones 40%"],
        value_propositions=["Personalizacion a escala con IA"],
    )


@pytest.fixture
def sample_icp() -> ICPProfile:
    """ICP de ejemplo para tests."""
    return ICPProfile(
        name="Decision Makers Tech",
        target_titles=["CTO", "VP Engineering", "Head of Engineering"],
        target_industries=["SaaS", "Fintech"],
        company_size_range=(50, 500),
        pain_points=["Escalar el equipo es dificil", "Deuda tecnica acumulada"],
    )


@pytest.fixture
def orchestrator(mock_llm: MockLLM) -> PromptChainOrchestrator:
    """Orchestrator con mock LLM."""
    return PromptChainOrchestrator(llm=mock_llm)


# ============================================================================
# TESTS: _classify_lead
# ============================================================================


@pytest.mark.asyncio
class TestClassifyLead:
    """Tests para el paso 1: clasificacion de lead."""

    async def test_classifies_decision_maker_correctly(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
    ):
        """Un CTO debe clasificarse como decision_maker."""
        mock_llm.set_responses(
            [
                json.dumps(
                    {
                        "role_type": "decision_maker",
                        "confidence": 0.95,
                        "reasoning": "CTO has budget authority",
                    }
                )
            ]
        )

        classification, tokens = await orchestrator._classify_lead(
            lead=sample_lead,
            seniority=Seniority.C_LEVEL,
        )

        assert classification.role_type == "decision_maker"
        assert classification.confidence == 0.95
        assert tokens == 150  # 100 prompt + 50 response

    async def test_classifies_end_user_for_junior(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
    ):
        """Un Junior Developer debe clasificarse como end_user."""
        junior_lead = Lead(
            first_name="Pedro",
            job_title="Junior Developer",
            company_name="StartupX",
        )
        mock_llm.set_responses(
            [
                json.dumps(
                    {
                        "role_type": "end_user",
                        "confidence": 0.88,
                        "reasoning": "Individual contributor",
                    }
                )
            ]
        )

        classification, _ = await orchestrator._classify_lead(
            lead=junior_lead,
            seniority=Seniority.JUNIOR,
        )

        assert classification.role_type == "end_user"

    async def test_uses_low_temperature_for_classification(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
    ):
        """Clasificacion debe usar temperature baja para consistencia."""
        mock_llm.set_responses([json.dumps({"role_type": "decision_maker", "confidence": 0.9})])

        await orchestrator._classify_lead(sample_lead, Seniority.C_LEVEL)

        assert mock_llm.calls[0]["temperature"] == 0.1

    async def test_prompt_includes_lead_info(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
    ):
        """El prompt debe incluir informacion del lead."""
        mock_llm.set_responses([json.dumps({"role_type": "decision_maker", "confidence": 0.9})])

        await orchestrator._classify_lead(sample_lead, Seniority.C_LEVEL)

        prompt = mock_llm.calls[0]["prompt"]
        assert "CTO" in prompt
        assert "TechStartup" in prompt
        assert "C_LEVEL" in prompt


# ============================================================================
# TESTS: _infer_context
# ============================================================================


@pytest.mark.asyncio
class TestInferContext:
    """Tests para el paso 2: inferencia de contexto."""

    async def test_infers_pain_points_and_hooks(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_playbook: Playbook,
        sample_icp: ICPProfile,
        sample_product: Product,
    ):
        """Debe inferir pain points, hooks y talking points."""
        mock_llm.set_responses(
            [
                json.dumps(
                    {
                        "pain_points": ["Escalar equipo tech", "Deuda tecnica"],
                        "hooks": ["Vi que estan contratando devs"],
                        "talking_points": ["Automatizacion de procesos"],
                    }
                )
            ]
        )
        classification = LeadClassification(
            role_type="decision_maker",
            confidence=0.95,
        )

        context, tokens = await orchestrator._infer_context(
            lead=sample_lead,
            classification=classification,
            playbook=sample_playbook,
            matched_icp=sample_icp,
            product=sample_product,
        )

        assert len(context.pain_points) == 2
        assert "Escalar equipo tech" in context.pain_points
        assert len(context.hooks) == 1
        assert tokens == 150

    async def test_handles_none_icp(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_playbook: Playbook,
    ):
        """Debe funcionar sin ICP matcheado."""
        mock_llm.set_responses(
            [
                json.dumps(
                    {
                        "pain_points": ["Generic pain point"],
                        "hooks": ["Generic hook"],
                        "talking_points": ["Generic point"],
                    }
                )
            ]
        )
        classification = LeadClassification(role_type="influencer", confidence=0.8)

        context, _ = await orchestrator._infer_context(
            lead=sample_lead,
            classification=classification,
            playbook=sample_playbook,
            matched_icp=None,
            product=None,
        )

        assert len(context.pain_points) == 1
        # Verifica que uso el producto default del playbook
        prompt = mock_llm.calls[0]["prompt"]
        assert "Sales Automation" in prompt  # category del producto default

    async def test_includes_industry_from_icp(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_playbook: Playbook,
        sample_icp: ICPProfile,
        sample_product: Product,
    ):
        """El prompt debe incluir la industria del ICP."""
        mock_llm.set_responses(
            [
                json.dumps(
                    {
                        "pain_points": ["Pain"],
                        "hooks": ["Hook"],
                        "talking_points": ["Point"],
                    }
                )
            ]
        )
        classification = LeadClassification(role_type="decision_maker", confidence=0.9)

        await orchestrator._infer_context(
            lead=sample_lead,
            classification=classification,
            playbook=sample_playbook,
            matched_icp=sample_icp,
            product=sample_product,
        )

        prompt = mock_llm.calls[0]["prompt"]
        assert "SaaS" in prompt  # Primera industria del ICP


# ============================================================================
# TESTS: _generate_message
# ============================================================================


@pytest.mark.asyncio
class TestGenerateMessage:
    """Tests para el paso 3: generacion de mensaje."""

    async def test_generates_personalized_message(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
        sample_product: Product,
    ):
        """Debe generar un mensaje personalizado."""
        expected_message = "Hola Juan, vi que lideras tech en TechStartup..."
        mock_llm.set_responses([expected_message])
        context = InferredContext(
            pain_points=["Escalar equipo"],
            hooks=["Estan contratando"],
            talking_points=["Automatizacion"],
        )

        message, tokens = await orchestrator._generate_message(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.LINKEDIN,
            sequence_step=SequenceStep.FIRST_CONTACT,
            strategy=MessageStrategy.BUSINESS_VALUE,
            context=context,
            seniority=Seniority.C_LEVEL,
            product=sample_product,
        )

        assert message == expected_message
        assert tokens == 150

    async def test_uses_higher_temperature_for_creativity(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
        sample_product: Product,
    ):
        """Generacion de mensaje debe usar temperature mas alta."""
        mock_llm.set_responses(["Mensaje generado"])
        context = InferredContext(
            pain_points=["Pain"],
            hooks=["Hook"],
            talking_points=["Point"],
        )

        await orchestrator._generate_message(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.EMAIL,
            sequence_step=SequenceStep.FOLLOW_UP_1,
            strategy=MessageStrategy.PROBLEM_SOLUTION,
            context=context,
            seniority=Seniority.MANAGER,
            product=sample_product,
        )

        assert mock_llm.calls[0]["temperature"] == 0.5

    async def test_includes_all_context_in_prompt(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
        sample_product: Product,
    ):
        """El prompt debe incluir toda la informacion relevante."""
        mock_llm.set_responses(["Mensaje"])
        context = InferredContext(
            pain_points=["Escalar equipo tech"],
            hooks=["Contratando developers"],
            talking_points=["Automatizacion"],
        )

        await orchestrator._generate_message(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.LINKEDIN,
            sequence_step=SequenceStep.FIRST_CONTACT,
            strategy=MessageStrategy.TECHNICAL_PEER,
            context=context,
            seniority=Seniority.C_LEVEL,
            product=sample_product,
        )

        prompt = mock_llm.calls[0]["prompt"]
        # Lead info
        assert "Juan" in prompt
        assert "CTO" in prompt
        assert "TechStartup" in prompt
        # Sender info
        assert "Maria Garcia" in prompt
        assert "SalesTools Inc" in prompt
        # Context
        assert "Escalar equipo tech" in prompt
        assert "Contratando developers" in prompt
        # Product
        assert "LeadAdapter Pro" in prompt

    async def test_uses_fallback_product_when_none(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
    ):
        """Debe usar el primer producto del playbook como fallback."""
        mock_llm.set_responses(["Mensaje"])
        context = InferredContext(
            pain_points=["Pain"],
            hooks=["Hook"],
            talking_points=["Point"],
        )

        await orchestrator._generate_message(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.EMAIL,
            sequence_step=SequenceStep.FIRST_CONTACT,
            strategy=MessageStrategy.CURIOSITY_HOOK,
            context=context,
            seniority=Seniority.MID,
            product=None,  # Sin producto especifico
        )

        prompt = mock_llm.calls[0]["prompt"]
        assert "LeadAdapter Pro" in prompt  # Primer producto del playbook


# ============================================================================
# TESTS: execute_chain (integracion)
# ============================================================================


@pytest.mark.asyncio
class TestExecuteChain:
    """Tests de integracion para el pipeline completo."""

    async def test_executes_full_chain(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
        sample_icp: ICPProfile,
    ):
        """Debe ejecutar los 3 pasos en orden."""
        mock_llm.set_responses(
            [
                # Step 1: classify
                json.dumps({"role_type": "decision_maker", "confidence": 0.95}),
                # Step 2: infer context
                json.dumps(
                    {
                        "pain_points": ["Scaling challenges"],
                        "hooks": ["Series A funding"],
                        "talking_points": ["AI automation"],
                    }
                ),
                # Step 3: generate message
                "Hola Juan, felicitaciones por la Serie A...",
            ]
        )

        message, total_tokens = await orchestrator.execute_chain(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.LINKEDIN,
            sequence_step=SequenceStep.FIRST_CONTACT,
            strategy=MessageStrategy.BUSINESS_VALUE,
            matched_icp=sample_icp,
            seniority=Seniority.C_LEVEL,
        )

        assert "Hola Juan" in message
        assert total_tokens == 450  # 3 calls x 150 tokens
        assert len(mock_llm.calls) == 3

    async def test_chain_without_icp(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
    ):
        """El pipeline debe funcionar sin ICP matcheado."""
        mock_llm.set_responses(
            [
                json.dumps({"role_type": "influencer", "confidence": 0.8}),
                json.dumps(
                    {
                        "pain_points": ["Generic pain"],
                        "hooks": ["Generic hook"],
                        "talking_points": ["Generic point"],
                    }
                ),
                "Mensaje generico pero personalizado",
            ]
        )

        message, total_tokens = await orchestrator.execute_chain(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.EMAIL,
            sequence_step=SequenceStep.FOLLOW_UP_1,
            strategy=MessageStrategy.PROBLEM_SOLUTION,
            matched_icp=None,
            seniority=Seniority.MANAGER,
        )

        assert message == "Mensaje generico pero personalizado"
        assert total_tokens == 450

    async def test_accumulates_tokens_correctly(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
    ):
        """Debe sumar tokens de todos los pasos."""
        mock_llm.set_responses(
            [
                json.dumps({"role_type": "end_user", "confidence": 0.7}),
                json.dumps(
                    {
                        "pain_points": ["Pain"],
                        "hooks": ["Hook"],
                        "talking_points": ["Point"],
                    }
                ),
                "Final message",
            ]
        )

        _, total_tokens = await orchestrator.execute_chain(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.LINKEDIN,
            sequence_step=SequenceStep.BREAKUP,
            strategy=MessageStrategy.SOCIAL_PROOF,
            matched_icp=None,
            seniority=Seniority.SENIOR,
        )

        # 3 llamadas x (100 prompt + 50 response) = 450
        assert total_tokens == 450

    async def test_passes_product_through_chain(
        self,
        orchestrator: PromptChainOrchestrator,
        mock_llm: MockLLM,
        sample_lead: Lead,
        sample_sender: Sender,
        sample_playbook: Playbook,
        sample_icp: ICPProfile,
    ):
        """El producto debe pasarse del paso 2 al paso 3."""
        mock_llm.set_responses(
            [
                json.dumps({"role_type": "decision_maker", "confidence": 0.9}),
                json.dumps(
                    {
                        "pain_points": ["Pain"],
                        "hooks": ["Hook"],
                        "talking_points": ["Point"],
                    }
                ),
                "Message with product",
            ]
        )

        await orchestrator.execute_chain(
            lead=sample_lead,
            sender=sample_sender,
            playbook=sample_playbook,
            channel=Channel.LINKEDIN,
            sequence_step=SequenceStep.FIRST_CONTACT,
            strategy=MessageStrategy.BUSINESS_VALUE,
            matched_icp=sample_icp,
            seniority=Seniority.C_LEVEL,
        )

        # Verifica que el producto se usa en infer_context (paso 2)
        infer_prompt = mock_llm.calls[1]["prompt"]
        assert "Sales Automation" in infer_prompt

        # Verifica que el producto se usa en generate_message (paso 3)
        generate_prompt = mock_llm.calls[2]["prompt"]
        assert "LeadAdapter Pro" in generate_prompt
