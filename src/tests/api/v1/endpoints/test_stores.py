import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoresModel

class TestStore():
    store_data = {
        "name":"Stanton - Heathcote",
        "description":"i'll reboot the optical xml bandwidth, that should program the css panel!",
        "address":"168 Johnson Plaza",
    }

    @staticmethod
    async def create_store(async_client: AsyncClient, store_data: dict, logged_in_token: str) -> dict:
        return await async_client.post(
            "/api/v1/stores/", json={**store_data}, headers={'Authorization': f'Bearer {logged_in_token}'}
        )
        
    
    @pytest.fixture()
    async def created_store(self, async_client: AsyncClient, logged_in_token: str) -> dict:
        response =  await self.create_store(async_client, self.store_data, logged_in_token)
        return response.json()

    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["admin", "owner"], indirect=True)
    async def test_create_store(self, async_client: AsyncClient, logged_in_token: str):
        response = await self.create_store(async_client, self.store_data, logged_in_token)
        assert response.status_code == 201

        data_src = self.store_data.copy()
        data_src["id"] = response.json()["id"]

        assert response.json().items() <= data_src.items()

    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["none"], indirect=True)
    async def test_create_store_low_permission(self, async_client: AsyncClient, logged_in_token: str):
        response = await self.create_store(async_client, self.store_data, logged_in_token)
        assert response.status_code == 403


    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["admin"], indirect=True)
    async def test_get_store_from_id(self, async_client: AsyncClient, created_store: dict):
        target_id = created_store["id"]
        response = await async_client.get(
            f"/api/v1/stores/{target_id}")
        assert response.status_code == 200

        req_user = self.store_data.copy()
        req_user["id"] = response.json()["id"]

        assert response.json().items() <= req_user.items()


    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["admin"], indirect=True)
    async def test_get_complete_empty_store_from_id(self, async_client: AsyncClient, created_store: dict):
        target_id = created_store["id"]
        response = await async_client.get(
            f"/api/v1/stores/complete/{target_id}")
        assert response.status_code == 200

        req_user = self.store_data.copy()
        req_user["id"] = response.json()["id"]
        req_user["products"] = []

        assert response.json().items() <= req_user.items()