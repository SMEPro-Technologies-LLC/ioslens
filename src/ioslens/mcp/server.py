"""
iOSLENS MCP Server — JSON-RPC 2.0 over HTTP.

Implements the Model Context Protocol spec (2024-11-05) exposing:
  - Tools:     compliance_check, enforce_policy, udm_resolve
  - Resources: policies, audit_logs
  - Prompts:   compliance_review, policy_explanation

Run with:
    python -m ioslens.mcp.server
    uvicorn ioslens.mcp.server:app --port 8001
"""

from __future__ import annotations

import logging
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ioslens.config import get_settings
from ioslens.mcp.tools import TOOL_REGISTRY, dispatch_tool
from ioslens.mcp.resources import get_resource
from ioslens.mcp.prompts import get_prompt, list_prompts, list_resources, list_tools

logger = logging.getLogger(__name__)
settings = get_settings()

SERVER_INFO = {
    "name": "ioslens-mcp",
    "version": settings.version,
}

PROTOCOL_VERSION = "2024-11-05"
CAPABILITIES = {
    "tools": {},
    "resources": {},
    "prompts": {},
}

app = FastAPI(
    title="iOSLENS MCP Server",
    description="Model Context Protocol server for iOSLENS.ai",
    version=settings.version,
    docs_url=None,
)


def _error(id, code: int, message: str, data=None) -> dict:
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": id, "error": err}


def _ok(id, result) -> dict:
    return {"jsonrpc": "2.0", "id": id, "result": result}


async def _handle_request(body: dict) -> dict:
    req_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params", {})

    if body.get("jsonrpc") != "2.0":
        return _error(req_id, -32600, "Invalid JSON-RPC version")

    # ── Lifecycle ────────────────────────────────────────────────────────────

    if method == "initialize":
        client_version = params.get("protocolVersion", PROTOCOL_VERSION)
        return _ok(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": CAPABILITIES,
            "serverInfo": SERVER_INFO,
        })

    if method == "notifications/initialized":
        return _ok(req_id, {})

    # ── Tools ────────────────────────────────────────────────────────────────

    if method == "tools/list":
        return _ok(req_id, {"tools": list_tools()})

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        if not tool_name:
            return _error(req_id, -32602, "Missing tool name")
        try:
            result = await dispatch_tool(tool_name, arguments)
            return _ok(req_id, {"content": [{"type": "text", "text": str(result)}]})
        except KeyError:
            return _error(req_id, -32601, f"Unknown tool: {tool_name!r}")
        except PermissionError:
            return _error(req_id, -32002, "Permission denied")
        except Exception as e:
            logger.exception("Tool %r raised unexpected error", tool_name)
            return _error(req_id, -32603, "Internal tool error")

    # ── Resources ────────────────────────────────────────────────────────────

    if method == "resources/list":
        return _ok(req_id, {"resources": list_resources()})

    if method == "resources/read":
        uri = params.get("uri", "")
        try:
            content = await get_resource(uri)
            return _ok(req_id, {"contents": [{"uri": uri, "text": content}]})
        except KeyError:
            return _error(req_id, -32601, f"Unknown resource: {uri!r}")
        except Exception:
            logger.exception("Resource read error: %s", uri)
            return _error(req_id, -32603, "Internal resource error")

    # ── Prompts ──────────────────────────────────────────────────────────────

    if method == "prompts/list":
        return _ok(req_id, {"prompts": list_prompts()})

    if method == "prompts/get":
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            messages = get_prompt(prompt_name, arguments)
            return _ok(req_id, {"messages": messages})
        except KeyError:
            return _error(req_id, -32601, f"Unknown prompt: {prompt_name!r}")

    return _error(req_id, -32601, f"Method not found: {method!r}")


@app.post("/")
@app.post("/mcp")
async def mcp_endpoint(request: Request) -> JSONResponse:
    """Main JSON-RPC 2.0 endpoint."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            _error(None, -32700, "Parse error"),
            status_code=200,
        )

    # Handle batch requests
    if isinstance(body, list):
        results = [await _handle_request(item) for item in body]
        return JSONResponse(results)

    result = await _handle_request(body)
    return JSONResponse(result)


@app.get("/health")
async def health():
    """MCP server health check."""
    return {"status": "healthy", "server": SERVER_INFO["name"], "version": SERVER_INFO["version"]}


def main():
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "ioslens.mcp.server:app",
        host=settings.mcp_host,
        port=settings.mcp_port,
        reload=settings.is_development,
    )


if __name__ == "__main__":
    main()
