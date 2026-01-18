from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://prelanding:prelanding123@localhost:5432/prelanding_db"
    
    # Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "prelanding_elements"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str
    openai_base_url: Optional[str] = None
    
    # API Configuration
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Upload Settings
    max_upload_size_mb: int = 100
    upload_dir: str = "./uploads"
    
    # Generation Settings
    default_temperature: float = 0.7
    max_tokens: int = 2000
    
    # Active Learning
    auto_promotion_threshold: float = 5.0
    min_feedback_samples: int = 10
    
    # Compliance
    default_compliance_level: str = "strict_facebook"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
