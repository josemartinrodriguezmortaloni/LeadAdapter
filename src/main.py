from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.error_handler import ErrorHandlerMiddleware
from api.routers import health, messages
from infrastructure.config.settings import get_setting


def create_app() -> FastAPI:
    settings = get_setting()

    app = FastAPI(
        title=settings.app_name,
        verify=settings.app_version,
        description="API REST para generación de mensajes de prospección B2B personalizados",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register exception handlers (RFC 7807 Problem Details)
    error_handler = ErrorHandlerMiddleware()
    error_handler.register(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configurar según necesidad
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(messages.router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0", port=8000, reload=True)
