import logging
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, status, Depends, HTTPException


from src.models import StoresModel
from src.schemas.stores import PlainStoreSchema, ReturnStoreSchema
from src.core.deps import get_session, is_valid_uuid


logger = logging.getLogger(__name__)

router = APIRouter()

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ReturnStoreSchema)
async def post_store(store: PlainStoreSchema, db: Annotated[AsyncSession, Depends(get_session)]):
    post_data = store.model_dump()
    new_store = StoresModel(**post_data)

    async with db as session:
        session.add(new_store)
        await session.commit()

    return new_store

@router.get('/{id}', response_model=ReturnStoreSchema)
async def get_store_by_id(id: str, db: Annotated[AsyncSession, Depends(get_session)]):
    if not is_valid_uuid(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND)
    
    requested_store = await StoresModel.find_by_id(id, db)
    if not requested_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND)

    return requested_store