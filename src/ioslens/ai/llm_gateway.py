"""LLM gateway — route to OpenAI / Anthropic / Gemini based on tenant config."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ioslens.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMResponse:
    """Structured response from the LLM gateway."""

    def __init__(self, content: str, provider: str, model: str, tokens_used: int) -> None:
        self.content = content
        self.provider = provider
        self.model = model
        self.tokens_used = tokens_used


class LLMGateway:
    """Route LLM requests to the configured provider."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.provider = provider or settings.default_llm_provider
        self.model = model or settings.default_llm_model

    async def complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to the configured LLM provider."""
        if self.provider == "openai":
            return await self._call_openai(messages, max_tokens, temperature)
        elif self.provider == "anthropic":
            return await self._call_anthropic(messages, max_tokens, temperature)
        elif self.provider == "gemini":
            return await self._call_gemini(messages, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider!r}")

    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")

        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise ImportError("openai package not installed") from e

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        resp = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = resp.choices[0].message.content or ""
        tokens = resp.usage.total_tokens if resp.usage else 0
        return LLMResponse(content, "openai", self.model, tokens)

    async def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")

        try:
            import anthropic
        except ImportError as e:
            raise ImportError("anthropic package not installed") from e

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        # Extract system message if present
        system = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_messages = [m for m in messages if m["role"] != "system"]

        resp = await client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or "",
            messages=user_messages,
        )
        content = resp.content[0].text if resp.content else ""
        return LLMResponse(content, "anthropic", self.model, resp.usage.input_tokens + resp.usage.output_tokens)

    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")

        raise NotImplementedError("Gemini integration not yet implemented")

    async def embed(self, text: str) -> List[float]:
        """Generate a text embedding using the configured provider."""
        if self.provider == "openai":
            if not settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY not configured")
            try:
                from openai import AsyncOpenAI
            except ImportError as e:
                raise ImportError("openai package not installed") from e
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await client.embeddings.create(
                model=settings.embedding_model,
                input=text,
            )
            return resp.data[0].embedding
        raise NotImplementedError(f"Embeddings not implemented for provider {self.provider!r}")
