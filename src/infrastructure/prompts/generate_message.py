from domain.enums.channel import Channel
from domain.enums.message_strategy import MessageStrategy
from domain.enums.sequence_step import SequenceStep

GENERATE_MESSAGE_SYSTEM = """You are an expert B2B copywriter. Generate personalized outreach messages that:
1. Feel genuine and human (not templated)
2. Reference specific details about the prospect
3. Have a clear value proposition
4. End with a soft call-to-action

NEVER use:
- Generic phrases like "game changer", "revolucionar", "líder del mercado"
- Aggressive sales language
- False urgency

Respond with ONLY the message content, no explanations."""


def build_generate_message_prompt(
    lead_name: str,
    lead_title: str,
    lead_company: str,
    sender_name: str,
    sender_company: str,
    channel: Channel,
    sequence_step: SequenceStep,
    strategy: MessageStrategy,
    pain_points: list[str],
    hooks: list[str],
    product_name: str,
    product_benefit: str,
    communication_style: str,
    years_in_role: int | None = None,
) -> str:
    """Construye el prompt para generar mensaje."""

    context_parts = []

    if years_in_role:
        context_parts.append(f"- Has been in their role for {years_in_role}+ years")

    context = "\n".join(context_parts) if context_parts else "- No additional context"

    pain_points_str = "\n".join(f"- {p}" for p in pain_points[:3])
    hooks_str = "\n".join(f"- {h}" for h in hooks[:2])

    return f"""Generate a {channel.value} message for {sequence_step.value}.

LEAD:
- Name: {lead_name}
- Title: {lead_title}
- Company: {lead_company}
{context}

SENDER:
- Name: {sender_name}
- Company: {sender_company}

STRATEGY: {strategy.value} - {strategy.description}

INFERRED PAIN POINTS:
{pain_points_str}

PERSONALIZATION HOOKS:
{hooks_str}

PRODUCT TO MENTION:
- Name: {product_name}
- Key Benefit: {product_benefit}

TONE: {communication_style}

MAX LENGTH: {channel.max_length} characters

Write the message now:"""
