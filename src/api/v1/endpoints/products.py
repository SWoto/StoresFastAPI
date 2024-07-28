import logging
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, status, Depends, HTTPException


from src.models import ProductsModel, StoresModel
from src.schemas.products import PlainProductSchema, ProductSchemaWithoutStore
from src.schemas.nested_schemas import  CreateProductSchema, ReturnProductSchema, ReturnFullProductSchema
from src.core.deps import get_session, is_valid_uuid


logger = logging.getLogger(__name__)

router = APIRouter()

async def _get_product_by_id(id: str, db: Annotated[AsyncSession, Depends(get_session)]):
    if not is_valid_uuid(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND)
    
    requested_product = await ProductsModel.find_by_id(id, db)
    if not requested_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND)
  
    return requested_product


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ReturnProductSchema)
async def post_product(product: CreateProductSchema, db: Annotated[AsyncSession, Depends(get_session)]):
    post_data = product.model_dump()
    new_product = ProductsModel(**post_data)

    async with db as session:
        if not await StoresModel.find_by_id(new_product.store_id, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Store ID not found")
        session.add(new_product)
        await session.commit()

    return new_product

@router.get('/{id}', response_model=ReturnProductSchema)
async def get_product_by_id(product: Annotated[ProductsModel, Depends(_get_product_by_id)]):
    return product

@router.get('/complete/{id}', response_model=ReturnFullProductSchema)
async def get_product_by_id_with_relationship(product: Annotated[ProductsModel, Depends(_get_product_by_id)]):
    return product