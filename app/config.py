import os
from typing import List

class Settings:
    """Simplified settings without Pydantic validation"""
    
    # Application Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_RECOMMENDATIONS = int(os.getenv("MAX_RECOMMENDATIONS", "20"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://recommender:password@postgres:5432/recommender_db"
    )
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_POOL_SIZE = int(os.getenv("REDIS_POOL_SIZE", "20"))
    
    # Feature Store
    FEATURE_STORE_PATH = os.getenv("FEATURE_STORE_PATH", "/app/data/features")
    MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "7de9093535a40fad13c284d89bea0076341f709dce3a93cf73bc2163a0eac2d2")
    
    # Parse allowed origins from comma-separated string
    _origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
    ALLOWED_ORIGINS = [origin.strip() for origin in _origins_str.split(",")]

settings = Settings()