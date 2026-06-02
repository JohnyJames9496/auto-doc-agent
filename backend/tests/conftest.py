import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from backend.app.main import app
from backend.app.auth.dependencies import get_current_user
from backend.app.db.session import get_db
from uuid import uuid4

TEST_USER_ID = str(uuid4())


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer autodoc_test_key"}


@pytest.fixture
def mock_db():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def client(mock_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


@pytest.fixture
async def auth_client(mock_db):
    async def mock_auth():
        return TEST_USER_ID

    app.dependency_overrides[get_current_user] = mock_auth

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.pop(get_current_user, None)
