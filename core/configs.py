from typing import Any
from pydantic_settings import BaseSettings
from sqlalchemy.ext.declarative import declarative_base


# TODO: Should i use singleton for this?
class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str = "postgresql+asyncpg://Making4751:underdog-squishy-lushness@127.0.0.1:5432/testinho_db"
    DBBaseModel: Any = declarative_base()

    JWT_SECRET: str = "CcCknY1Lo38kjQwerJEFMuFQr8AFc-4YL4WAPAXmmdj-deQ"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*7  # 1 week

    class Config:
        case_sensitive = True


settings: Settings = Settings()
