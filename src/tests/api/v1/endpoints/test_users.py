import pytest
from httpx import AsyncClient
from random import randint
from jose import jwt
from uuid import uuid4, SafeUUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks


from src.models import UsersModel


class TestUser():
    user_data = {'email': 'test1@example.net', "first_name": "Alison",
                 "sur_name": "Brown", "document": "12345678901", "password": "ito2i23f#$@%@#Vcsa13", "role": "none", "confirmed": False}

    @staticmethod
    async def register_user(async_client: AsyncClient, user_data: dict) -> dict:
        return await async_client.post(
            "/api/v1/users/signup", json={**user_data}
        )

    @staticmethod
    async def login_user(async_client: AsyncClient, email: str, password: str) -> dict:
        return await async_client.post(
            "/api/v1/users/login", data={'username': email, 'password': password})
    
    @staticmethod
    async def confirm_user(email, session: AsyncSession) -> dict:
        user = await UsersModel.find_by_email(email, session)
        user.confirmed = True
        await session.commit()

        return user

    @pytest.fixture(autouse=True)
    def reset_state(self) -> None:
        self.user_data["confirmed"] = False
    

    @pytest.fixture()
    async def registered_user(self, async_client: AsyncClient) -> dict:
        response = await self.register_user(async_client, self.user_data)
        return response.json()

    @pytest.fixture()
    async def confirmed_user(self, registered_user: dict, session: AsyncSession) -> dict:
        user = await self.confirm_user(self.user_data['email'], session)
        self.user_data['confirmed'] = True
 
        return user

    @pytest.fixture()
    async def logged_in_token(self, async_client: AsyncClient, confirmed_user: UsersModel):
        response = await self.login_user(async_client, self.user_data['email'], self.user_data['password'])
        return response.json()["access_token"]

    @pytest.mark.anyio
    async def test_register_user(self, async_client: AsyncClient):
        response = await self.register_user(async_client, self.user_data)
        assert response.status_code == 201

        data_src = self.user_data.copy()

        data_src["id"] = response.json()["id"]
        data_src.pop("password")

        assert response.json().items() <= data_src.items()

    @pytest.mark.anyio
    async def test_register_user_already_exists_email(self, async_client: AsyncClient, registered_user: dict):
        temp_data = self.user_data.copy()
        temp_data['document'] = str(randint(1000, 100000000))
        response = await self.register_user(async_client, temp_data)

        assert response.status_code == 409
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_register_user_already_exists_doc(self, async_client: AsyncClient, registered_user: dict):
        temp_data = self.user_data.copy()
        temp_data['email'] = str(randint(1, 999))+temp_data['email']
        response = await self.register_user(async_client, temp_data)

        assert response.status_code == 409
        assert "Document already registered" in response.json()["detail"]

    # NOTE: Do not use confirmed_user method here, this is for real testing. Method confirmed_user uses direct access to db to speed it up
    @pytest.mark.anyio
    async def test_confirm_user(self, async_client: AsyncClient, mocker):
        spy = mocker.spy(BackgroundTasks, "add_task")
        await self.register_user(async_client, self.user_data)

        confirmation_url = str(spy.call_args[1]["confirmation_url"])
        response = await async_client.get(confirmation_url)

        assert response.status_code == 202

    @pytest.mark.anyio
    async def test_login_user(self, async_client: AsyncClient, confirmed_user: dict):
        response = await self.login_user(async_client, self.user_data['email'], self.user_data['password'])
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_login_user_not_confirmed(self, async_client: AsyncClient, registered_user: dict):
        response = await self.login_user(async_client, self.user_data['email'], self.user_data['password'])
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

        username = str(randint(1, 999))+self.user_data['email']
        response = await self.login_user(async_client, username, self.user_data['password'])
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_login_user_invalid_password(self, async_client: AsyncClient, confirmed_user: dict):
        password = None
        response = await self.login_user(async_client, self.user_data['email'], password)
        assert response.status_code == 422

        password = ""
        response = await self.login_user(async_client, self.user_data['email'], password)
        assert response.status_code == 422

        password = str(randint(1, 100000000))
        response = await self.login_user(async_client, self.user_data['email'], password)
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_get_user_from_token(self, async_client: AsyncClient, logged_in_token: str):
        response = await async_client.get(
            "/api/v1/users/", headers={'Authorization': f'Bearer {logged_in_token}'})

        assert response.status_code == 200

        data_src = self.user_data.copy()

        data_src["id"] = response.json()["id"]
        data_src.pop("password")

        assert response.json().items() <= data_src.items()

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

        admin_user = self.user_data.copy()
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

        req_user = self.user_data.copy()
        req_user["id"] = response.json()["id"]
        req_user.pop("password")

        assert response.json().items() <= req_user.items()

    @pytest.mark.anyio
    async def test_get_from_id_not_admin(self, async_client: AsyncClient, confirmed_user: dict):
        id_to_be_requested = confirmed_user.id

        response = await self.login_user(async_client, self.user_data['email'],  self.user_data['password'])
        assert response.status_code == 200

        jwt_token = response.json()["access_token"]
        response = await async_client.get(
            f"/api/v1/users/{id_to_be_requested}", headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_get_from_id_wrong_id(self, async_client: AsyncClient, registered_user: dict, session: AsyncSession):
        admin_user = self.user_data.copy()
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
