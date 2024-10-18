from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets
from sqlalchemy.orm import declarative_base


from functools import lru_cache


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    """Loads the dotenv file. Including this is necessary to get
    pydantic to load a .env file."""
    # TODO: Set extra=True due to be using only one file, but later this should be removed.
    model_config = SettingsConfigDict(
        env_file="src/core/.env", case_sensitive=True, extra='ignore')


class GlobalConfig(BaseConfig):
    API_V1_STR: str = '/api/v1'

    JWT_SECRET: str = secrets.token_hex(64)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*1  # 1 day
    CONFIRMATION_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes

    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_HOST: Optional[str] = None

    RABBITMQ_URL: Optional[str] = None
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASS: Optional[str] = None
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[int] = None

    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None

    DBBaseModel: Any = declarative_base()

    def __init__(self):
        super(GlobalConfig, self).__init__()
        self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        self.RABBITMQ_URL = f'amqps://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/%2F?connection_attempts=3&heartbeat=3600'


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="TEST_")


@lru_cache
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


settings = get_config(BaseConfig().ENV_STATE)
