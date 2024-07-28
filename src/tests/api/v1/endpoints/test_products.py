import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ProductsModel

class TestProduct():
    product_data = {
        "name":"Rempel - Corkery",
        "description":"you can't input the application without synthesizing the 1080p rss bandwidth!",
        "price":204.96,
        "store_id": None,
    }