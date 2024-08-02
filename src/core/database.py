import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession
)
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy import text

from src.core.configs import settings, DevConfig, TestConfig
import src.models

logger = logging.getLogger(__name__)



async def database_exists(base_url, database_name):
    logger.debug(f"Checking if database '{database_name}' exists")
    engine = create_async_engine(base_url, echo=True)
    async with engine.connect() as conn:
        try:
            result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = :dbname"), {'dbname': database_name})
            exists = result.scalar() is not None
            if exists:
                logger.debug(f"Database '{database_name}' was found")
            else:
                logger.warning(f"Database '{database_name}' does not exists")
            return exists
        except (ProgrammingError, OperationalError) as e:
            logger.error(f"Error checking database existence: {e}")
            return False
        finally:
            await conn.close()

async def create_database(settings):
    engine_url = str(settings.DATABASE_URL)
    database_name = settings.POSTGRES_DB
    base_url = engine_url.rsplit('/', 1)[0] + '/postgres' 

    logger.info("Checking if DB exists")
    if not await database_exists(base_url, database_name):
        logger.warning(f"Database '{database_name}' does not exist, trying to create it")
        engine = create_async_engine(base_url, isolation_level="AUTOCOMMIT", echo=True)
        async with engine.connect() as conn:
            try:
                await conn.execute(text(f"CREATE DATABASE {database_name}"))
                logger.info(f"Database '{database_name}' created successfully")
            except Exception as e:
                logger.error(f"Failed to create database '{database_name}': {e}")
            finally:
                await conn.close()
    else:
        logger.info("Database exists")

async def create_tables():
    logger.warning(f"Creating tables on DB: {engine.url}")
    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBaseModel.metadata.create_all)
        logger.debug("Created tables")


async def drop_tables():
    logger.warning(f"Dropping tables on DB")
    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBaseModel.metadata.drop_all)
        logger.debug("Tables removed")

engine = create_async_engine(settings.DATABASE_URL)

Session: AsyncSession = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)