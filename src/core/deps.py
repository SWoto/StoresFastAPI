from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.core.database import Session


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
