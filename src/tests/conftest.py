import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


import os
os.environ["ENV_STATE"] = "test"

from src.core.configs import settings
from src.core.database import engine, create_tables, drop_tables, Session
from src.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def session() -> AsyncGenerator:
    async with Session() as session:
        await create_tables()
        yield session
        await drop_tables()

    engine.sync_engine.dispose()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac
