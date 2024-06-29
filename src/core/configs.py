from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets
from sqlalchemy.orm import declarative_base


from functools import lru_cache


class BaseConfig(BaseSettings):
    API_V1_STR: str = '/api/v1'
    ENV_STATE: Optional[str] = None

    """Loads the dotenv file. Including this is necessary to get
    pydantic to load a .env file."""
    model_config = SettingsConfigDict(env_file=".env")


class GlobalConfig(BaseSettings):
    DATABASE_URL: Optional[str] = None
    JWT_SECRET: str = secrets.token_hex(64)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*7  # 1 week
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_HOST: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def __init__(self):
        super(GlobalConfig, self).__init__()
        self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="TEST_")


""" class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    # TODO: change DB URL based on the enviroment, if test, dev or prod
    DB_URL: str = "postgresql+asyncpg://Making4751:underdog-squishy-lushness@127.0.0.1:5432/testinho_db"
    DBBaseModel: Any = declarative_base()

    JWT_SECRET: str = "CcCknY1Lo38kjQwerJEFMuFQr8AFc-4YL4WAPAXmmdj-deQ"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*7  # 1 week

    model_config = dict(case_sensitive=True)


settings: Settings = Settings()
 """


@lru_cache
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


settings = get_config(BaseConfig().ENV_STATE)
