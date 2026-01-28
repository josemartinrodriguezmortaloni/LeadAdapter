"""
Configuracion de pytest para tests unitarios.

Este conftest sobreescribe el global para evitar dependencias de FastAPI/DB.
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
