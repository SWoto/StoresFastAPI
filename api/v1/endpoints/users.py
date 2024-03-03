from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from models import UsersModel
from schemas.users import PostPutUserSchema, ReturnUserSchema
from core.deps import get_session
from core.auth import authenticate_user, create_access_token, Token

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


@router.post('/login')
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_session)]) -> Token:
    user = await authenticate_user(email=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return Token(access_token=create_access_token(
        subject=str(user.id)), token_type='bearer')
