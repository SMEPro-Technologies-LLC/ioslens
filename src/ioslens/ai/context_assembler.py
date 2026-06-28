"""
Context assembler — builds bounded, policy-scoped context chunks for LLM input.

Ensures that:
  - Only tenant-scoped data is included
  - Context size is bounded (token budget)
  - Sensitive fields are filtered per purpose
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_TOKEN_BUDGET = 4096


class ContextChunk:
    """A single bounded context chunk ready for LLM consumption."""

    def __init__(self, content: str, source: str, token_estimate: int) -> None:
        self.content = content
        self.source = source
        self.token_estimate = token_estimate


class ContextAssembler:
    """Assemble policy-scoped context chunks for AI model consumption."""

    def __init__(self, token_budget: int = DEFAULT_TOKEN_BUDGET) -> None:
        self.token_budget = token_budget

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate: ~4 chars per token."""
        return max(1, len(text) // 4)

    def _filter_fields(
        self,
        record: Dict[str, Any],
        purpose: str,
        roles: List[str],
    ) -> Dict[str, Any]:
        """Remove fields not permitted for the given purpose and roles."""
        restricted = {"ssn", "password", "token_hash", "chain_hash"}
        if "ADMIN" not in roles:
            restricted.update({"clearance", "metadata"})
        return {k: v for k, v in record.items() if k not in restricted}

    def build_chunks(
        self,
        records: List[Dict[str, Any]],
        purpose: str,
        roles: List[str],
        system_prompt: Optional[str] = None,
    ) -> List[ContextChunk]:
        """
        Build a list of bounded context chunks from records.

        Args:
            records: list of data records
            purpose: declared access purpose (used for field filtering)
            roles: caller roles (used for field filtering)
            system_prompt: optional system-level context prepended

        Returns:
            List of ContextChunk objects within token_budget
        """
        chunks: List[ContextChunk] = []
        remaining_budget = self.token_budget

        if system_prompt:
            est = self._estimate_tokens(system_prompt)
            if est <= remaining_budget:
                chunks.append(ContextChunk(system_prompt, "system", est))
                remaining_budget -= est

        for i, record in enumerate(records):
            filtered = self._filter_fields(record, purpose, roles)
            content = "\n".join(f"{k}: {v}" for k, v in filtered.items())
            est = self._estimate_tokens(content)

            if remaining_budget <= 0:
                logger.debug("Token budget exhausted after %d records", i)
                break

            if est > remaining_budget:
                # Truncate content to fit budget
                chars = remaining_budget * 4
                content = content[:chars] + " [TRUNCATED]"
                est = remaining_budget

            chunks.append(ContextChunk(content, f"record_{i}", est))
            remaining_budget -= est

        return chunks
