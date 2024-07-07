import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession
)

from src.core.configs import settings
import src.models

logger = logging.getLogger(__name__)


engine = create_async_engine(settings.DATABASE_URL)


async def create_tables():
    logger.critical(f"Creating tables on DB")
    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBaseModel.metadata.create_all)


async def drop_tables():
    logger.critical(f"Dropping tables on DB")
    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBaseModel.metadata.drop_all)


Session: AsyncSession = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
