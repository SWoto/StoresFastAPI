from pytz import timezone
from typing import Annotated, List, Literal, Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel, EmailStr

from src.models import UsersModel
from src.core.configs import settings
from src.core.security import check_password

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login"
)


class Token(BaseModel):
    access_token: str
    token_type: str


def create_token(token_type: str, life_time: timedelta, subject: str) -> str:
    payload = {}  # More about at: https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3
    timezone_sao_paulo = timezone('America/Sao_Paulo')
    expires_on = datetime.now(tz=timezone_sao_paulo) + life_time

    payload['type'] = token_type
    payload['exp'] = expires_on
    payload['iat'] = datetime.now(tz=timezone_sao_paulo)  # issued at
    payload["sub"] = subject

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    # https://jwt.io
    return create_token('access_token', timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), subject=subject)


async def get_user(db: AsyncSession, **kwargs) -> Optional[UsersModel]:
    async with db as session:
        if kwargs.get('email'):
            return await UsersModel.find_by_email(kwargs['email'], session)
        elif kwargs.get('id'):
            return await UsersModel.find_by_id(kwargs['id'], session)
        else:
            return


async def authenticate_user(email: EmailStr, password: str, db: AsyncSession) -> Optional[UsersModel]:
    user = await get_user(db, email=email)
    if (not user or
            not check_password(password, user.password)):
        return
    else:
        return user


async def get_current_user(token: str, db: AsyncSession) -> Optional[UsersModel]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(db, id=user_id)
    if user is None:
        raise credentials_exception
    return user
