import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    
    # AI Service
    GEMINI_API_KEY: str = "temp-key"
    AI_MODEL: str = "gemini-1.5-flash"
    
    # Embeddings
    EMB_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMB_DIM: int = 384
    
    # API Security
    API_KEY: str
    SECRET_KEY: str = "default-secret-key-change-in-production"
    
    # CORS
    CORS_ALLOW_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    
    # Export
    OBSIDIAN_EXPORT_PATH: str = "./data/exports"
    
    # Security & Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # env yoksa burada hata versin 