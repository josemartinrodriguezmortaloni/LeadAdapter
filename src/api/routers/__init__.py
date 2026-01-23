"""
API route definitions for LeadAdapter.

This package contains all HTTP endpoint definitions organized by domain:
- health: Service health and readiness checks
- messages: Message generation endpoints

Each router module defines endpoints for a specific domain area and
delegates business logic to application layer use cases.

Example:
    >>> from fastapi import FastAPI
    >>> from api.routers import health, messages
    >>>
    >>> app = FastAPI()
    >>> app.include_router(health.router)
    >>> app.include_router(messages.router)
"""
