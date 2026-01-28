"""
Configuracion global de pytest.

Los fixtures de integracion (DB, HTTP client) solo se cargan si las
dependencias estan disponibles. Los tests unitarios funcionan sin ellas.
"""

import asyncio
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Fixture para event loop.
    Necesario para tests async con pytest-asyncio.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# FIXTURES DE INTEGRACION (solo si las dependencias estan disponibles)
# ============================================================================

try:
    from typing import AsyncGenerator

    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.db.base_class import Base
    from app.db.session import get_db
    from app.main import app

    # URL de base de datos de test (en memoria o test DB)
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

    @pytest.fixture(scope="function")
    async def engine():
        """Fixture para crear engine de test."""
        engine = create_async_engine(
            TEST_DATABASE_URL,
            echo=False,
            future=True,
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        await engine.dispose()

    @pytest.fixture(scope="function")
    async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
        """Fixture para crear sesion de DB de test."""
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session() as session:
            yield session

    @pytest.fixture(scope="function")
    async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
        """
        Fixture para crear cliente HTTP de test.
        Inyecta DB de test en la app.
        """

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.clear()

except ImportError:
    # Las dependencias de integracion no estan disponibles.
    # Los tests unitarios funcionaran sin problemas.
    pass
