import pytest
from httpx import AsyncClient
from random import randint
from jose import jwt
from uuid import uuid4, SafeUUID


class TestUser():
    user_data = {'email': 'test1@example.net', "first_name": "Alison",
                 "sur_name": "Brown", "document": "12345678901", "password": "ito2i23f#$@%@#Vcsa13", "admin": False}

    @staticmethod
    async def register_user(async_client: AsyncClient, user_data: dict) -> dict:
        return await async_client.post(
            "/api/v1/users/signup", json={**user_data}
        )

    @staticmethod
    async def login_user(async_client: AsyncClient, email: str, password: str) -> dict:
        return await async_client.post(
            "/api/v1/users/login", data={'username': email, 'password': password})

    @pytest.fixture()
    async def registered_user(self, async_client: AsyncClient) -> dict:
        response = await self.register_user(async_client, self.user_data)
        return response.json()

    @pytest.fixture()
    async def logged_in_token(self, async_client: AsyncClient, registered_user: dict):
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

    @pytest.mark.anyio
    async def test_login_user(self, async_client: AsyncClient, registered_user: dict):
        response = await self.login_user(async_client, self.user_data['email'], self.user_data['password'])
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_login_user_wrong_password(self, async_client: AsyncClient, registered_user: dict):
        response = await self.login_user(async_client, self.user_data['email'], str(randint(1, 100000000)))
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_login_user_random_username(self, async_client: AsyncClient, registered_user: dict):
        temp_data = self.user_data.copy()
        temp_data['email'] = str(randint(1, 999))+temp_data['email']
        response = await self.login_user(async_client, temp_data['email'], self.user_data['password'])
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
    async def test_get_from_id(self, async_client: AsyncClient, registered_user: dict):
        id_to_be_requested = registered_user['id']

        admin_user = self.user_data.copy()
        admin_user['admin'] = True
        admin_user['email'] = str(randint(1, 999))+admin_user['email']
        admin_user['document'] = str(randint(1, 100000000))
        response = await self.register_user(async_client, admin_user)
        assert response.status_code == 201

        response = await self.login_user(async_client, admin_user['email'], admin_user['password'])
        assert response.status_code == 200

        jwt_token = response.json()["access_token"]
        response = await async_client.get(
            f"/api/v1/users/{id_to_be_requested}", headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200

        req_user = self.user_data.copy()
        req_user["id"] = response.json()["id"]
        req_user.pop("password")

        assert response.json().items() <= req_user.items()

    @pytest.mark.anyio
    async def test_get_from_id_not_admin(self, async_client: AsyncClient, registered_user: dict):
        id_to_be_requested = registered_user['id']

        response = await self.login_user(async_client, self.user_data['email'],  self.user_data['password'])
        assert response.status_code == 200

        jwt_token = response.json()["access_token"]
        response = await async_client.get(
            f"/api/v1/users/{id_to_be_requested}", headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_get_from_id_wrong_id(self, async_client: AsyncClient, registered_user: dict):
        admin_user = self.user_data.copy()
        admin_user['admin'] = True
        admin_user['email'] = str(randint(1, 999))+admin_user['email']
        admin_user['document'] = str(randint(1, 100000000))
        response = await self.register_user(async_client, admin_user)
        assert response.status_code == 201

        response = await self.login_user(async_client, admin_user['email'], admin_user['password'])
        assert response.status_code == 200

        jwt_token = response.json()["access_token"]
        response = await async_client.get(
            "/api/v1/users/1", headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404
