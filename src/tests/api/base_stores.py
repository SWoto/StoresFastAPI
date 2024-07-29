import pytest
from httpx import AsyncClient

class BaseStore():
    data = {
        "name":"Stanton - Heathcote",
        "description":"i'll reboot the optical xml bandwidth, that should program the css panel!",
        "address":"168 Johnson Plaza",
    }

    @staticmethod
    async def create_store(async_client: AsyncClient, store_data: dict, logged_in_token: str) -> dict:
        return await async_client.post(
            "/api/v1/stores/", json={**store_data}, headers={'Authorization': f'Bearer {logged_in_token}'}
        )