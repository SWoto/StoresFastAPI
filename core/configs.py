from typing import Any
from pydantic_settings import BaseSettings
from sqlalchemy.ext.declarative import declarative_base


# TODO: Should i use singleton for this?
class Settings(BaseSettings):
    DBBaseModel: Any = declarative_base()

    class Config:
        case_sensitive = True


settings: Settings = Settings()
