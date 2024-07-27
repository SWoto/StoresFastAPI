from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging

from src.core.database import Session
from src.models import UsersModel
from src.core.configs import settings, DevConfig
from src.core.mqtt import aiorabbit


logger = logging.getLogger(__name__)


async def get_session() -> AsyncGenerator:
    session: AsyncSession = Session()

    try:
        yield session
    finally:
        await session.close()


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
        return True
    except ValueError:
        return False


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


async def user_confirmation_email(email: str, confirmation_url: str):
    await send_user_registration_email(email, confirmation_url)

    if isinstance(settings, DevConfig):
        logger.debug(
            f"Confirmation URL for {email} is {confirmation_url}")
