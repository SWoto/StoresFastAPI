from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import BaseModel
from core.security import generate_hashed_password


class ClientsModel(BaseModel):
    __tablename__ = 'clients'

    first_name = Column(String(256), nullable=False)
    sur_name = Column(String(256), nullable=False)
    document = Column(String(50), unique=True, index=True)
    email = Column(String(256), unique=True, index=True)
    password = Column(String(256), nullable=False)

    def __init__(self, *args, **kwargs):
        super(ClientsModel, self).__init__(*args, **kwargs)
        self.password = generate_hashed_password(kwargs["password"])

    @classmethod
    async def find_by_email(cls, email: str, db: AsyncSession):
        async with db as session:
            return session.query(cls).filter_by(email=email).unique().one_or_none()

    @classmethod
    async def find_by_document(cls, document: str, db: AsyncSession):
        async with db as session:
            return session.query(cls).filter_by(document=document).unique().one_or_none()
