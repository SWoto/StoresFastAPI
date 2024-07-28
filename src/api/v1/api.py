from fastapi import APIRouter

from src.api.v1.endpoints import users
from src.api.v1.endpoints import status
from src.api.v1.endpoints import stores
from src.api.v1.endpoints import products



api_router = APIRouter()
api_router.include_router(users.router, prefix='/users', tags=['Users'])
api_router.include_router(stores.router, prefix='/stores', tags=['Stores'])
api_router.include_router(products.router, prefix='/products', tags=['Products'])
api_router.include_router(status.router, prefix='/status', tags=['Status'])
