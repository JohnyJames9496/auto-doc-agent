import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4


@pytest.mark.asyncio
async def test_docs_endpoint_requires_auth():
    from httpx import AsyncClient, ASGITransport
    from backend.app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        response = await c.post(
            "/api/v1/documentation",
            json={
                "file_path": "/test/utils.py",
                "function_name": "add",
                "code_snippet": "def add(a, b): return a + b",
                "language": "python",
                "project_id": str(uuid4()),
            },
        )
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_docs_endpoint_with_auth(auth_client):
    with patch("backend.app.api.docs.cache_get", new_callable=AsyncMock) as mock_cache:
        with patch("backend.app.api.docs.generate_doc_task") as mock_task:
            mock_cache.return_value = None
            mock_task.delay.return_value.id = "fake-task-id"

            response = await auth_client.post(
                "/api/v1/documentation",
                json={
                    "file_path": "/test/utils.py",
                    "function_name": "add",
                    "code_snippet": "def add(a, b): return a + b",
                    "language": "python",
                    "project_id": str(uuid4()),
                },
            )
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_docs_endpoint_cache_hit(auth_client):
    with patch("backend.app.api.docs.cache_get", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = "### `add`\n\nAdds two numbers."

        response = await auth_client.post(
            "/api/v1/documentation",
            json={
                "file_path": "/test/utils.py",
                "function_name": "add",
                "code_snippet": "def add(a, b): return a + b",
                "language": "python",
                "project_id": str(uuid4()),
            },
        )
        assert response.status_code == 200
        assert "add" in response.text
