# iOSLENS REST API Reference

Base URL: `https://api.ioslens.ai/v1`

Authentication: ****** or execution token in `Authorization` header.

---

## Health

### `GET /health`
Returns service health status.

**Response 200**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

---

## Governance

### `POST /v1/governance/evaluate`
Evaluate a data access request against governance policies.

**Request Body**
```json
{
  "subject_id": "user-uuid",
  "resource_type": "student_record",
  "resource_id": "record-uuid",
  "action": "read",
  "purpose": "academic_advising"
}
```

**Response 200**
```json
{
  "decision": "PERMIT",
  "obligations": [],
  "filtered_fields": [],
  "audit_id": "audit-uuid"
}
```

### `GET /v1/governance/policies`
List active governance policies for the current tenant.

---

## Audit

### `GET /v1/audit/logs`
Retrieve audit log entries with chain verification.

**Query Parameters**
- `from` (ISO 8601 datetime)
- `to` (ISO 8601 datetime)
- `subject_id` (optional)
- `resource_type` (optional)
- `page` (default: 1)
- `per_page` (default: 50, max: 200)

**Response 200**
```json
{
  "entries": [
    {
      "id": "uuid",
      "timestamp": "2024-01-01T00:00:00Z",
      "subject_id": "user-uuid",
      "action": "read",
      "resource_type": "student_record",
      "resource_id": "record-uuid",
      "decision": "PERMIT",
      "hash": "sha256-hex",
      "prev_hash": "sha256-hex"
    }
  ],
  "chain_valid": true,
  "total": 100,
  "page": 1
}
```

### `GET /v1/audit/verify`
Verify audit chain integrity for a time range.

---

## UDM (Universal Decoding Matrix)

### `GET /v1/udm/resolve`
Resolve cross-domain mappings between CIP, SOC, and NAICS codes.

**Query Parameters**
- `cip_code` (optional)
- `soc_code` (optional)
- `naics_code` (optional)

**Response 200**
```json
{
  "cip_code": "11.0701",
  "cip_title": "Computer Science",
  "soc_mappings": [
    {"code": "15-1252", "title": "Software Developers"}
  ],
  "naics_mappings": [
    {"code": "541511", "title": "Custom Computer Programming Services"}
  ]
}
```

### `POST /v1/udm/search`
Semantic search across UDM using vector embeddings.

---

## Tenants

### `GET /v1/tenants/me`
Get current tenant information.

### `PUT /v1/tenants/me`
Update current tenant configuration.

### `GET /v1/tenants/me/users`
List users in the current tenant (admin only).

---

## Error Responses

All errors return a standard envelope:

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Insufficient clearance for requested resource.",
    "request_id": "req-uuid"
  }
}
```

| HTTP Code | Error Code           | Description                        |
|-----------|----------------------|------------------------------------|
| 400       | INVALID_REQUEST      | Malformed request body             |
| 401       | UNAUTHORIZED         | Missing or invalid token           |
| 403       | PERMISSION_DENIED    | RLS or policy denial               |
| 404       | NOT_FOUND            | Resource does not exist            |
| 422       | VALIDATION_ERROR     | Input validation failure           |
| 429       | RATE_LIMITED         | Token bucket exhausted             |
| 500       | INTERNAL_ERROR       | Unexpected server error            |
