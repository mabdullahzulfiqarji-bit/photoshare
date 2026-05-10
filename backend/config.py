"""
Configuration settings for PhotoShare application.
All sensitive values are loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Azure SQL
    DATABASE_URL: str = "sqlite:///./photoshare.db"  # Fallback for local dev
    
    # Azure SQL (production)
    AZURE_SQL_SERVER: Optional[str] = None
    AZURE_SQL_DATABASE: Optional[str] = None
    AZURE_SQL_USERNAME: Optional[str] = None
    AZURE_SQL_PASSWORD: Optional[str] = None
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: str = "photos"
    AZURE_STORAGE_THUMBNAILS_CONTAINER: str = "thumbnails"
    
    # Azure AI Vision (Cognitive Services)
    AZURE_VISION_KEY: Optional[str] = None
    AZURE_VISION_ENDPOINT: Optional[str] = None
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # App
    DEBUG: bool = True
    FRONTEND_URL: str = "http://localhost:5173"
    
    # File upload limits
    MAX_FILE_SIZE_MB: int = 16
    THUMBNAIL_SIZE: tuple = (400, 400)
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
