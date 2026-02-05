import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "mobile-automation-agent"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # BrowserStack
    BROWSERSTACK_USERNAME: Optional[str] = None
    BROWSERSTACK_ACCESS_KEY: Optional[str] = None
    BROWSERSTACK_HUB: str = "https://hub-cloud.browserstack.com/wd/hub"

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # AI Keys
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2-vision:latest"

    # Security
    ENCRYPTION_KEY: str = "change-me-in-prod"
    PIN_SALT: str = "change-me-in-prod"

    # Feature Flags
    ENABLE_SUPABASE: bool = True
    ENABLE_REDIS: bool = True
    ENABLE_OLLAMA: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CONFIG_DIR: Path = BASE_DIR / "config"
    AGENTS_DIR: Path = CONFIG_DIR / "agents" # YAMLs moved to config/agents? No, user has agents/yaml in root.
    # Actually, file structure puts agents/yaml in "agents/". Let's point to that.
    # WAIT. My script put agents/yaml in mobile-automation-agent/agents/.
    # And Settings is in mobile-automation-agent/config/settings.py.
    # So ROOT/agents.
    
    @property
    def AGENT_CONFIG_DIR(self) -> Path:
        return self.BASE_DIR / "agents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
