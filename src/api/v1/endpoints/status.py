from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone

router = APIRouter()


@router.get('/live', status_code=status.HTTP_200_OK)
async def get_live():
    return datetime.now(timezone.utc).isoformat()
