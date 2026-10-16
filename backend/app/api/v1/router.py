"""API v1 master router aggregating domain endpoints."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.societies import router as societies_router

api_v1_router = APIRouter()

# Health and diagnostic endpoints
api_v1_router.include_router(health_router, prefix="", tags=["Health"])

# Identity, Authentication & Accounts
api_v1_router.include_router(auth_router, tags=["Authentication & Accounts"])

# Societies, Wings, Units & Memberships
api_v1_router.include_router(societies_router, tags=["Societies & Memberships"])
