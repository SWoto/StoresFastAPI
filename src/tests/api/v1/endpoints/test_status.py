import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_live(async_client: AsyncClient):
    response = await async_client.get("/api/v1/status/live")
    assert response.status_code == 200
