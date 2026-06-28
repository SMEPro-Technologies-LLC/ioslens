"""Integration tests for MCP server protocol compliance."""

import json
import pytest
from ioslens.mcp.server import MCPServer


@pytest.fixture
def server() -> MCPServer:
    return MCPServer()


@pytest.mark.asyncio
async def test_initialize(server: MCPServer) -> None:
    """initialize method should return protocol version and capabilities."""
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
    })
    response_str = await server.handle(request)
    response = json.loads(response_str)

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    result = response["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert "capabilities" in result
    assert "serverInfo" in result


@pytest.mark.asyncio
async def test_tools_list(server: MCPServer) -> None:
    """tools/list should return a list of tools."""
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    })
    response = json.loads(await server.handle(request))
    assert "result" in response
    tools = response["result"]["tools"]
    assert isinstance(tools, list)
    tool_names = [t["name"] for t in tools]
    assert "compliance_check" in tool_names
    assert "enforce_policy" in tool_names


@pytest.mark.asyncio
async def test_tools_call_compliance_check(server: MCPServer) -> None:
    """tools/call compliance_check should return a decision."""
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "compliance_check",
            "arguments": {
                "subject_id": "user-1",
                "action": "read",
                "resource_type": "student_record",
                "purpose": "academic_advising",
            },
        },
    })
    response = json.loads(await server.handle(request))
    assert "result" in response


@pytest.mark.asyncio
async def test_resources_list(server: MCPServer) -> None:
    """resources/list should return a list of resources."""
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "resources/list",
        "params": {},
    })
    response = json.loads(await server.handle(request))
    assert "result" in response
    resources = response["result"]["resources"]
    assert isinstance(resources, list)
    assert len(resources) > 0


@pytest.mark.asyncio
async def test_unknown_method_returns_error(server: MCPServer) -> None:
    """Unknown methods should return -32601 error."""
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "nonexistent/method",
        "params": {},
    })
    response = json.loads(await server.handle(request))
    assert "error" in response
    assert response["error"]["code"] == -32601


@pytest.mark.asyncio
async def test_invalid_json_returns_parse_error(server: MCPServer) -> None:
    """Invalid JSON should return -32700 parse error."""
    response = json.loads(await server.handle("this is not json{"))
    assert "error" in response
    assert response["error"]["code"] == -32700
