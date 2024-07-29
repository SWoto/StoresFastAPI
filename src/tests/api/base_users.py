import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


from src.models import UsersModel


class BaseUser():
    data = {
        'email': 'test@example.net', 
        "first_name": "Alison",
        "sur_name": "Brown", 
        "document": "12345678901", 
        "password": "ito2i23", 
        "role": "none", 
        "confirmed": False,
    }

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
        self.data["confirmed"] = False