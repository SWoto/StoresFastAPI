from core.database import engine
from core.configs import settings


async def create_tables() -> None:
    import models
    print("Creating all data tables...")

    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBaseModel.metadata.drop_all)
        await conn.run_sync(settings.DBBaseModel.metadata.create_all)
    print("Tables created")

if __name__ == "__main__":
    import asyncio

    asyncio.run(create_tables())
