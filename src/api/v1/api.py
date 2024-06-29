from fastapi import APIRouter

from src.api.v1.endpoints import users
from src.api.v1.endpoints import status


api_router = APIRouter()
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(status.router, prefix='/status', tags=['status'])
