# iOSLENS.ai — REST API Specification

Base URL: `https://api.ioslens.ai/api/v1`

All endpoints require a valid ****** in the `Authorization` header.

## Authentication

```
Authorization: ******
```

JWTs are issued by the Ethos/OIDC provider and must contain:
- `sub`: user identifier
- `tenant_id`: institution tenant
- `roles`: array of role strings
- `exp`: expiry timestamp

---

## Health

### `GET /health`

Returns service health status. No authentication required.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## Governance

### `POST /governance/check`

Evaluate a governance policy against a data access request.

**Request:**
```json
{
  "resource_type": "student_record",
  "resource_id": "uuid",
  "purpose": "academic_advising",
  "action": "read"
}
```

**Response 200:**
```json
{
  "allowed": true,
  "policy_id": "uuid",
  "rationale": "Role ADVISOR + purpose ACADEMIC_ADVISING grants read access",
  "execution_token": "et_...",
  "expires_at": "2025-01-01T01:00:00Z"
}
```

**Response 403:**
```json
{
  "allowed": false,
  "reason": "Insufficient clearance for resource",
  "policy_id": "uuid"
}
```

### `GET /governance/policies`

List applicable governance policies for the current tenant.

**Query parameters:**
- `resource_type` (optional): filter by resource type
- `role` (optional): filter by role
- `page` (default: 1), `page_size` (default: 20)

---

## Audit

### `GET /audit/logs`

Retrieve audit log entries for the current tenant.

**Query parameters:**
- `start` (ISO 8601): start timestamp
- `end` (ISO 8601): end timestamp
- `user_id` (optional): filter by user
- `action` (optional): filter by action type
- `page`, `page_size`

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "tenant_id": "uuid",
      "user_id": "uuid",
      "resource_type": "student_record",
      "resource_id": "uuid",
      "action": "read",
      "purpose": "academic_advising",
      "timestamp": "2025-01-01T00:00:00Z",
      "chain_hash": "sha256hex"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### `GET /audit/verify`

Verify audit chain integrity for the current tenant.

**Response 200:**
```json
{
  "valid": true,
  "records_checked": 1000,
  "last_hash": "sha256hex"
}
```

---

## UDM (Universal Decoding Matrix)

### `POST /udm/resolve`

Resolve an entity across classification systems.

**Request:**
```json
{
  "query": "computer science",
  "systems": ["CIP", "SOC", "NAICS"],
  "limit": 10
}
```

**Response 200:**
```json
{
  "results": [
    {
      "system": "CIP",
      "code": "11.0101",
      "title": "Computer and Information Sciences, General",
      "score": 0.97
    },
    {
      "system": "SOC",
      "code": "15-1252",
      "title": "Software Developers",
      "score": 0.91
    }
  ]
}
```

### `GET /udm/crosswalk`

Get crosswalk mappings between classification systems.

**Query parameters:**
- `from_system`: source classification (CIP, SOC, NAICS)
- `from_code`: source code
- `to_system`: target classification

---

## Tenants

### `GET /tenants/me`

Get current tenant details (admin only).

**Response 200:**
```json
{
  "id": "uuid",
  "name": "State University",
  "domain": "stateuniversity.edu",
  "tier": "enterprise",
  "features": ["udm", "audit", "mcp"],
  "created_at": "2025-01-01T00:00:00Z"
}
```

### `GET /tenants/users`

List users in the current tenant (admin only).

---

## Error Responses

All errors follow RFC 7807 Problem Details:

```json
{
  "type": "https://api.ioslens.ai/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "JWT token has expired",
  "instance": "/api/v1/governance/check"
}
```

Standard status codes:
- `400` Bad Request — invalid input
- `401` Unauthorized — missing or invalid JWT
- `403` Forbidden — insufficient permissions (RLS/policy denial)
- `404` Not Found
- `422` Unprocessable Entity — validation error
- `429` Too Many Requests — rate limit exceeded
- `500` Internal Server Error
