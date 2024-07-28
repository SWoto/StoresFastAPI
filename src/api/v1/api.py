from fastapi import APIRouter

from src.api.v1.endpoints import users
from src.api.v1.endpoints import status
from src.api.v1.endpoints import stores
from src.api.v1.endpoints import products



api_router = APIRouter()
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(stores.router, prefix='/stores', tags=['stores'])
api_router.include_router(products.router, prefix='/products', tags=['products'])
api_router.include_router(status.router, prefix='/status', tags=['status'])
