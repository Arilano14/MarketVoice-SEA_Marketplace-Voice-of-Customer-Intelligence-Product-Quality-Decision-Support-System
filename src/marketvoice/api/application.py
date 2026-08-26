"""FastAPI Application Factory.

Phase 11: Operational Automation & Inference Service.
Configures CORS middleware, lifespan events, exception handlers, and API routing.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from marketvoice.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup: Models preloaded in memory
    print("[API] Starting MarketVoice SEA Inference & Decision Service...")
    yield
    # Shutdown: Clean resource disposal
    print("[API] Shutting down MarketVoice SEA Service...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="MarketVoice SEA — Operational Inference & Decision Service",
        description=(
            "Phase 11 Operational Microservice providing NLP aspect intelligence, "
            "rating-based severity proxies, and contextual Decision Support System (DSS) priority scoring."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS configuration for local n8n and dashboard integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Validation Error Handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": "INVALID_PAYLOAD_SCHEMA",
                "error_message": "Request validation failed against Pydantic schema.",
                "details": exc.errors(),
                "retryable": False,
            },
        )

    # Custom General Exception Handler
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "error_message": "An unexpected error occurred during processing.",
                "retryable": True,
            },
        )

    # Include Routes
    app.include_router(router)

    return app


# Application entry point for ASGI servers (uvicorn)
app = create_app()
