"""
Puerto de aplicación para operaciones de cache.

Este módulo define la interfaz abstracta (Port) que cualquier
adaptador de cache debe implementar. Sigue el patrón Ports & Adapters
de Arquitectura Hexagonal.

Example:
    >>> # En infrastructure/adapters/redis_adapter.py
    >>> class RedisAdapter(CachePort):
    ...     async def get(self, key: str) -> Any | None:
    ...         return await self.redis.get(key)
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class CachePort(ABC):
    """
    Interfaz abstracta para operaciones de cache.

    Define el contrato que cualquier adaptador de cache (Redis, Memcached,
    in-memory, mock) debe implementar. El Application Layer depende de esta
    interfaz, no de implementaciones concretas.

    Casos de uso típicos:
        - Cachear mensajes generados para evitar regeneración
        - Almacenar resultados de inferencia de seniority
        - Rate limiting por lead/sender

    Implementaciones esperadas:
        - RedisAdapter: Cache distribuido con Redis
        - MemoryCacheAdapter: Cache en memoria (desarrollo)
        - MockCacheAdapter: Para testing

    Example:
        >>> class MemoryCache(CachePort):
        ...     def __init__(self):
        ...         self._store = {}
        ...     async def get(self, key: str) -> Any | None:
        ...         return self._store.get(key)
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        Obtiene un valor del cache por su clave.

        Args:
            key: Clave única del valor a recuperar.
                Convención: usar formato "prefix:entity:id"
                Ejemplo: "message:lead_123:v1"

        Returns:
            El valor cacheado si existe y no expiró, None en caso contrario.
            El tipo depende de lo que se almacenó originalmente.

        Example:
            >>> cached = await cache.get("seniority:cto_acme")
            >>> if cached:
            ...     return cached  # Evita recalcular
            >>> # Cache miss, calcular y guardar
            >>> result = inferrer.infer(job_title)
            >>> await cache.set("seniority:cto_acme", result)
        """
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """
        Almacena un valor en el cache con tiempo de expiración.

        Args:
            key: Clave única para identificar el valor.
                Debe ser descriptiva y seguir convención de namespacing.
            value: Valor a almacenar. Debe ser serializable.
                Tipos comunes: str, dict, dataclass (como dict).
            ttl_seconds: Tiempo de vida en segundos antes de expirar.
                - 3600 (1 hora): Default, bueno para datos semi-estáticos
                - 300 (5 min): Para datos que cambian frecuentemente
                - 86400 (24 hrs): Para datos muy estables

        Returns:
            None. La operación es fire-and-forget.

        Raises:
            CacheConnectionError: Si falla la conexión con el backend.
            CacheSerializationError: Si el valor no es serializable.

        Example:
            >>> # Cachear un mensaje generado por 1 hora
            >>> await cache.set(
            ...     key=f"message:{lead.id}:{channel}",
            ...     value={"content": message, "score": 7.5},
            ...     ttl_seconds=3600,
            ... )
        """
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Elimina un valor del cache.

        Útil para invalidar cache cuando los datos subyacentes cambian.
        No lanza error si la clave no existe (operación idempotente).

        Args:
            key: Clave del valor a eliminar.

        Returns:
            None. No indica si la clave existía o no.

        Example:
            >>> # Invalidar cache cuando se actualiza el playbook
            >>> await cache.delete(f"icp_match:{lead.id}")
            >>> await cache.delete(f"strategy:{lead.id}")
        """
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el cache.

        Más eficiente que get() cuando solo necesitás saber si existe,
        sin recuperar el valor completo.

        Args:
            key: Clave a verificar.

        Returns:
            True si la clave existe y no ha expirado, False en caso contrario.

        Example:
            >>> # Check rápido antes de operación costosa
            >>> if await cache.exists(f"message:{lead.id}"):
            ...     return await cache.get(f"message:{lead.id}")
            >>> # No existe, generar mensaje
            >>> message = await generate_message(lead)
        """
        ...

    async def get_or_set(
        self,
        key: str,
        factory: "Callable[[], Awaitable[Any]]",
        ttl_seconds: int = 3600,
    ) -> Any:
        """
        Obtiene del cache o ejecuta factory y cachea el resultado.

        Implementa el patrón cache-aside de forma atómica.
        Útil para evitar el boilerplate de check-get-set.

        Args:
            key: Clave de cache.
            factory: Función async que produce el valor si no está cacheado.
            ttl_seconds: TTL para el valor si se genera.

        Returns:
            Valor cacheado o generado por factory.

        Example:
            >>> async def generate():
            ...     return await expensive_llm_call()
            >>> result = await cache.get_or_set("msg:123", generate, ttl=3600)
        """
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        await self.set(key, value, ttl_seconds)
        return value
