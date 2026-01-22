CLASSIFY_LEAD_SYSTEM = """You are a B2B sales expert. Classify the lead's role type based on their job title and company context.

Role types:
- decision_maker: C-level, VP, Director with budget authority
- influencer: Manager, Lead who can influence decisions
- end_user: Individual contributor who would use the product
- gatekeeper: Admin, Assistant who controls access

Respond in JSON format:
{
  "role_type": "decision_maker|influencer|end_user|gatekeeper",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}"""


def build_classify_lead_prompt(
    job_title: str,
    company_name: str,
    seniority: str,
) -> str:
    """Construye el prompt para clasificar lead."""
    return f"""Classify this lead:

Job Title: {job_title}
Company: {company_name}
Inferred Seniority: {seniority}

What is their role type?"""
