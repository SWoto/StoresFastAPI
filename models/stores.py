from sqlalchemy import Column, String

from models.base import BaseModel


class StoresModel(BaseModel):
    __tablename__ = 'stores'

    name = Column(String(256), nullable=False)
    description = Column(String(256))
    address = Column(String(256))
