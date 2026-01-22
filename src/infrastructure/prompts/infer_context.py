INFER_CONTEXT_SYSTEM = """You are a B2B sales research expert. Based on the lead's profile, infer likely pain points, personalization hooks, and talking points.

Consider:
1. Common challenges for this role/seniority
2. Industry-specific problems
3. Current tech trends affecting their work
4. Likely priorities based on role type

Be specific and actionable. Avoid generic statements.

Respond in JSON format:
{
  "pain_points": ["specific pain point 1", "specific pain point 2", "specific pain point 3"],
  "hooks": ["personalization hook 1", "personalization hook 2"],
  "talking_points": ["talking point 1", "talking point 2"]
}"""


def build_infer_context_prompt(
    job_title: str,
    company_name: str,
    industry: str | None,
    role_type: str,
    product_category: str,
    years_in_role: int | None = None,
    company_size: str | None = None,
) -> str:
    """Construye el prompt para inferir contexto."""
    context_parts = []

    if industry:
        context_parts.append(f"Industry: {industry}")
    if years_in_role:
        context_parts.append(f"Years in role: {years_in_role}")
    if company_size:
        context_parts.append(f"Company size: {company_size}")

    additional_context = (
        "\n".join(context_parts) if context_parts else "No additional context available"
    )

    return f"""Infer likely pain points and personalization opportunities for this lead:

LEAD PROFILE:
- Job Title: {job_title}
- Company: {company_name}
- Role Type: {role_type}
{additional_context}

PRODUCT CONTEXT:
- Category: {product_category}

What are their likely pain points, personalization hooks, and talking points?"""
