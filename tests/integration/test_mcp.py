"""Integration tests for MCP JSON-RPC 2.0 server."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from ioslens.mcp.server import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def mcp_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def _rpc(client, method, params=None, req_id=1):
    body = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params:
        body["params"] = params
    r = await client.post("/", json=body)
    return r.json()


@pytest.mark.anyio
async def test_health_endpoint(mcp_client):
    r = await mcp_client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.anyio
async def test_initialize(mcp_client):
    resp = await _rpc(mcp_client, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"},
    })
    assert "result" in resp
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert "serverInfo" in resp["result"]


@pytest.mark.anyio
async def test_tools_list(mcp_client):
    resp = await _rpc(mcp_client, "tools/list")
    assert "result" in resp
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "compliance_check" in tool_names
    assert "enforce_policy" in tool_names
    assert "udm_resolve" in tool_names


@pytest.mark.anyio
async def test_compliance_check_tool(mcp_client):
    resp = await _rpc(mcp_client, "tools/call", {
        "name": "compliance_check",
        "arguments": {
            "resource_type": "student_record",
            "purpose": "academic_advising",
            "user_id": "00000000-0000-0000-0000-000000000001",
            "tenant_id": "00000000-0000-0000-0000-000000000002",
        },
    })
    assert "result" in resp
    assert "content" in resp["result"]


@pytest.mark.anyio
async def test_udm_resolve_tool(mcp_client):
    resp = await _rpc(mcp_client, "tools/call", {
        "name": "udm_resolve",
        "arguments": {
            "query": "computer science",
            "tenant_id": "00000000-0000-0000-0000-000000000002",
        },
    })
    assert "result" in resp


@pytest.mark.anyio
async def test_resources_list(mcp_client):
    resp = await _rpc(mcp_client, "resources/list")
    assert "result" in resp
    resources = resp["result"]["resources"]
    assert any("policies" in r["uri"] for r in resources)


@pytest.mark.anyio
async def test_prompts_list(mcp_client):
    resp = await _rpc(mcp_client, "prompts/list")
    assert "result" in resp
    prompts = resp["result"]["prompts"]
    prompt_names = [p["name"] for p in prompts]
    assert "compliance_review" in prompt_names


@pytest.mark.anyio
async def test_prompts_get(mcp_client):
    resp = await _rpc(mcp_client, "prompts/get", {
        "name": "compliance_review",
        "arguments": {
            "tenant_id": "abc-123",
            "start": "2025-01-01",
            "end": "2025-01-31",
        },
    })
    assert "result" in resp
    messages = resp["result"]["messages"]
    assert len(messages) > 0
    assert "abc-123" in messages[0]["content"]


@pytest.mark.anyio
async def test_unknown_method_returns_error(mcp_client):
    resp = await _rpc(mcp_client, "nonexistent/method")
    assert "error" in resp
    assert resp["error"]["code"] == -32601


@pytest.mark.anyio
async def test_invalid_jsonrpc_version(mcp_client):
    r = await mcp_client.post("/", json={"jsonrpc": "1.0", "id": 1, "method": "tools/list"})
    body = r.json()
    assert "error" in body
