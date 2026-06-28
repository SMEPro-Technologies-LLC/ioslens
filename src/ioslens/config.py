"""iOSLENS application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────
    app_name: str = "iOSLENS"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # ── Database ──────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://localhost/ioslens",
        description="PostgreSQL async connection string",
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ── Redis ─────────────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # ── Auth / Tokens ─────────────────────────────────────────────────
    jwt_secret: str = Field(
        default="dev-jwt-secret-change-in-production",
        description="HMAC secret for JWT signing",
    )
    jwt_algorithm: str = "HS256"
    token_ttl_seconds: int = 900  # 15 minutes

    # ── AI Gateway ────────────────────────────────────────────────────
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    default_llm_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # ── MCP Server ────────────────────────────────────────────────────
    mcp_port: int = 8001
    mcp_host: str = "0.0.0.0"

    # ── API ───────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    cors_origins: list[str] = ["http://localhost:3000"]

    def model_post_init(self, __context: object) -> None:
        """Validate settings after initialization."""
        if (
            self.environment == "production"
            and self.jwt_secret == "dev-jwt-secret-change-in-production"
        ):
            raise ValueError(
                "JWT_SECRET must be set to a strong secret in production environments. "
                "The default placeholder value is not acceptable for production use."
            )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
