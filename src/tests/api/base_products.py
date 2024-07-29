import pytest
from httpx import AsyncClient


class BaseProduct():
    data = {
        "name":"Rempel - Corkery",
        "description":"you can't input the application without synthesizing the 1080p rss bandwidth!",
        "price":"204.96",
        "store_id": None,
    }

    @staticmethod
    async def create_product(async_client: AsyncClient, product_data: dict) -> dict:
        return await async_client.post(
            "/api/v1/products/", json={**product_data}
        )