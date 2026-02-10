import os
from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    APP_NAME: str = "Ceiling KP Generator"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenRouter AI
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Model for text parsing (Claude Sonnet 4.5)
    OPENROUTER_PARSER_MODEL: str = "anthropic/claude-sonnet-4"
    
    # Model for audio transcription (Gemini 3 Flash - supports audio)
    OPENROUTER_TRANSCRIBE_MODEL: str = "google/gemini-3-flash-preview"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
