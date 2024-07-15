import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

# first thing to initialize the ENV variables
from src.core.configs import settings
from src.core.mqtt import aiorabbit
from src.core.logging import configure_logging
from src.api.v1.api import api_router
from src.core.database import create_tables


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await create_tables()
    aiorabbit.connect()
    yield

app = FastAPI(debug=True, title="Stores FastAPI",
              lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True, log_level="info")
