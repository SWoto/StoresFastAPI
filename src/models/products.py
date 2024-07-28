from sqlalchemy import Column, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.models.base import BaseModel


class ProductsModel(BaseModel):
    __tablename__ = 'products'

    name = Column(String(256), nullable=False)
    description = Column(String(256))
    price = Column(Numeric(precision=10, scale=2))

    store_id = mapped_column(ForeignKey("stores.id"), unique=False, nullable=False)
    store = relationship("StoresModel", back_populates="products", lazy='selectin')

    def __init__(self, *args, **kwargs):
        super(ProductsModel, self).__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<ProductsModel(id={self.id}, name={self.name}, description={self.description}, price={self.price}, created_on={self.created_on}, modified_on={self.modified_on})>"
