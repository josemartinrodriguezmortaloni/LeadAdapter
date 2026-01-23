"""
API layer for LeadAdapter.

This package contains the FastAPI application components including:
- routers: HTTP endpoint definitions
- dependencies: Dependency injection container
- middleware: Cross-cutting concerns (error handling, logging)

The API layer is responsible for HTTP concerns only and delegates
all business logic to the application layer use cases.
"""
