from random import randint
import tempfile
import logging
import aiofiles
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Request, BackgroundTasks

from src.models import UsersModel
from src.schemas import PostPutUserSchema, ReturnUserSchema
from src.core.deps import get_session, is_valid_uuid, user_confirmation_email
from src.core.auth import Token, authenticate_user, create_access_token, create_confirmation_token, get_current_user, RoleChecker, validate_token, blacklist_token
from src.core.configs import settings, DevConfig

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024
EXISTING_ROLES = ["admin", "none"]


@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=ReturnUserSchema)
async def post_user(user: PostPutUserSchema, request: Request, background_tasks: BackgroundTasks, db: Annotated[AsyncSession, Depends(get_session)]):
    post_data = user.model_dump()
    new_user = UsersModel(**post_data)

    async with db as session:
        if new_user.role not in EXISTING_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
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

        background_tasks.add_task(
            user_confirmation_email,
            email=new_user.email,
            confirmation_url=request.url_for(
                "get_confirm_email",
                token=create_confirmation_token(str(new_user.id))),
        )

    return new_user


@router.get('/confirm/{token}', status_code=status.HTTP_202_ACCEPTED)
async def get_confirm_email(token: str, db: Annotated[AsyncSession, Depends(get_session)]):
    payload = await validate_token(token, "confirmation")
    user = await get_current_user(payload, db)

    if not user.has_confirmed():
        async with db as session:
            requested_user = await UsersModel.find_by_id(user.id, session)
            requested_user.confirmed = True
            await session.commit()

    await blacklist_token(payload)

    return {"detail": "User confirmed"}


@router.get('/', response_model=ReturnUserSchema)
async def get_user(current_user: Annotated[UsersModel, Depends(get_current_user)]):
    return current_user


@router.get('/{id}', response_model=ReturnUserSchema)
async def get_user_by_id(id: str, _: Annotated[str, Depends(RoleChecker(allowed_roles=["admin"]))], db: Annotated[AsyncSession, Depends(get_session)]):
    if not is_valid_uuid(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND)

    requested_user = await UsersModel.find_by_id(id, db)
    if not requested_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND)

    return requested_user


@router.post('/login')
async def login_user(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_session)]) -> Token:
    user = await authenticate_user(email=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.has_confirmed():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail pending confirmation",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(
        subject=str(user.id)), token_type='bearer')


# TODO: This will integrate with mqtt for some heavy lifting
@router.post('/import/upload')
async def post_upload_csv(file: UploadFile, _: Annotated[str, Depends(RoleChecker(allowed_roles=["admin"]))]):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
            logger.info(f"Saving uploaded file temporarily to {filename}")
            async with aiofiles.open(filename, "wb") as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)
    except Exception as e:
        logger.exception("Failed to save temp file. Error", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        )
