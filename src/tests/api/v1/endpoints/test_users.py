import pytest
from httpx import AsyncClient
from random import randint
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks

from src.tests.api.base_users import BaseUser


class TestUser(BaseUser):
    @pytest.mark.anyio
    async def test_register_user(self, async_client: AsyncClient):
        response = await self.register_user(async_client, self.data)
        assert response.status_code == 201

        base_data = self.data.copy()

        base_data["id"] = response.json()["id"]
        base_data.pop("password")

        assert response.json().items() <= base_data.items()

    @pytest.mark.anyio
    async def test_register_user_already_exists_email(self, async_client: AsyncClient, registered_user: dict):
        temp_data = self.data.copy()
        temp_data['document'] = str(randint(1000, 100000000))
        response = await self.register_user(async_client, temp_data)

        assert response.status_code == 409
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_register_user_already_exists_doc(self, async_client: AsyncClient, registered_user: dict):
        temp_data = self.data.copy()
        temp_data['email'] = str(randint(1, 999))+temp_data['email']
        response = await self.register_user(async_client, temp_data)

        assert response.status_code == 409
        assert "Document already registered" in response.json()["detail"]

    # NOTE: Do not use confirmed_user method here, this is for real testing. Method confirmed_user uses direct access to db to speed it up
    @pytest.mark.anyio
    async def test_confirm_user(self, async_client: AsyncClient, mocker):
        spy = mocker.spy(BackgroundTasks, "add_task")
        await self.register_user(async_client, self.data)

        confirmation_url = str(spy.call_args[1]["confirmation_url"])
        response = await async_client.get(confirmation_url)

        assert response.status_code == 202

    @pytest.mark.anyio
    async def test_login_user(self, async_client: AsyncClient, confirmed_user: dict):
        response = await self.login_user(async_client, self.data['email'], self.data['password'])
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_login_user_not_confirmed(self, async_client: AsyncClient, registered_user: dict):
        response = await self.login_user(async_client, self.data['email'], self.data['password'])
        assert "E-mail pending confirmation" in response.json()["detail"]
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_login_user_invalid_username(self, async_client: AsyncClient):
        username = ""
        password = "123456"
        response = await self.login_user(async_client, username, password)
        assert response.status_code == 422

        username = None
        response = await self.login_user(async_client, username, password)
        assert response.status_code == 422

        username = "lalaland"
        response = await self.login_user(async_client, username, password)
        assert response.status_code == 422

        username = str(randint(1, 999))+self.data['email']
        response = await self.login_user(async_client, username, self.data['password'])
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_login_user_invalid_password(self, async_client: AsyncClient, confirmed_user: dict):
        password = None
        response = await self.login_user(async_client, self.data['email'], password)
        assert response.status_code == 422

        password = ""
        response = await self.login_user(async_client, self.data['email'], password)
        assert response.status_code == 422

        password = str(randint(1, 100000000))
        response = await self.login_user(async_client, self.data['email'], password)
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_get_user_from_token(self, async_client: AsyncClient, logged_in_token: str):
        response = await async_client.get(
            "/api/v1/users/", headers={'Authorization': f'Bearer {logged_in_token}'})

        assert response.status_code == 200

        base_data = self.data.copy()

        base_data["id"] = response.json()["id"]
        base_data["confirmed"] = response.json()["confirmed"]
        base_data.pop("password")

        assert response.json().items() <= base_data.items()

    @pytest.mark.anyio
    async def test_get_user_from_random_token(self, async_client: AsyncClient, logged_in_token: str):
        random_jwt = jwt.encode(
            {'some': 'not so random payload'}, 'my deepest secret', algorithm='HS256')
        response = await async_client.get(
            "/api/v1/users/", headers={'Authorization': f'Bearer {random_jwt}'})

        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_get_from_id(self, async_client: AsyncClient, registered_user: dict, session: AsyncSession):
        id_to_be_requested = registered_user['id']

        admin_user = self.data.copy()
        admin_user['role'] = "admin"
        admin_user['email'] = str(randint(1, 999))+admin_user['email']
        admin_user['document'] = str(randint(1, 100000000))
        register_response = await self.register_user(async_client, admin_user)
        assert register_response.status_code == 201

        _ = await self.confirm_user(admin_user['email'], session)

        login_response = await self.login_user(async_client, admin_user['email'], admin_user['password'])
        assert login_response.status_code == 200

        jwt_token = login_response.json()["access_token"]
        response = await async_client.get(
            f"/api/v1/users/{id_to_be_requested}", headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200

        base_data = self.data.copy()
        base_data["id"] = response.json()["id"]
        base_data.pop("password")

        assert response.json().items() <= base_data.items()

    @pytest.mark.anyio
    async def test_get_from_id_not_admin(self, async_client: AsyncClient, confirmed_user: dict):
        id_to_be_requested = confirmed_user.id

        response = await self.login_user(async_client, self.data['email'],  self.data['password'])
        assert response.status_code == 200

        jwt_token = response.json()["access_token"]
        response = await async_client.get(
            f"/api/v1/users/{id_to_be_requested}", headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_get_from_id_wrong_id(self, async_client: AsyncClient, registered_user: dict, session: AsyncSession):
        admin_user = self.data.copy()
        admin_user['role'] = "admin"
        admin_user['email'] = str(randint(1, 999))+admin_user['email']
        admin_user['document'] = str(randint(1, 100000000))
        response = await self.register_user(async_client, admin_user)
        assert response.status_code == 201

        _ = await self.confirm_user(admin_user['email'], session)

        response = await self.login_user(async_client, admin_user['email'], admin_user['password'])
        assert response.status_code == 200

        jwt_token = response.json()["access_token"]
        response = await async_client.get(
            "/api/v1/users/1", headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404
