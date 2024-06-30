from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.configs import settings
from src.api.v1.api import api_router
from src.core.database import create_tables


@asynccontextmanager
async def init_db_tables(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(debug=True, title="Stores FastAPI", lifespan=init_db_tables)
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True, log_level="info")
