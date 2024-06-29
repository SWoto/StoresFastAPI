from typing import Any
from pydantic_settings import BaseSettings
from sqlalchemy.orm import declarative_base


# TODO: Should i use singleton for this?
class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    # TODO: change DB URL based on the enviroment, if test, dev or prod
    DB_URL: str = "postgresql+asyncpg://Making4751:underdog-squishy-lushness@127.0.0.1:5432/testinho_db"
    DBBaseModel: Any = declarative_base()

    JWT_SECRET: str = "CcCknY1Lo38kjQwerJEFMuFQr8AFc-4YL4WAPAXmmdj-deQ"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*7  # 1 week

    model_config = dict(case_sensitive=True)


settings: Settings = Settings()
