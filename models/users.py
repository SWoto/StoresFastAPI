from sqlalchemy import Column, String, select, Boolean
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import BaseModel
from core.security import generate_hashed_password


class UsersModel(BaseModel):
    __tablename__ = 'users'

    first_name = Column(String(256), nullable=False)
    sur_name = Column(String(256), nullable=False)
    document = Column(String(50), unique=True, index=True)
    email = Column(String(256), unique=True, index=True)
    password = Column(String(256), nullable=False)
    admin = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(UsersModel, self).__init__(*args, **kwargs)
        self.password = generate_hashed_password(kwargs["password"])

    def __repr__(self):
        return f"<UsersModel(id={self.id}, first_name={self.first_name}, sur_name={self.sur_name}, document={self.document}, email={self.email}, created_on={self.created_on}, modified_on={self.modified_on}, admin={self.admin})>"

    @classmethod
    async def find_by_email(cls, email: str, db: AsyncSession):
        query = select(cls).filter_by(email=email).limit(1)
        result = await db.execute(query)
        return result.scalars().unique().one_or_none()

    @classmethod
    async def find_by_document(cls, document: str, db: AsyncSession):
        query = select(cls).filter_by(document=document).limit(1)
        result = await db.execute(query)
        return result.scalars().unique().one_or_none()
