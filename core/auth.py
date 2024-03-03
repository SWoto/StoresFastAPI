from pytz import timezone
from typing import Annotated, List, Optional
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from pydantic import BaseModel, EmailStr

from models import UsersModel
from core.configs import settings
from core.security import check_password

oauth2_schema = OAuth2PasswordBearer(
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


async def authenticate_user(email: EmailStr, password: str, db: AsyncSession) -> Optional[UsersModel]:
    async with db as session:
        user: UsersModel = await UsersModel.find_by_email(email, session)
        if (not user or
                not check_password(password, user.password)):
            return
        else:
            return user
