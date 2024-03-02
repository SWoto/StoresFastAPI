from typing import Annotated
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status

from models.users import UsersModel
from schemas.users import PostPutUserSchema, ReturnUserSchema
from core.deps import get_session

router = APIRouter()


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ReturnUserSchema)
async def post_user(user: PostPutUserSchema, db: Annotated[AsyncSession, Depends(get_session)]):
    post_data = user.model_dump()
    new_user = UsersModel(**post_data)

    async with db as session:
        if await UsersModel.find_by_email(
                new_user.email, session):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        if await UsersModel.find_by_document(
                new_user.document, session):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Document already registered")

        session.add(new_user)
        await session.commit()

    return new_user
