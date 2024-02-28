from sqlalchemy import Column, Numeric, String

from models.base import BaseModel


class ProductsModel(BaseModel):
    __tablename__ = 'products'

    name = Column(String(256), nullable=False)
    description = Column(String(256))
    price = Column(Numeric(precision=10, scale=2))
