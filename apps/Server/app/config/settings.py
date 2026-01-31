"""Application settings using Pydantic Settings."""

import json
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: Optional[str] = None

    # JWT Authentication
    JWT_SECRET_KEY: str = "change-this-in-production-min-32-characters"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS - JSON array format
    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:8000"]'

    # Server
    SERVER_PORT: int = 8000
    USE_MOCK_APIS: bool = True

    # AI Data Extraction
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    REMOVEBG_API_KEY: Optional[str] = None
    EXTRACTION_AI_PROVIDER: str = "anthropic"
    EXTRACTION_MAX_RETRIES: int = 3
    EXTRACTION_TIMEOUT_SECONDS: int = 60

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from JSON string to list."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except json.JSONDecodeError:
            print("WARN [Settings]: Failed to parse CORS_ORIGINS, using defaults")
            return ["http://localhost:5173", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
