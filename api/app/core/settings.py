import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Trading API Gateway"
    VERSION: str = "1.0.0"

    GRPC_TARGET: str = os.getenv("ENGINE_TARGET", "localhost:50051")
    SNAPSHOT_INTERVAL_SEC: float = 1.0
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6380")
    REDIS_DB: int = os.getenv("REDIS_DB", 1)

    class Config:
        env_file = ".env"


settings = Settings()