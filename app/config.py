"""
Configuration management for the application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "webown"
    MYSQL_USER: str = "webown"
    MYSQL_PASSWORD: str = "webown_password"
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Scheduler Configuration
    SCHEDULER_ENABLED: bool = True
    LEBONCOIN_INTERVAL_MINUTES: int = 30
    SELOGER_INTERVAL_MINUTES: int = 30
    CARTE_COLOC_INTERVAL_MINUTES: int = 30
    
    # Scraping Configuration
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    REQUEST_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

