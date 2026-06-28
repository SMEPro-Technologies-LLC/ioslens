"""iOSLENS MCP client implementation."""

from __future__ import annotations

import json
import uuid
from typing import Any

import httpx


class MCPClient:
    """Client for the iOSLENS MCP server (JSON-RPC 2.0)."""

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        api_key: str = "",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "MCPClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": "Bearer " + self._api_key},
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client:
            await self._client.aclose()

    async def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a JSON-RPC 2.0 call to the MCP server."""
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }
        assert self._client is not None, "Use async context manager"
        response = await self._client.post("/mcp", json=payload)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise RuntimeError(
                f"MCP error {data['error']['code']}: {data['error']['message']}"
            )
        return data.get("result")

    async def initialize(self) -> dict:
        """Initialize the MCP session."""
        return await self.call("initialize", {"protocolVersion": "2024-11-05"})

    async def list_tools(self) -> list[dict]:
        """List available MCP tools."""
        result = await self.call("tools/list")
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool by name."""
        return await self.call("tools/call", {"name": name, "arguments": arguments})

    async def compliance_check(
        self,
        subject_id: str,
        action: str,
        resource_type: str,
        purpose: str = "",
    ) -> dict:
        """Call the compliance_check MCP tool."""
        return await self.call_tool(
            "compliance_check",
            {
                "subject_id": subject_id,
                "action": action,
                "resource_type": resource_type,
                "purpose": purpose,
            },
        )
