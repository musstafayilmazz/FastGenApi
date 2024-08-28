import os
from functools import lru_cache
from typing import Optional
import logging
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = os.getenv("ENV_STATE", "dev")  # Provide a default value
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class GlobalConfig(BaseConfig):
    POSTGRES_URL: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USERNAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET_NAME: Optional[str] = None
    MINIO_ENDPOINT: Optional[str] = None
    DB_FORCE_ROLLBACK: bool = False
    RAPID_API_KEY: Optional[str] = None

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.POSTGRES_URL}/{self.DB_NAME}"

class DevConfig(GlobalConfig):
    POSTGRES_URL: Optional[str] = os.getenv("DEV_POSTGRES_URL")
    DB_NAME: Optional[str] = os.getenv("DEV_DB_NAME")
    DB_USERNAME: Optional[str] = os.getenv("DEV_DB_USERNAME")
    DB_PASSWORD: Optional[str] = os.getenv("DEV_DB_PASSWORD")
    MINIO_ACCESS_KEY: Optional[str] = os.getenv("DEV_MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: Optional[str] = os.getenv("DEV_MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: Optional[str] = os.getenv("DEV_MINIO_BUCKET_NAME")
    MINIO_ENDPOINT: Optional[str] = os.getenv("DEV_MINIO_ENDPOINT")

class ProdConfig(GlobalConfig):
    POSTGRES_URL: Optional[str] = os.getenv("PROD_POSTGRES_URL")
    DB_NAME: Optional[str] = os.getenv("PROD_DB_NAME")
    DB_USERNAME: Optional[str] = os.getenv("PROD_DB_USERNAME")
    DB_PASSWORD: Optional[str] = os.getenv("PROD_DB_PASSWORD")
    MINIO_ACCESS_KEY: Optional[str] = os.getenv("PROD_MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: Optional[str] = os.getenv("PROD_MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: Optional[str] = os.getenv("PROD_MINIO_BUCKET_NAME")
    MINIO_ENDPOINT: Optional[str] = os.getenv("PROD_MINIO_ENDPOINT")

@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig}
    return configs[env_state]()



config = get_config(BaseConfig().ENV_STATE)
