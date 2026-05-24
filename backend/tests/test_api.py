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
        json={"target_product": "Slack", "analysis_dimensions": {"pricing": True}},
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
    assert len(data["data"]["items"]) >= 1


@pytest.mark.asyncio
async def test_get_report(client: AsyncClient):
    resp = await client.get("/api/reports/r1p2o3r4t5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["task_target_product"] == "Notion"
