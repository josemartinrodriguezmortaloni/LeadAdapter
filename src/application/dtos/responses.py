"""
DTOs de Response para la API de LeadAdapter.

Este módulo contiene los Data Transfer Objects (DTOs) que definen
la estructura de las respuestas de la API. Usan Pydantic para
serialización automática a JSON.

Note:
    Los DTOs de response se construyen en los Use Cases a partir
    de las entidades de dominio y datos adicionales de metadata.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class QualityBreakdownDTO(BaseModel):
    """
    Desglose del score de calidad del mensaje.

    Cada dimensión tiene un peso específico que suma hasta 10 puntos:
    - Personalización (0-3): Uso de nombre, empresa, contexto específico
    - Anti-spam (0-3): Ausencia de frases genéricas y spam
    - Estructura (0-2): Hook, propuesta de valor, CTA
    - Tono (0-2): Adecuación al seniority y contexto

    Attributes:
        personalization: Score de personalización (0-3 puntos).
        anti_spam: Score anti-spam (0-3 puntos).
        structure: Score de estructura (0-2 puntos).
        tone: Score de tono (0-2 puntos).

    Example:
        >>> breakdown = QualityBreakdownDTO(
        ...     personalization=2.5,
        ...     anti_spam=2.0,
        ...     structure=1.5,
        ...     tone=1.5,
        ... )
        >>> total = sum([breakdown.personalization, breakdown.anti_spam,
        ...              breakdown.structure, breakdown.tone])
        >>> print(total)  # 7.5
    """

    personalization: float = Field(..., ge=0, le=3, description="Score de personalización (0-3)")
    anti_spam: float = Field(..., ge=0, le=3, description="Score anti-spam (0-3)")
    structure: float = Field(..., ge=0, le=2, description="Score de estructura (0-2)")
    tone: float = Field(..., ge=0, le=2, description="Score de tono (0-2)")


class QualityDTO(BaseModel):
    """
    Evaluación de calidad del mensaje generado.

    Contiene el score total, el desglose por dimensión, y si
    el mensaje pasó el umbral de calidad (default: 6.0).

    Attributes:
        score: Score total de calidad (0-10).
        breakdown: Desglose por dimensión de calidad.
        passes_threshold: True si score >= 6.0 (umbral configurable).

    Example:
        >>> quality = QualityDTO(
        ...     score=7.5,
        ...     breakdown=QualityBreakdownDTO(...),
        ...     passes_threshold=True,
        ... )
    """

    score: float = Field(..., ge=0, le=10, description="Score total (0-10)")
    breakdown: QualityBreakdownDTO = Field(..., description="Desglose por dimensión")
    passes_threshold: bool = Field(..., description="Si pasó el umbral de calidad")


class MetadataDTO(BaseModel):
    """
    Metadata técnica de la generación del mensaje.

    Información útil para debugging, monitoreo de costos,
    y análisis de performance.

    Attributes:
        tokens_used: Total de tokens consumidos (prompt + response).
        generation_time_ms: Tiempo de generación en milisegundos.
        model_used: Modelo de LLM utilizado (ej: "gpt-4o-mini").
        attempts: Número de intentos hasta pasar el quality gate.

    Example:
        >>> metadata = MetadataDTO(
        ...     tokens_used=450,
        ...     generation_time_ms=2847,
        ...     model_used="gpt-4o-mini",
        ...     attempts=1,
        ... )
    """

    tokens_used: int = Field(..., ge=0, description="Tokens consumidos")
    generation_time_ms: int = Field(..., ge=0, description="Tiempo de generación (ms)")
    model_used: str = Field(..., description="Modelo de LLM utilizado")
    attempts: int = Field(1, ge=1, description="Intentos hasta pasar quality gate")


class GenerateMessageResponse(BaseModel):
    """
    Response exitoso de generación de mensaje.

    Contiene el mensaje generado, su evaluación de calidad,
    la estrategia utilizada y metadata técnica.

    Attributes:
        message_id: ID único del mensaje generado (formato: msg_xxxxxxxxxxxx).
        content: Contenido del mensaje generado.
        quality: Evaluación de calidad con score y desglose.
        strategy_used: Estrategia de personalización utilizada:
            - TECHNICAL_PEER: Comunicación entre pares técnicos
            - BUSINESS_VALUE: Enfoque en ROI y métricas
            - PROBLEM_SOLUTION: Ataque a pain point específico
            - SOCIAL_PROOF: Uso de casos de éxito
            - CURIOSITY_HOOK: Pregunta intrigante
            - MUTUAL_CONNECTION: Contexto en común
        metadata: Información técnica de la generación.
        created_at: Timestamp de creación (UTC).

    Example:
        >>> response = GenerateMessageResponse(
        ...     message_id="msg_abc123def456",
        ...     content="Hola Mateo, vi que llevas más de 6 años...",
        ...     quality=QualityDTO(score=7.5, ...),
        ...     strategy_used="TECHNICAL_PEER",
        ...     metadata=MetadataDTO(...),
        ... )
    """

    message_id: str = Field(..., description="ID único del mensaje")
    content: str = Field(..., description="Contenido del mensaje generado")
    quality: QualityDTO = Field(..., description="Evaluación de calidad")
    strategy_used: str = Field(..., description="Estrategia de personalización usada")
    metadata: MetadataDTO = Field(..., description="Metadata técnica")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp de creación (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message_id": "msg_abc123def456",
                "content": "Hola Mateo, vi que llevas más de 6 años...",
                "quality": {
                    "score": 7.5,
                    "breakdown": {
                        "personalization": 2.5,
                        "anti_spam": 2.0,
                        "structure": 1.5,
                        "tone": 1.5,
                    },
                    "passes_threshold": True,
                },
                "strategy_used": "TECHNICAL_PEER",
                "metadata": {
                    "tokens_used": 450,
                    "generation_time_ms": 2847,
                    "model_used": "gpt-4o-mini",
                    "attempts": 1,
                },
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Response de error estándar de la API.

    Formato consistente para todos los errores, permitiendo
    a los clientes parsear y manejar errores de forma uniforme.

    Attributes:
        error: Mensaje de error legible para humanos.
        detail: Detalle adicional del error (opcional).
        code: Código de error para manejo programático:
            - INVALID_REQUEST: Request malformado o validación fallida
            - LEAD_NOT_FOUND: Lead no encontrado
            - QUALITY_THRESHOLD_NOT_MET: Mensaje no pasó quality gate
            - LLM_ERROR: Error del proveedor de LLM
            - INTERNAL_ERROR: Error interno del servidor

    Example:
        >>> error = ErrorResponse(
        ...     error="El mensaje no alcanzó el umbral de calidad",
        ...     detail="Score: 4.5, Threshold: 6.0",
        ...     code="QUALITY_THRESHOLD_NOT_MET",
        ... )
    """

    error: str = Field(..., description="Mensaje de error legible")
    detail: str | None = Field(None, description="Detalle adicional")
    code: str = Field(..., description="Código de error para manejo programático")


class HealthResponse(BaseModel):
    """
    Response del endpoint de health check.

    Usado por load balancers y sistemas de monitoreo para
    verificar que el servicio está funcionando correctamente.

    Attributes:
        status: Estado del servicio ("healthy" o "unhealthy").
        version: Versión de la API (ej: "1.0.0").
        timestamp: Timestamp del check (UTC).

    Example:
        >>> health = HealthResponse(
        ...     status="healthy",
        ...     version="1.0.0",
        ... )
    """

    status: str = Field("healthy", description="Estado del servicio")
    version: str = Field(..., description="Versión de la API")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp del check (UTC)",
    )
