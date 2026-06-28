# iOSLENS MCP Server Reference

iOSLENS exposes a [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server on port 8001, allowing AI agents and LLM applications to interact with the governance platform via JSON-RPC 2.0.

## Protocol

Transport: HTTP/SSE (Server-Sent Events) or stdio
Protocol Version: MCP 2024-11-05
Endpoint: `http://localhost:8001/mcp`

---

## Tools

### `compliance_check`
Evaluate whether a proposed action complies with active governance policies.

**Input Schema**
```json
{
  "subject_id": "string",
  "action": "string",
  "resource_type": "string",
  "resource_id": "string",
  "purpose": "string",
  "context": {}
}
```

**Output**
```json
{
  "compliant": true,
  "decision": "PERMIT",
  "obligations": [],
  "explanation": "Access permitted under academic advising purpose."
}
```

---

### `enforce_policy`
Apply a named policy to a dataset and return filtered results.

**Input Schema**
```json
{
  "policy_id": "string",
  "dataset": [],
  "subject_context": {}
}
```

---

### `audit_query`
Query the audit ledger with chain verification.

**Input Schema**
```json
{
  "from": "ISO8601",
  "to": "ISO8601",
  "subject_id": "string | null",
  "verify_chain": true
}
```

---

### `udm_resolve`
Resolve UDM cross-domain mappings.

**Input Schema**
```json
{
  "code": "string",
  "code_type": "cip | soc | naics"
}
```

---

## Resources

### `policies://active`
Returns all active governance policies for the current tenant as a JSON document.

### `audit_logs://recent`
Returns the 100 most recent audit log entries.

### `udm://cip_codes`
Returns the full CIP code taxonomy.

### `udm://soc_codes`
Returns the full SOC code taxonomy.

---

## Prompts

### `governance_review`
Standard prompt for reviewing a data access decision with context.

**Arguments**
- `subject_name`: Display name of the requesting user
- `resource_description`: Human-readable description of the resource
- `decision`: PERMIT or DENY

---

## Authentication

MCP requests require a valid execution token passed in the `Authorization` header:

```
Authorization: ******
```

Execution tokens are short-lived (15 minutes) and scoped to a specific purpose. See [SECURITY.md](SECURITY.md) for token lifecycle details.

---

## Error Handling

MCP errors follow JSON-RPC 2.0 error format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {"detail": "RLS policy denied access"}
  }
}
```

| Code    | Meaning                  |
|---------|--------------------------|
| -32700  | Parse error              |
| -32600  | Invalid request          |
| -32601  | Method not found         |
| -32602  | Invalid params           |
| -32603  | Internal error           |
| -32001  | Unauthorized             |
| -32002  | Permission denied        |
