"""
Configuration management for AI-Nihongo application.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration class using Pydantic."""
    
    # OpenAI Configuration
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    
    # Application Settings
    default_language: str = Field("en", env="DEFAULT_LANGUAGE")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Japanese Learning Settings
    difficulty_level: str = Field("beginner", env="DIFFICULTY_LEVEL")
    practice_session_length: int = Field(10, env="PRACTICE_SESSION_LENGTH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config() -> Config:
    """Load configuration from environment variables and .env file."""
    # Load .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    
    return Config()


def get_data_dir() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent / "data"


def get_models_dir() -> Path:
    """Get the models directory path."""
    return Path(__file__).parent.parent / "models"


# Global configuration instance
config = load_config()