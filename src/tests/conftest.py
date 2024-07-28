import pytest
from typing import AsyncGenerator, Generator, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


import os
os.environ["ENV_STATE"] = "test"

from src.core.configs import settings
from src.core.database import engine, create_tables, drop_tables, Session
from src.main import app
from src.tests.api.v1.endpoints.test_users import TestUser
from src.models import UsersModel

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

@pytest.fixture()
async def registered_user(async_client: AsyncClient, request) -> dict:
    data_in = TestUser.user_data.copy()
    if not hasattr(request, "param"):
        role = "none"
    else:
        role = request.param
    data_in['role'] = role
    response = await TestUser.register_user(async_client, data_in)
    return response.json()

@pytest.fixture()
async def confirmed_user(registered_user: dict, session: AsyncSession) -> UsersModel:
    user = await TestUser.confirm_user(TestUser.user_data['email'], session)

    return user

@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: UsersModel) -> str:
    response = await TestUser.login_user(async_client, TestUser.user_data['email'], TestUser.user_data['password'])
    return response.json()["access_token"]