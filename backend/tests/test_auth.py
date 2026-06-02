import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    response = await client.post("/auth/register", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"email": "notanemail", "password": "testpassword123"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_credentials(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/documentation",
        json={
            "file_path": "/test/utils.py",
            "function_name": "add",
            "code_snippet": "def add(a, b): return a + b",
            "language": "python",
            "project_id": "test-project",
        },
    )
    assert response.status_code == 401
