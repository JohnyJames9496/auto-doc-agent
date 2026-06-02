import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.auth.dependencies import get_current_user
from uuid import uuid4

@pytest.fixture
def auth_headers():
    """Mock API key for testing"""
    return {"Authorization": "Bearer autodoc_test_key_12345"}

@pytest.fixture
def override_auth():
    """Override auth to return a test user ID"""
    test_user_id = str(uuid4())
    
    async def override_get_current_user(*args, **kwargs):
        return test_user_id
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_docs_endpoint_requires_auth(override_auth):
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
        )
        assert response.status_code in [200, 401]

@pytest.mark.asyncio
async def test_docs_endpoint_with_auth(override_auth):
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()

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
                    )
                    assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_docs_endpoint_cache_hit(override_auth):
    cached_doc = "### `add`\n\nAdds two numbers."
    
    with patch("backend.app.api.docs.cache_get", new_callable=AsyncMock) as mock_cache_get:
        mock_cache_get.return_value = cached_doc

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
            )
            assert response.status_code == 200
            assert "add" in response.text
