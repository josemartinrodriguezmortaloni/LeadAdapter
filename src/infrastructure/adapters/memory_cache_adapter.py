import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from application.ports.cache_port import CachePort


@dataclass()
class CacheEntry:
    value: Any
    expires_at: datetime


class MemoryCacheAdapter(CachePort):
    def __init__(self) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if datetime.utcnow() > entry.expires_at:
                del self._cache[key]
                return None
            return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 3600,
    ) -> None:
        """Guarda valor en cache."""
        async with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    async def delete(self, key: str) -> None:
        """Elimina valor del cache."""
        async with self._lock:
            self._cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Verifica si existe una clave."""
        value = await self.get(key)
        return value is not None

    async def clear(self) -> None:
        """Limpia todo el cache (útil para tests)."""
        async with self._lock:
            self._cache.clear()
