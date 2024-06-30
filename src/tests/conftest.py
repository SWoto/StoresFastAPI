from src.main import app
from src.core.database import engine, create_tables, drop_tables, Session
from src.core.configs import settings
import os
import pytest
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

os.environ["ENV_STATE"] = "test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def get_session() -> AsyncGenerator:
    async with Session() as session:
        await create_tables()
        yield session
        await drop_tables()

    engine.sync_engine.dispose()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac
