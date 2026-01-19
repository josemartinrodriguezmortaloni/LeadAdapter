"""
DTOs de Request para la API de LeadAdapter.

Este módulo contiene los Data Transfer Objects (DTOs) que definen
la estructura de los requests entrantes a la API. Usan Pydantic
para validación automática.

Note:
    Los DTOs son diferentes a las entidades de dominio. Los DTOs:
    - Viven en Application Layer
    - Usan Pydantic para validación
    - Se convierten a entidades de dominio en los Use Cases
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ============ Nested DTOs ============


class WorkExperienceDTO(BaseModel):
    """
    Experiencia laboral de un lead.

    Representa un puesto de trabajo en el historial del lead.
    Se usa para calcular años de experiencia y entender el contexto profesional.

    Attributes:
        company: Nombre de la empresa.
        title: Título del puesto.
        start_date: Fecha de inicio en el puesto.
        end_date: Fecha de fin. None indica puesto actual.
        description: Descripción opcional del rol.
    """

    company: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None


class CampaignHistoryDTO(BaseModel):
    """
    Historial de contactos previos con el lead.

    Permite personalizar el mensaje según interacciones anteriores.
    Si el lead ya fue contactado, se ajusta el tono y la estrategia.

    Attributes:
        total_attempts: Número total de intentos de contacto previos.
        last_contact_date: Fecha del último contacto.
        last_channel: Canal usado en el último contacto ("linkedin", "email").
        responses_received: Número de respuestas recibidas del lead.
    """

    total_attempts: int = 0
    last_contact_date: Optional[datetime] = None
    last_channel: Optional[str] = None
    responses_received: int = 0


class ProductDTO(BaseModel):
    """
    Producto o servicio a promocionar.

    Define qué se está vendiendo y sus beneficios clave.
    Se usa para personalizar la propuesta de valor en el mensaje.

    Attributes:
        name: Nombre del producto/servicio.
        description: Descripción breve del producto.
        key_benefits: Lista de beneficios principales (ej: ["Ahorra tiempo", "Reduce costos"]).
        target_problems: Problemas que resuelve (ej: ["Deuda técnica", "Falta de documentación"]).
    """

    name: str
    description: str
    key_benefits: list[str] = Field(default_factory=list)
    target_problems: list[str] = Field(default_factory=list)


class ICPProfileDTO(BaseModel):
    """
    Perfil de Cliente Ideal (Ideal Customer Profile).

    Define las características del cliente objetivo para matching.
    Se usa para seleccionar pain points y estrategias relevantes.

    Attributes:
        name: Nombre descriptivo del ICP (ej: "Decision Makers Tech").
        target_titles: Títulos de puesto objetivo (ej: ["CTO", "VP Engineering"]).
        target_industries: Industrias objetivo (ej: ["SaaS", "Fintech"]).
        pain_points: Problemas típicos de este perfil.
        keywords_sector: Keywords del sector para matching avanzado.
    """

    name: str
    target_titles: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    keywords_sector: list[str] = Field(default_factory=list)


# ============ Main Request DTOs ============


class LeadDTO(BaseModel):
    """
    Datos del prospecto/lead a contactar.

    Contiene toda la información disponible sobre el lead que se usará
    para personalizar el mensaje: nombre, puesto, empresa, historial, etc.

    Attributes:
        first_name: Nombre del lead (requerido).
        last_name: Apellido del lead (opcional).
        job_title: Título del puesto actual (requerido). Se usa para inferir seniority.
        company_name: Nombre de la empresa actual (requerido).
        work_experience: Lista de experiencias laborales previas.
        campaign_history: Historial de contactos previos con este lead.
        bio: Biografía o descripción del perfil (de LinkedIn, etc.).
        skills: Lista de habilidades/tecnologías del lead.
        linkedin_url: URL del perfil de LinkedIn.

    Example:
        >>> lead = LeadDTO(
        ...     first_name="Mateo",
        ...     last_name="Gutierrez",
        ...     job_title="Senior PHP Developer",
        ...     company_name="Tecnocom",
        ...     skills=["PHP", "Laravel", "AWS"],
        ... )
    """

    first_name: str = Field(..., min_length=1, description="Nombre del lead")
    last_name: Optional[str] = Field(None, description="Apellido del lead")
    job_title: str = Field(..., min_length=1, description="Título del puesto actual")
    company_name: str = Field(..., min_length=1, description="Empresa actual")
    work_experience: list[WorkExperienceDTO] = Field(default_factory=list)
    campaign_history: Optional[CampaignHistoryDTO] = None
    bio: Optional[str] = Field(None, description="Biografía del perfil")
    skills: list[str] = Field(default_factory=list, description="Habilidades técnicas")
    linkedin_url: Optional[str] = Field(None, description="URL de LinkedIn")

    @field_validator("first_name", "job_title", "company_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Valida que los campos requeridos no estén vacíos después de strip."""
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class SenderDTO(BaseModel):
    """
    Datos del remitente que envía el mensaje.

    Representa al SDR, vendedor o persona que contacta al lead.
    Se usa para personalizar la firma y el contexto del mensaje.

    Attributes:
        name: Nombre del remitente (requerido).
        company_name: Empresa del remitente (requerido).
        job_title: Título del puesto del remitente (opcional).
        email: Email de contacto (opcional).

    Example:
        >>> sender = SenderDTO(
        ...     name="Fernando",
        ...     company_name="Synapsale",
        ...     job_title="CTO",
        ... )
    """

    name: str = Field(..., min_length=1, description="Nombre del remitente")
    company_name: str = Field(..., min_length=1, description="Empresa del remitente")
    job_title: Optional[str] = Field(None, description="Título del puesto")
    email: Optional[str] = Field(None, description="Email de contacto")


class PlaybookDTO(BaseModel):
    """
    Configuración comercial para la generación de mensajes.

    Contiene el estilo de comunicación, productos, ICPs y material
    de ventas que se usa para personalizar los mensajes.

    Attributes:
        communication_style: Estilo de comunicación (ej: "B2B directo", "Consultivo").
        products: Lista de productos/servicios a promocionar (mínimo 1).
        icp_profiles: Perfiles de cliente ideal para matching.
        success_cases: Casos de éxito para social proof.
        common_objections: Objeciones comunes y cómo manejarlas.
        value_propositions: Propuestas de valor principales.

    Example:
        >>> playbook = PlaybookDTO(
        ...     communication_style="B2B directo",
        ...     products=[ProductDTO(name="DevPlatform", description="...")],
        ...     value_propositions=["Reduce tiempo de desarrollo en 40%"],
        ... )
    """

    communication_style: str = Field(..., min_length=1, description="Estilo de comunicación")
    products: list[ProductDTO] = Field(..., min_length=1, description="Productos a promocionar")
    icp_profiles: list[ICPProfileDTO] = Field(default_factory=list)
    success_cases: list[str] = Field(default_factory=list)
    common_objections: list[str] = Field(default_factory=list)
    value_propositions: list[str] = Field(default_factory=list)


class GenerateMessageRequest(BaseModel):
    """
    Request principal para generar un mensaje personalizado.

    Combina toda la información necesaria para generar un mensaje:
    el canal, paso en la secuencia, datos del lead, remitente y playbook.

    Attributes:
        channel: Canal de comunicación ("linkedin" o "email").
        sequence_step: Paso en la secuencia de outreach:
            - "first_contact": Primer contacto
            - "follow_up_1": Primer follow-up
            - "follow_up_2": Segundo follow-up
            - "breakup": Mensaje de despedida
        lead: Datos del prospecto a contactar.
        sender: Datos del remitente.
        playbook: Configuración comercial.

    Example:
        >>> request = GenerateMessageRequest(
        ...     channel="linkedin",
        ...     sequence_step="first_contact",
        ...     lead=LeadDTO(...),
        ...     sender=SenderDTO(...),
        ...     playbook=PlaybookDTO(...),
        ... )
    """

    channel: str = Field(
        ...,
        pattern="^(linkedin|email)$",
        description="Canal: 'linkedin' o 'email'",
    )
    sequence_step: str = Field(
        ...,
        pattern="^(first_contact|follow_up_1|follow_up_2|breakup)$",
        description="Paso en la secuencia de outreach",
    )
    lead: LeadDTO = Field(..., description="Datos del prospecto")
    sender: SenderDTO = Field(..., description="Datos del remitente")
    playbook: PlaybookDTO = Field(..., description="Configuración comercial")

    model_config = {
        "json_schema_extra": {
            "example": {
                "channel": "linkedin",
                "sequence_step": "first_contact",
                "lead": {
                    "first_name": "Mateo",
                    "last_name": "Gutierrez",
                    "job_title": "Senior PHP Developer",
                    "company_name": "Tecnocom",
                },
                "sender": {
                    "name": "Fernando",
                    "company_name": "Synapsale",
                    "job_title": "CTO",
                },
                "playbook": {
                    "communication_style": "B2B directo",
                    "products": [
                        {
                            "name": "DevPlatform",
                            "description": "Plataforma de desarrollo",
                            "key_benefits": ["Velocidad", "Calidad"],
                        }
                    ],
                },
            }
        }
    }
