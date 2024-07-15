from functools import wraps
import logging
import uuid

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
from src.core.deps import get_session
from src.core.mqtt import aiorabbit
from src.core.blocklist import jwt_redis_blocklist


logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login"
)


class Token(BaseModel):
    access_token: str
    token_type: str


def create_token(token_type: str, life_time: timedelta, subject: str) -> str:
    payload = {}  # More about at: https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3
    timezone_sao_paulo = timezone('America/Sao_Paulo')
    now = datetime.now(tz=timezone_sao_paulo)
    expires_on = now + life_time
    logger.debug(f"Creating {token_type} token", extra={
                 "id": subject, "experis_on": expires_on})

    payload['type'] = token_type
    payload['exp'] = expires_on
    payload['iat'] = now  # issued at
    payload['sub'] = subject
    payload['jti'] = str(uuid.uuid4())  # so we can blacklist

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    # https://jwt.io
    return create_token('access_token', timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), subject=subject)


def create_confirmation_token(subject: str) -> str:
    return create_token('confirmation', timedelta(minutes=settings.CONFIRMATION_TOKEN_EXPIRE_MINUTES), subject=subject)


async def get_user(db: AsyncSession, **kwargs) -> Optional[UsersModel]:
    logger.debug("Fetching user from the database", extra=kwargs)
    async with db as session:
        if kwargs.get('email'):
            return await UsersModel.find_by_email(kwargs['email'], session)
        elif kwargs.get('id'):
            return await UsersModel.find_by_id(kwargs['id'], session)
        else:
            return


async def authenticate_user(email: EmailStr, password: str, db: AsyncSession) -> Optional[UsersModel]:
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(db, email=email)
    if (not user or
            not check_password(password, user.password)):
        return
    else:
        return user


def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def validate_token(token: Annotated[str, Depends(oauth2_scheme)], type: Literal["access_token", "confirmation"] = "access_token") -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError as e:
        logger.error(f"Token has expired: {e}")
        raise create_credentials_exception("Token has expired") from e
    except JWTError as e:
        logger.error(f"Invalid Token: {e}")
        raise create_credentials_exception("Invalid token") from e

    jti = payload.get("jti")
    jti_in_redis = jwt_redis_blocklist.get(jti)
    if not jti or jti_in_redis:
        # should I? maybe a vague answer would be more secure
        raise create_credentials_exception("Token with invalid 'jti' field")

    user_id = payload.get("sub")
    if not user_id:
        raise create_credentials_exception("Token is missing 'sub' field")

    token_type = payload.get("type")
    if not token_type or token_type != type:
        logger.error(
            f"Token has incorrect type. Expects: {type}, Received:{token_type}")
        raise create_credentials_exception("Token has incorrect type")

    return payload


async def blacklist_token(payload: Annotated[dict, Depends(validate_token)]):
    jti = payload.get("jti")
    token_type = payload.get("type")
    experis_on = timedelta(minutes=settings.CONFIRMATION_TOKEN_EXPIRE_MINUTES) if token_type == "confirmation" else timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_redis_blocklist.set(jti, "", ex=experis_on)


async def get_current_user(payload: Annotated[dict, Depends(validate_token)], db: Annotated[AsyncSession, Depends(get_session)]):
    user_id = payload.get("sub")
    user = await get_user(db, id=user_id)
    if user is None:
        raise create_credentials_exception("Invalid 'id' field")

    return user


# default as admin to err on the side of safety
def authorize(role: Literal["all", "admin"] = "admin"):
    def decorator(func):
        @wraps(func)
        async def wrapper(current_user: Annotated[UsersModel, Depends(get_current_user)], *args, **kwargs):
            if not current_user.is_admin() and role != 'all':
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# TODO: MQTT
async def send_user_registration_email(email: str, confirmation_url: str):
    subject = "Successfully signed up - Confirm your email"
    body = (
        f"Hi {email}! You have successfully signed up to the StoresFastAPI."
        " Please confirm your email by clicking on the"
        f" following link: {confirmation_url}.\n"
        "Note: This link is valid only for 30 minutes."
    )
    payload = {'subject': subject, 'body': body}
    aiorabbit.publish_message(payload)
    pass
