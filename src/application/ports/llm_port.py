"""
Puerto de aplicación para interacciones con LLMs.

Este módulo define la interfaz abstracta (Port) que cualquier
adaptador de LLM debe implementar. Sigue el patrón Ports & Adapters
de Arquitectura Hexagonal.

Example:
    >>> # En infrastructure/adapters/openai_adapter.py
    >>> class OpenAIAdapter(LLMPort):
    ...     async def complete(self, prompt, **kwargs) -> str:
    ...         # Implementación con OpenAI SDK
    ...         return response.choices[0].message.content
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMResponse:
    """Respuesta estructurada de una llamada al LLM."""

    content: str
    prompt_tokens: int
    response_tokens: int
    model: str  # Modelo usado para esta respuesta

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.response_tokens


class LLMPort(ABC):
    """
    Interfaz abstracta para interacciones con Large Language Models.

    Define el contrato que cualquier adaptador de LLM (OpenAI, Anthropic,
    local, mock) debe implementar. El Application Layer depende de esta
    interfaz, no de implementaciones concretas.

    Implementaciones esperadas:
        - OpenAIAdapter: Usa la API de OpenAI (gpt-4o-mini, gpt-4o)
        - AnthropicAdapter: Usa la API de Anthropic (Claude)
        - MockLLMAdapter: Para testing sin llamadas reales

    Example:
        >>> class MockLLM(LLMPort):
        ...     async def complete(self, prompt, **kwargs) -> str:
        ...         return "Respuesta mock para testing"
        ...
        >>> use_case = GenerateMessageUseCase(llm=MockLLM(), ...)
    """

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1000,
    ) -> LLMResponse:
        """
        Genera una completion de texto desde el LLM.

        Envía un prompt al modelo y retorna la respuesta generada.
        Este es el método principal para generación de texto libre.

        Args:
            prompt: El mensaje del usuario a enviar al modelo.
                Debe contener el contexto necesario para la tarea.
            system_prompt: Instrucciones de sistema que definen el
                comportamiento del modelo. None usa el default del modelo.
            temperature: Control de creatividad/aleatoriedad (0.0-1.0).
                - 0.0: Determinístico, respuestas consistentes
                - 0.3: Balance (recomendado para tareas estructuradas)
                - 0.7+: Más creativo, mayor variabilidad
            max_tokens: Límite máximo de tokens en la respuesta.
                Previene respuestas excesivamente largas y controla costos.

        Returns:
            Texto generado por el modelo como string.

        Raises:
            LLMConnectionError: Si falla la conexión con el proveedor.
            LLMRateLimitError: Si se excede el rate limit de la API.
            LLMResponseError: Si el modelo retorna una respuesta inválida.

        Example:
            >>> response = await llm.complete(
            ...     prompt="Genera un saludo para Juan, CTO de Acme",
            ...     system_prompt="Eres un SDR profesional",
            ...     temperature=0.3,
            ... )
            >>> print(response)
            "Hola Juan, vi que liderás el área técnica en Acme..."
        """
        ...

    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """
        Genera una completion estructurada en formato JSON.

        Similar a complete(), pero fuerza al modelo a responder con
        JSON válido. Útil para extraer datos estructurados como
        clasificaciones, scores, o listas de items.

        Args:
            prompt: El mensaje del usuario. Debe indicar claramente
                la estructura JSON esperada en la respuesta.
            system_prompt: Instrucciones de sistema. Recomendado incluir
                "Responde SOLO con JSON válido" o similar.
            temperature: Control de creatividad (0.0-1.0).
                Para JSON estructurado, valores bajos (0.1-0.3) son mejores.

        Returns:
            Diccionario Python parseado desde el JSON de respuesta.
            Las claves dependen del prompt enviado.

        Raises:
            LLMConnectionError: Si falla la conexión con el proveedor.
            LLMJSONParseError: Si la respuesta no es JSON válido.

        Example:
            >>> result = await llm.complete_json(
            ...     prompt="Clasifica este lead: CTO de startup fintech",
            ...     system_prompt="Responde con {role_type, confidence}",
            ... )
            >>> print(result)
            {"role_type": "decision_maker", "confidence": 0.95}
        """
        ...

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Cuenta el número de tokens en un texto.

        Útil para estimar costos, verificar límites de contexto,
        y optimizar prompts antes de enviarlos al modelo.

        La tokenización depende del modelo específico. Por ejemplo,
        GPT-4 usa tiktoken con encoding cl100k_base.

        Args:
            text: El texto a tokenizar. Puede ser un prompt,
                respuesta, o cualquier string.

        Returns:
            Número de tokens en el texto.

        Example:
            >>> tokens = llm.count_tokens("Hola, ¿cómo estás?")
            >>> print(tokens)
            7
            >>> # Verificar si cabe en el contexto
            >>> if tokens > 4000:
            ...     text = truncate_text(text)
        """
        ...
