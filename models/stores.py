from sqlalchemy import Column, Numeric, String
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import BaseModel


class StoresModel(BaseModel):
    __tablename__ = 'stores'

    name = Column(String(256), nullable=False)
    description = Column(String(256))
    address = Column(String(256))
