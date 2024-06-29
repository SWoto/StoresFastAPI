import uuid
from sqlalchemy import UUID, Column, DateTime, Integer, String, ForeignKey, func, select
from sqlalchemy.orm import relationship

from src.core.configs import settings


class BaseModel(settings.DBBaseModel):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    modified_on = Column(DateTime, default=func.now(),
                         onupdate=func.now(), nullable=False)

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f"<InternalBaseModel(id={self.id}, created_on={self.created_on}, modified_on={self.modified_on})>"

    async def save_to_db(self, session):
        session.add(self)
        await session.commit()

    async def delete_from_db(self, session):
        await session.delete(self)
        await session.commit()

    @classmethod
    async def find_by_id(cls, session):
        query = select(cls).filter_by(id=id)
        result = await session.execute(query)
        return result.scalars().unique().one_or_none()
