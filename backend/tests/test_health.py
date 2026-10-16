"""Unit and integration tests for service health and diagnostics."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test that the root endpoint returns service info."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Socievo"
    assert data["status"] == "operational"
    assert "version" in data
    assert "documentation" in data


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Test that the liveness probe returns healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "Socievo"
    assert data["status"] == "healthy"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_readiness_check_endpoint(client: AsyncClient):
    """Test that the readiness probe verifies database and returns 200."""
    response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert len(data["dependencies"]) >= 1
    
    db_dep = next((d for d in data["dependencies"] if d["name"] == "database"), None)
    assert db_dep is not None
    assert db_dep["status"] == "healthy"
    assert db_dep["latency_ms"] is not None


@pytest.mark.asyncio
async def test_request_id_header(client: AsyncClient):
    """Verify that every response includes X-Request-ID and X-Response-Time headers."""
    response = await client.get("/")
    assert "x-request-id" in response.headers
    assert "x-response-time" in response.headers
