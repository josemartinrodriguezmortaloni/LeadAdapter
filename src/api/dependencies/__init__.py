"""
Dependency injection container for FastAPI.

This package provides factory functions that wire up the application's
dependency graph, following the Composition Root pattern. All object
creation and assembly happens here, keeping the rest of the code
focused on its single responsibility.

Example:
    >>> from api.dependencies.container import get_generate_message_use_case
    >>> use_case = get_generate_message_use_case()
"""
