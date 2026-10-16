"""Health and readiness monitoring endpoints."""

import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app import __version__
from app.core.config import settings
from app.core.redis import get_redis
from app.db.session import get_async_session
from app.schemas.common import (
    HealthStatus,
    ReadinessStatus,
    ServiceDependencyStatus,
)

router = APIRouter(prefix="", tags=["Health & Diagnostics"])


@router.get("/health", response_model=HealthStatus, summary="Liveness Probe")
async def health_check() -> HealthStatus:
    """Returns basic service liveness status."""
    return HealthStatus(
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version=__version__,
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ready", response_model=ReadinessStatus, summary="Readiness Probe")
async def readiness_check(
    db: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """Verifies operational readiness of database and cache dependencies."""
    dependencies = []
    is_ready = True

    # 1. Check Database
    db_start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        db_latency = (time.perf_counter() - db_start) * 1000
        dependencies.append(
            ServiceDependencyStatus(
                name="database",
                status="healthy",
                latency_ms=round(db_latency, 2),
                details="PostgreSQL / Database connection active",
            )
        )
    except Exception as e:
        is_ready = False
        dependencies.append(
            ServiceDependencyStatus(
                name="database",
                status="unhealthy",
                details=f"Database check failed: {str(e)}",
            )
        )

    # 2. Check Redis
    redis_instance = await get_redis()
    if redis_instance:
        redis_start = time.perf_counter()
        try:
            await redis_instance.ping()
            redis_latency = (time.perf_counter() - redis_start) * 1000
            dependencies.append(
                ServiceDependencyStatus(
                    name="redis",
                    status="healthy",
                    latency_ms=round(redis_latency, 2),
                    details="Redis cache connection active",
                )
            )
        except Exception as e:
            dependencies.append(
                ServiceDependencyStatus(
                    name="redis",
                    status="degraded",
                    details=f"Redis ping failed: {str(e)}",
                )
            )
    else:
        dependencies.append(
            ServiceDependencyStatus(
                name="redis",
                status="degraded",
                details="Redis client not initialized (running in local fallback mode)",
            )
        )

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    response_body = ReadinessStatus(
        status="ready" if is_ready else "not_ready",
        dependencies=dependencies,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return JSONResponse(status_code=status_code, content=response_body.model_dump())
