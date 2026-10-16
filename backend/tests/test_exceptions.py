"""Tests for uniform exception handling and HTTP status mappings."""

import pytest
from httpx import AsyncClient
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.main import app


@app.get("/test-not-found-endpoint")
async def trigger_not_found():
    raise NotFoundError("Deal", "test-deal-uuid-123")


@app.get("/test-permission-endpoint")
async def trigger_permission():
    raise PermissionDeniedError("Custom access prohibited.")


@pytest.mark.asyncio
async def test_not_found_exception_handling(client: AsyncClient):
    """Verify that NotFoundError formats with standard JSON error response."""
    response = await client.get("/test-not-found-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "RESOURCE_NOT_FOUND"
    assert "test-deal-uuid-123" in data["message"]
    assert data["details"]["resource"] == "Deal"
    assert "request_id" in data


@pytest.mark.asyncio
async def test_permission_denied_exception_handling(client: AsyncClient):
    """Verify that PermissionDeniedError returns 403."""
    response = await client.get("/test-permission-endpoint")
    assert response.status_code == 403
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "PERMISSION_DENIED"
    assert data["message"] == "Custom access prohibited."
