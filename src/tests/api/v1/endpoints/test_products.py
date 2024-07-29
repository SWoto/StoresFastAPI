import pytest
from httpx import AsyncClient

from src.tests.api.base_products import BaseProduct
from src.tests.api.base_stores import BaseStore


@pytest.mark.parametrize('registered_user', ["admin"], indirect=True)
class TestProduct(BaseProduct):
    @pytest.mark.anyio
    async def test_create_product(self, async_client: AsyncClient, created_store: str):
        base_data = TestProduct.data.copy()
        base_data["store_id"] = created_store["id"]

        response = await self.create_product(async_client, base_data)
        assert response.status_code == 201

        base_data["id"] = response.json()["id"]

        assert response.json().items() <= base_data.items()

    @pytest.mark.anyio
    async def test_get_product_from_id(self, async_client: AsyncClient, created_product: str):
        target_id = created_product["id"]
        response = await async_client.get(
            f"/api/v1/products/{target_id}")
        assert response.status_code == 200

        base_data = self.data.copy()
        base_data["id"] = response.json()["id"]
        base_data["store_id"] = response.json()["store_id"]

        assert response.json().items() <= base_data.items()

    @pytest.mark.anyio
    async def test_get_product_from_id_complete(self, async_client: AsyncClient, created_product: str):
        target_id = created_product["id"]
        response = await async_client.get(
            f"/api/v1/products/complete/{target_id}")
        assert response.status_code == 200

        base_data = self.data.copy()
        base_data["id"] = target_id
        base_data["store"] = BaseStore.data
        base_data["store"]['id'] = response.json()["store"]['id']

        assert response.json().items() <= base_data.items()

    