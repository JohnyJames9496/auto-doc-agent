import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.auth.security import create_access_token


@pytest.fixture
def auth_token():
    return create_access_token("test-user-id")


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c