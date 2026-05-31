import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
from backend.app.main import app
from backend.app.db.session import get_db


@pytest.mark.asyncio
async def test_docs_endpoint_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/documentation", json={
        "file_path": "/test/utils.py",
        "function_name": "add",
        "code_snippet": "def add(a, b): return a + b",
        "language": "python",
        "project_id": "test-project",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_docs_endpoint_with_auth(auth_headers: dict):
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with patch("backend.app.api.docs.cache_get", new_callable=AsyncMock) as mock_cache_get:
            with patch("backend.app.api.docs.generate_doc_task") as mock_task:
                mock_cache_get.return_value = None
                mock_task.delay.return_value.id = "fake-task-id"

                from httpx import AsyncClient, ASGITransport
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test",
                ) as client:
                    response = await client.post(
                        "/api/v1/documentation",
                        json={
                            "file_path": "/test/utils.py",
                            "function_name": "add",
                            "code_snippet": "def add(a, b): return a + b",
                            "language": "python",
                            "project_id": "test-project",
                        },
                        headers=auth_headers,
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "queued"
                    assert data["task_id"] == "fake-task-id"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_docs_endpoint_cache_hit(client: AsyncClient, auth_headers: dict):
    cached_doc = "### `add`\n\nAdds two numbers."
    with patch("backend.app.api.docs.cache_get", new_callable=AsyncMock) as mock_cache_get:
        mock_cache_get.return_value = cached_doc

        response = await client.post(
            "/api/v1/documentation",
            json={
                "file_path": "/test/utils.py",
                "function_name": "add",
                "code_snippet": "def add(a, b): return a + b",
                "language": "python",
                "project_id": "test-project",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert data["cached"] is True
        assert data["documentation"] == cached_doc
