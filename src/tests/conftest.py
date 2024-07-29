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
from src.tests.api.base_products import BaseProduct
from src.tests.api.base_stores import BaseStore
from src.tests.api.base_users import BaseUser
from src.models import UsersModel

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def session() -> AsyncGenerator:
    async with Session() as session:
        await create_tables()
        yield session
        await drop_tables()

    engine.sync_engine.dispose()


@pytest.fixture
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac

@pytest.fixture
async def registered_user(async_client: AsyncClient, request) -> dict:
    data_in = BaseUser.data.copy()
    if not hasattr(request, "param"):
        role = "none"
    else:
        role = request.param
    data_in['role'] = role
    response = await BaseUser.register_user(async_client, data_in)
    return response.json()

@pytest.fixture
async def confirmed_user(registered_user: dict, session: AsyncSession) -> UsersModel:
    user = await BaseUser.confirm_user(BaseUser.data['email'], session)

    return user

@pytest.fixture
async def logged_in_token(async_client: AsyncClient, confirmed_user: UsersModel) -> str:
    response = await BaseUser.login_user(async_client, BaseUser.data['email'], BaseUser.data['password'])
    return response.json()["access_token"]

@pytest.fixture
async def created_store(async_client: AsyncClient, logged_in_token: str) -> dict:
    response =  await BaseStore.create_store(async_client, BaseStore.data, logged_in_token)
    return response.json()

@pytest.fixture
async def created_product(async_client: AsyncClient, created_store: str) -> dict:
    data_in = BaseProduct.data.copy()
    data_in["store_id"] = created_store["id"]
    response =  await BaseProduct.create_product(async_client, data_in)
    return response.json()

@pytest.fixture
async def created_store_with_product(async_client: AsyncClient, created_store: str) -> dict:
    data_in = BaseProduct.data.copy()
    data_in["store_id"] = created_store["id"]
    _ = await BaseProduct.create_product(async_client, data_in)
    return created_store