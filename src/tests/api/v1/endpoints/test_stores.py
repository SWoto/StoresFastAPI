import pytest
from httpx import AsyncClient

from src.tests.api.base_stores import BaseStore
from src.tests.api.base_products import BaseProduct

class TestStore(BaseStore):
    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["admin", "owner"], indirect=True)
    async def test_create_store(self, async_client: AsyncClient, logged_in_token: str):
        response = await self.create_store(async_client, self.data, logged_in_token)
        assert response.status_code == 201

        data_src = self.data.copy()
        data_src["id"] = response.json()["id"]

        assert response.json().items() <= data_src.items()

    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["none"], indirect=True)
    async def test_create_store_low_permission(self, async_client: AsyncClient, logged_in_token: str):
        response = await self.create_store(async_client, self.data, logged_in_token)
        assert response.status_code == 403


    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["admin"], indirect=True)
    async def test_get_store_from_id(self, async_client: AsyncClient, created_store: dict):
        target_id = created_store["id"]
        response = await async_client.get(
            f"/api/v1/stores/{target_id}")
        assert response.status_code == 200

        base_data = self.data.copy()
        base_data["id"] = response.json()["id"]

        assert response.json().items() <= base_data.items()


    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["admin"], indirect=True)
    async def test_get_store_from_id_complete_empty(self, async_client: AsyncClient, created_store: dict):
        target_id = created_store["id"]
        response = await async_client.get(
            f"/api/v1/stores/complete/{target_id}")
        assert response.status_code == 200

        base_data = self.data.copy()
        base_data["id"] = response.json()["id"]
        base_data["products"] = []

        assert response.json().items() <= base_data.items()

    @pytest.mark.anyio
    @pytest.mark.parametrize('registered_user', ["admin"], indirect=True)
    async def test_get_store_from_id_complete_with_product(self, async_client: AsyncClient, created_store_with_product: dict):
        target_id = created_store_with_product["id"]
        response = await async_client.get(
            f"/api/v1/stores/complete/{target_id}")
        assert response.status_code == 200

        base_data = self.data.copy()
        base_data["id"] = response.json()["id"]
        base_data["products"] = [BaseProduct.data]
        base_data["products"][0]['id'] = response.json()['products'][0]['id']
        base_data["products"][0].pop('store_id')

        assert response.json().items() <= base_data.items()