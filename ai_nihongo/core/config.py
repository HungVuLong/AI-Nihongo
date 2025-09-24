"""Configuration settings for AI-Nihongo."""

import os
from typing import Optional


class Settings:
    """Application settings."""
    
    def __init__(self):
        # Load environment variables
        self._load_env()
        
        # API Keys
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        
        # Database
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ai_nihongo.db")
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # API Configuration
        self.api_host: str = os.getenv("API_HOST", "0.0.0.0")
        self.api_port: int = int(os.getenv("API_PORT", "8000"))
        self.debug: bool = os.getenv("DEBUG", "True").lower() == "true"
        
        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv("LOG_FILE", "logs/app.log")
        
        # Model Configuration
        self.default_model: str = os.getenv("DEFAULT_MODEL", "gpt-4")
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Japanese Language Processing
        self.tokenizer_model: str = os.getenv("TOKENIZER_MODEL", "mecab")
        self.sudachi_dict_type: str = os.getenv("SUDACHI_DICT_TYPE", "core")
    
    def _load_env(self):
        """Load environment variables from .env file if it exists."""
        env_file = ".env"
        if os.path.exists(env_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                # Manually load .env file if python-dotenv is not available
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()


# Global settings instance
settings = Settings()