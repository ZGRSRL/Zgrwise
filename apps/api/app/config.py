import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    postgres_user: str = "zgr"
    postgres_password: str = "zgrpass"
    postgres_db: str = "zgrwise"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Ollama
    ollama_base: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    
    # Embeddings
    emb_model: str = "BAAI/bge-small-en-v1.5"
    emb_dim: int = 384
    
    # API
    api_key: str = "devkey"
    
    # Export
    obsidian_export_path: str = "./data/exports"
    
    # Security & Rate Limiting
    rate_limit_per_minute: int = 100
    
    class Config:
        env_file = ".env"


settings = Settings() 