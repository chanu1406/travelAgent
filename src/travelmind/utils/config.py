"""
Configuration Management

Loads settings from environment variables and .env files.
Uses pydantic-settings for type-safe configuration.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Settings are loaded from:
    1. Environment variables
    2. .env file in project root
    3. Default values (defined here)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Configuration
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # External API Keys
    opentripmap_api_key: str | None = None
    openrouteservice_api_key: str | None = None
    osrm_base_url: str = "http://router.project-osrm.org"

    # Caching
    cache_dir: Path = Path(".cache/travelmind")
    cache_ttl_seconds: int = 86400  # 24 hours

    # Rate Limiting
    rate_limit_rpm: int = 60  # Requests per minute

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Logging
    log_level: str = "INFO"

    # Development
    environment: str = "development"
    debug: bool = False

    def __init__(self, **kwargs):  # type: ignore
        """Initialize settings and create cache directory if needed."""
        super().__init__(**kwargs)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
