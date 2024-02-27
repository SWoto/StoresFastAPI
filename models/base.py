import uuid
from sqlalchemy import UUID, Column, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship

from core.configs import settings


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
