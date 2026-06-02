import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.auth.dependencies import get_current_user
from uuid import uuid4


@pytest.mark.asyncio
async def test_docs_endpoint_requires_auth():
    """Test that docs endpoint requires authentication"""
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
                "project_id": str(uuid4()),
            },
        )
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_docs_endpoint_with_auth():
    """Test docs endpoint with valid auth"""
    test_user_id = str(uuid4())
    test_project_id = str(uuid4())

    async def override_get_current_user(*args, **kwargs):
        return test_user_id

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    try:
        with patch("backend.app.api.docs.cache_get", new_callable=AsyncMock) as mock_cache:
            with patch("backend.app.api.docs.generate_doc_task") as mock_task:
                mock_cache.return_value = None
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
                            "project_id": test_project_id,
                        },
                        headers={"Authorization": "Bearer test-key"},
                    )
                    assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_docs_endpoint_cache_hit():
    """Test cache hit for docs"""
    test_user_id = str(uuid4())
    test_project_id = str(uuid4())

    async def override_get_current_user(*args, **kwargs):
        return test_user_id

    mock_session = AsyncMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    try:
        cached_doc = "### `add`\n\nAdds two numbers."
        with patch("backend.app.api.docs.cache_get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = cached_doc

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
                        "project_id": test_project_id,
                    },
                    headers={"Authorization": "Bearer test-key"},
                )
                assert response.status_code == 200
                assert "add" in response.text
    finally:
        app.dependency_overrides.clear()
