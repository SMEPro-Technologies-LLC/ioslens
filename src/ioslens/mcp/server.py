"""MCP Server — JSON-RPC 2.0 server implementing the Model Context Protocol."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from ioslens.config import get_settings
from ioslens.mcp.prompts import get_prompt
from ioslens.mcp.resources import get_resource
from ioslens.mcp.tools import TOOLS, dispatch_tool

logger = logging.getLogger(__name__)

MCP_VERSION = "2024-11-05"
SERVER_NAME = "ioslens-mcp"
SERVER_VERSION = "1.0.0"


class MCPServer:
    """Minimal MCP server implementing core JSON-RPC 2.0 methods.

    Supported methods:
      - initialize
      - tools/list
      - tools/call
      - resources/list
      - resources/read
      - prompts/list
      - prompts/get
    """

    async def handle(self, raw: str) -> str:
        """Handle a raw JSON-RPC 2.0 request string and return response string."""
        try:
            request = json.loads(raw)
        except json.JSONDecodeError:
            return self._error(None, -32700, "Parse error")

        request_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        try:
            result = await self._dispatch(method, params)
            return json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result})
        except ValueError as exc:
            return self._error(request_id, -32602, str(exc))
        except NotImplementedError:
            return self._error(request_id, -32601, f"Method not found: {method}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("MCP internal error for method=%s", method)
            return self._error(request_id, -32603, "Internal error", str(exc))

    async def _dispatch(self, method: str, params: dict[str, Any]) -> Any:
        """Route a JSON-RPC method call to the appropriate handler."""
        if method == "initialize":
            return self._initialize(params)
        if method == "tools/list":
            return {"tools": TOOLS}
        if method == "tools/call":
            return await dispatch_tool(params.get("name", ""), params.get("arguments", {}))
        if method == "resources/list":
            from ioslens.mcp.resources import RESOURCES

            return {"resources": RESOURCES}
        if method == "resources/read":
            return await get_resource(params.get("uri", ""))
        if method == "prompts/list":
            from ioslens.mcp.prompts import PROMPTS

            return {"prompts": PROMPTS}
        if method == "prompts/get":
            return await get_prompt(
                params.get("name", ""),
                params.get("arguments", {}),
            )
        raise NotImplementedError(method)

    def _initialize(self, params: dict) -> dict:
        return {
            "protocolVersion": MCP_VERSION,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "prompts": {"listChanged": False},
            },
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
            },
        }

    def _error(
        self,
        request_id: Any,
        code: int,
        message: str,
        data: str | None = None,
    ) -> str:
        error: dict[str, Any] = {"code": code, "message": message}
        if data:
            error["data"] = data
        return json.dumps({"jsonrpc": "2.0", "id": request_id, "error": error})


async def main() -> None:
    """Run the MCP server as a stdio process (stdio transport)."""
    settings = get_settings()
    server = MCPServer()
    logger.info("iOSLENS MCP server starting (port=%d)", settings.mcp_port)

    # Read JSON-RPC requests from stdin line by line
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    transport, _ = await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    try:
        async for line in reader:
            line_str = line.decode().strip()
            if line_str:
                response = await server.handle(line_str)
                print(response, flush=True)
    finally:
        transport.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
