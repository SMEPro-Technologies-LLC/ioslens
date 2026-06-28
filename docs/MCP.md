# iOSLENS.ai — MCP Server Specification

## Overview

iOSLENS exposes a **Model Context Protocol (MCP)** server implementing JSON-RPC 2.0. This allows AI assistants and MCP-compatible clients to interact with iOSLENS governance, audit, and UDM capabilities in a structured, policy-enforced way.

MCP endpoint: `http://localhost:8001` (local dev) / `https://mcp.ioslens.ai` (production)

## Protocol

The MCP server speaks **JSON-RPC 2.0** over HTTP POST to `/` (or `/mcp`).

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "compliance_check",
    "arguments": { ... }
  }
}
```

## Initialization

### `initialize`

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": { "name": "my-client", "version": "1.0" }
  }
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    },
    "serverInfo": { "name": "ioslens-mcp", "version": "1.0.0" }
  }
}
```

## Tools

### `tools/list`

Returns the list of available tools.

### `compliance_check`

Check whether a proposed data access is compliant.

**Arguments:**
```json
{
  "resource_type": "student_record",
  "resource_id": "uuid",
  "purpose": "academic_advising",
  "user_id": "uuid",
  "tenant_id": "uuid"
}
```

**Result:**
```json
{
  "compliant": true,
  "policy_applied": "FERPA_ADVISOR_READ",
  "rationale": "...",
  "execution_token": "et_..."
}
```

### `enforce_policy`

Execute a governance policy decision and write to the audit ledger.

**Arguments:**
```json
{
  "execution_token": "et_...",
  "action": "read",
  "resource_type": "student_record",
  "resource_id": "uuid"
}
```

**Result:**
```json
{
  "enforced": true,
  "audit_id": "uuid",
  "chain_hash": "sha256hex"
}
```

### `udm_resolve`

Resolve a query through the Universal Decoding Matrix.

**Arguments:**
```json
{
  "query": "nursing informatics",
  "systems": ["CIP", "SOC"],
  "tenant_id": "uuid"
}
```

## Resources

### `resources/list`

Returns available resources.

### `policies`

URI: `ioslens://policies/{tenant_id}`

Returns the active governance policy set for a tenant as structured JSON.

### `audit_logs`

URI: `ioslens://audit/{tenant_id}?start=...&end=...`

Returns recent audit log entries for the tenant.

## Prompts

### `prompts/list`

Returns available prompt templates.

### `compliance_review`

A standard prompt template for reviewing compliance posture:

```
Review the compliance status for tenant {{tenant_id}} covering the period {{start}} to {{end}}.
Focus on: {{focus_areas}}
```

### `policy_explanation`

A standard prompt for explaining a specific policy to end users.

## Authentication

MCP requests must include a valid ******

```
Authorization: ******
```

The JWT must contain `tenant_id` and appropriate `roles`.

## Error Codes

| Code  | Meaning                          |
|-------|----------------------------------|
| -32700 | Parse error                     |
| -32600 | Invalid request                  |
| -32601 | Method not found                 |
| -32602 | Invalid params                   |
| -32603 | Internal error                   |
| -32001 | Authentication required          |
| -32002 | Insufficient permissions         |
| -32003 | Execution token expired/invalid  |
| -32004 | RLS policy denied                |
