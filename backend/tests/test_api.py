"""Smoke tests for the FastAPI application."""

import pytest
from httpx import ASGITransport
from httpx import AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "CompeteScope API"


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    resp = await client.post(
        "/api/tasks",
        json={"target_product": "Slack", "analysis_dimensions": ["SWOT", "features"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["target_product"] == "Slack"


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert isinstance(data["data"]["items"], list)


@pytest.mark.asyncio
async def test_report_not_found(client: AsyncClient):
    """Querying a non-existent report should return success=false."""
    resp = await client.get("/api/reports/nonexistent-id")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["error"] == "报告不存在"
