from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, relationship
from typing import List

from src.models.base import BaseModel


class StoresModel(BaseModel):
    __tablename__ = 'stores'

    name = Column(String(256), nullable=False)
    description = Column(String(256))
    address = Column(String(256))

    products = relationship("ProductsModel", back_populates="store", cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        super(StoresModel, self).__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<StoresModel(id={self.id}, name={self.name}, description={self.description}, address={self.address}, created_on={self.created_on}, modified_on={self.modified_on})>"
