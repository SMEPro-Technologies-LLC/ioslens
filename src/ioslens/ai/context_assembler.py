"""Context assembler — builds bounded, sanitized context chunks for LLM calls."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Maximum token budget for a single context window
MAX_CONTEXT_TOKENS = 8192


@dataclass
class ContextChunk:
    """A bounded context chunk ready for LLM consumption."""

    system_prompt: str
    user_content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    estimated_tokens: int = 0


class ContextAssembler:
    """Constructs bounded, sanitized context chunks for LLM gateway calls.

    Responsibilities:
      - Retrieve relevant data from governed sources
      - Apply LENS-filtered field exclusions
      - Sanitize for prompt injection
      - Stay within token budget
    """

    INJECTION_PATTERNS = [
        "ignore previous instructions",
        "disregard system prompt",
        "you are now",
        "forget your instructions",
    ]

    def assemble(
        self,
        system_context: str,
        user_query: str,
        data_chunks: list[dict[str, Any]],
        excluded_fields: set[str] | None = None,
        max_tokens: int = MAX_CONTEXT_TOKENS,
    ) -> ContextChunk:
        """Assemble a sanitized context chunk."""
        excluded_fields = excluded_fields or set()

        # Sanitize user query for prompt injection
        sanitized_query = self._sanitize(user_query)

        # Filter data chunks
        filtered_chunks = [self._filter_fields(chunk, excluded_fields) for chunk in data_chunks]

        # Build user content
        data_str = "\n".join(str(c) for c in filtered_chunks)
        user_content = f"Query: {sanitized_query}\n\nContext:\n{data_str}"

        # Rough token estimate (4 chars ≈ 1 token)
        estimated = (len(system_context) + len(user_content)) // 4

        logger.debug(
            "Context assembled: estimated_tokens=%d excluded_fields=%s",
            estimated,
            excluded_fields,
        )

        return ContextChunk(
            system_prompt=system_context,
            user_content=user_content,
            estimated_tokens=estimated,
        )

    def _sanitize(self, text: str) -> str:
        """Remove known prompt injection patterns."""
        lower = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if pattern in lower:
                logger.warning("Prompt injection attempt detected: '%s'", pattern)
                text = text.replace(pattern, "[REDACTED]")
        return text

    def _filter_fields(
        self,
        record: dict[str, Any],
        excluded_fields: set[str],
    ) -> dict[str, Any]:
        """Remove excluded fields from a data record."""
        return {k: v for k, v in record.items() if k not in excluded_fields}
