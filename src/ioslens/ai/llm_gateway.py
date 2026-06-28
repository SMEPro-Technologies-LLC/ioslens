"""LLM Gateway — routes completions and embeddings to configured providers."""

from __future__ import annotations

import logging

from ioslens.config import get_settings

logger = logging.getLogger(__name__)


class LLMGateway:
    """Routes LLM requests to OpenAI, Anthropic, or other providers.

    Provider selection is based on `default_llm_provider` in settings,
    but can be overridden per-request.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def complete(
        self,
        system_prompt: str,
        user_content: str,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a completion from the configured LLM provider."""
        provider = provider or self._settings.default_llm_provider
        logger.debug("LLM complete: provider=%s", provider)

        if provider == "openai":
            return await self._openai_complete(
                system_prompt,
                user_content,
                model or "gpt-4o-mini",
                temperature,
                max_tokens,
            )
        if provider == "anthropic":
            return await self._anthropic_complete(
                system_prompt,
                user_content,
                model or "claude-3-haiku-20240307",
                temperature,
                max_tokens,
            )

        raise ValueError(f"Unsupported LLM provider: {provider}")

    async def embed(
        self,
        text: str,
        model: str | None = None,
    ) -> list[float]:
        """Generate a text embedding vector."""
        model = model or self._settings.embedding_model
        logger.debug("LLM embed: model=%s", model)
        # Stub: return zero vector — real implementation calls OpenAI embeddings API
        return [0.0] * self._settings.embedding_dimensions

    async def _openai_complete(
        self,
        system_prompt: str,
        user_content: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call OpenAI chat completions API."""
        if not self._settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        # Real implementation: from openai import AsyncOpenAI; client = AsyncOpenAI(...)
        raise NotImplementedError("OpenAI integration not yet implemented in stub")

    async def _anthropic_complete(
        self,
        system_prompt: str,
        user_content: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Anthropic messages API."""
        if not self._settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")
        raise NotImplementedError("Anthropic integration not yet implemented in stub")
