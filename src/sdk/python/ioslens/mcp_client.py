"""iOSLENS Python SDK — MCP client."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from ioslens.exceptions import IOSLensError

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for the iOSLENS MCP (JSON-RPC 2.0) server."""

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        token: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._request_id = 0
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> MCPClient:
        headers = {}
        if self._token:
            headers["Authorization"] = f"******"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self._timeout,
            headers=headers,
        )
        await self.initialize()
        return self

    async def __aexit__(self, *args) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("MCPClient not started. Use as async context manager.")
        return self._client

    async def _rpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            req["params"] = params

        r = await self._get_client().post("/", json=req)
        r.raise_for_status()
        body = r.json()

        if "error" in body:
            raise IOSLensError(f"MCP error {body['error']['code']}: {body['error']['message']}")
        return body.get("result")

    async def initialize(self) -> Dict[str, Any]:
        """Perform MCP handshake."""
        return await self._rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "ioslens-python-sdk", "version": "1.0.0"},
        })

    async def list_tools(self) -> List[Dict[str, Any]]:
        result = await self._rpc("tools/list")
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        result = await self._rpc("tools/call", {"name": name, "arguments": arguments})
        return result

    async def compliance_check(
        self,
        resource_type: str,
        purpose: str,
        user_id: str,
        tenant_id: str,
        resource_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call the compliance_check MCP tool."""
        args: Dict[str, Any] = {
            "resource_type": resource_type,
            "purpose": purpose,
            "user_id": user_id,
            "tenant_id": tenant_id,
        }
        if resource_id:
            args["resource_id"] = resource_id
        return await self.call_tool("compliance_check", args)

    async def udm_resolve(
        self,
        query: str,
        tenant_id: str,
        systems: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Call the udm_resolve MCP tool."""
        args: Dict[str, Any] = {"query": query, "tenant_id": tenant_id}
        if systems:
            args["systems"] = systems
        return await self.call_tool("udm_resolve", args)

    async def list_resources(self) -> List[Dict[str, Any]]:
        result = await self._rpc("resources/list")
        return result.get("resources", [])

    async def read_resource(self, uri: str) -> str:
        result = await self._rpc("resources/read", {"uri": uri})
        contents = result.get("contents", [])
        return contents[0]["text"] if contents else ""

    async def list_prompts(self) -> List[Dict[str, Any]]:
        result = await self._rpc("prompts/list")
        return result.get("prompts", [])

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
        result = await self._rpc("prompts/get", {"name": name, "arguments": arguments or {}})
        return result.get("messages", [])
