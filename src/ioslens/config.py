"""Application configuration via Pydantic Settings (env-var driven)."""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "iOSLENS"
    version: str = "1.0.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ── Server ────────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    mcp_host: str = Field(default="0.0.0.0", alias="MCP_HOST")
    mcp_port: int = Field(default=8001, alias="MCP_PORT")

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="******localhost:5432/ioslens",
        alias="DATABASE_URL",
    )
    database_pool_min: int = Field(default=5, alias="DB_POOL_MIN")
    database_pool_max: int = Field(default=20, alias="DB_POOL_MAX")

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )

    # ── JWT / Auth ────────────────────────────────────────────────────────────
    jwt_secret: str = Field(default="dev-jwt-secret-change-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiry_seconds: int = Field(default=3600, alias="JWT_EXPIRY_SECONDS")

    # ── Execution tokens ──────────────────────────────────────────────────────
    execution_token_ttl_seconds: int = Field(default=60, alias="EXECUTION_TOKEN_TTL")

    # ── AI providers ─────────────────────────────────────────────────────────
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    default_llm_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")
    default_llm_model: str = Field(default="gpt-4o", alias="DEFAULT_LLM_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    # ── Rate limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: List[str] = Field(default=["http://localhost:3000"], alias="CORS_ORIGINS")

    # ── Telemetry ─────────────────────────────────────────────────────────────
    otel_endpoint: Optional[str] = Field(default=None, alias="OTEL_ENDPOINT")
    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
