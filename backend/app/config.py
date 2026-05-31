from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "Auto-Doc Agent"
    debug: bool = False

    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    database_url: str
    database_url_direct: str

    redis_url: str
    celery_broker_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    cache_ttl_seconds: int = 86400


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()