from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):

  #app
  app_name: str = "Auto-Doc Agent"
  debug: bool = False
  #Anthropic
  gemini_api_key:str
  #Database
  database_url:str
  database_url_direct:str
  #Redis
  redis_url:str
  celery_broker_url:str
  #JWT
  jwt_secret: str
  jwt_algorithm:str = "HS256"
  jwt_expiry_minutes:int = 60

  #cache
  cache_ttl_seconds: int = 86400

  class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
@lru_cache()
def get_settings() -> Settings:
  return Settings()

settings = get_settings()
