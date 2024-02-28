from typing import Any
from pydantic_settings import BaseSettings
from sqlalchemy.ext.declarative import declarative_base


# TODO: Should i use singleton for this?
class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://Making4751:underdog-squishy-lushness@127.0.0.1:5432/testinho_db"
    DBBaseModel: Any = declarative_base()

    class Config:
        case_sensitive = True


settings: Settings = Settings()
