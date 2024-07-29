from sqlalchemy import Column, Numeric, DateTime, Boolean, Integer

from src.models.base import BaseModel


class PurchasesModel(BaseModel):
    __tablename__ = 'purchases'

    total_price = Column(Numeric(precision=10, scale=2))
    total_qnt = Column(Integer)
    paid = Column(Boolean, default=False)
    paid_on = Column(DateTime)

    def __init__(self, *args, **kwargs):
        super(PurchasesModel, self).__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<PurchasesModel(id={self.id}, total_price={self.total_price}, total_qnt={self.total_price}, paid={self.paid}, paid_on={self.paid_on}, created_on={self.created_on}, modified_on={self.modified_on})>"
