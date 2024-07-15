from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone

from src.core.mqtt import aiorabbit

router = APIRouter()


@router.get('/live', status_code=status.HTTP_200_OK)
async def get_live():
    current_date = datetime.now(timezone.utc).isoformat()
    aiorabbit.publish_message(f"I'm alive. It is: {current_date}")
    return datetime.now(timezone.utc).isoformat()
