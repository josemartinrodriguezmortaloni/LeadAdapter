"""
Middleware components for cross-cutting concerns.

This package contains middleware that applies to all requests:
- Error handling: Transforms exceptions to RFC 7807 Problem Details
- Future: Request logging, tracing, rate limiting, etc.

Middleware is registered during application startup in main.py.
"""
