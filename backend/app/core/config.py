"""
Конфигурация приложения через pydantic-settings
"""
from pathlib import Path
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILES = [BACKEND_ROOT / ".env", ".env"]


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=[str(path) for path in ENV_FILES],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # App
    APP_NAME: str = "CRM Backend"
    APP_ENV: str = "dev"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/crm.db"
    
    # JWT
    JWT_SECRET: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL_SECONDS: int = 300
    
    # Files
    FILE_STORAGE: str = "local"  # local | s3
    FILES_PATH: str = "./data/files"
    REPORTS_PATH: str = "./data/reports"
    MAX_FILE_SIZE_MB: int = 10
    
    # Security
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"])
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Парсинг CORS_ORIGINS из строки или списка"""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v
    
    @property
    def max_file_size_bytes(self) -> int:
        """Максимальный размер файла в байтах"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
