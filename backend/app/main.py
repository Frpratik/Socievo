"""Main FastAPI application entrypoint for Socievo."""

import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app import __version__
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    SocievoException,
    generic_exception_handler,
    socievo_exception_handler,
    validation_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.core.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown."""
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{__version__} [Env: {settings.APP_ENV}]")
    
    # Initialize Redis connection pool
    await init_redis()

    yield

    # Clean up connections on shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise group-buying and local home-services marketplace for residential housing societies.",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
origins = (
    settings.CORS_ORIGINS
    if isinstance(settings.CORS_ORIGINS, list)
    else [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and Request Logging Middleware
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

    # Only log standard API calls, suppress excessive log spam
    if not request.url.path.endswith("/health"):
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.2f}ms)",
            extra={"request_id": request_id},
        )

    return response


# Register Exception Handlers
app.add_exception_handler(SocievoException, socievo_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API v1 Router
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint providing service identity and documentation links."""
    return {
        "service": settings.APP_NAME,
        "version": __version__,
        "documentation": "/api/docs",
        "api_v1": "/api/v1",
        "status": "operational",
    }
