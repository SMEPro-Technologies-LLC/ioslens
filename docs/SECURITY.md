# iOSLENS.ai — Security Model

## Threat Model

iOSLENS handles sensitive institutional data including student records, employment data, and financial classifications. The threat model addresses:

1. **Unauthorized data access** — mitigated by PostgreSQL RLS + execution token validation
2. **Cross-tenant data leakage** — mitigated by tenant-scoped RLS policies on every table
3. **Token replay attacks** — mitigated by Redis-backed nonce store and token expiry
4. **Audit log tampering** — mitigated by chained SHA-256 hash ledger
5. **Privilege escalation** — mitigated by RESTRICTIVE RLS policies (cannot be bypassed by row ownership)
6. **LLM context injection** — mitigated by bounded context assembly and purpose-scoped prompts

---

## Identity & Access: Ethos/Banner Seam

**Ethos grants application-level access.** Banner is the authoritative ERP source.

```
[User Browser] → [Ethos SAML/OIDC] → [JWT issued] → [iOSLENS API]
                                                          ↓
                                              [JWT validation (Layer 2)]
                                                          ↓
                                              [UDM + RLS scoping (Layer 3/5)]
                                                          ↓
                                              [Data returned — tenant-scoped]
```

**Critical**: Ethos authenticates *who*. iOSLENS enforces *what they can see* independently, using its own UDM filtering and PostgreSQL RLS. No data access decision is delegated back to Ethos/Banner.

---

## Row-Level Security (RLS)

All tenant-data tables have RLS enabled with `SECURITY INVOKER` and `RESTRICTIVE` policies.

### Policy Pattern

```sql
-- Every table follows this pattern:
ALTER TABLE tablename ENABLE ROW LEVEL SECURITY;
ALTER TABLE tablename FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON tablename
  AS RESTRICTIVE
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

`RESTRICTIVE` policies cannot be bypassed even by the table owner. All rows not matching the current tenant's ID are invisible.

### Setting the Tenant Context

Before every query, the application sets:

```sql
SET LOCAL app.tenant_id = '<tenant-uuid>';
SET LOCAL app.user_id = '<user-uuid>';
SET LOCAL app.roles = '<role1,role2>';
```

This is done in the connection pool checkout callback.

### Role-Based Policies

Some tables have additional role-based RLS:

```sql
CREATE POLICY role_scoped_read ON student_records
  AS RESTRICTIVE
  FOR SELECT
  USING (
    'ADVISOR' = ANY(string_to_array(current_setting('app.roles'), ','))
    OR 'ADMIN' = ANY(string_to_array(current_setting('app.roles'), ','))
  );
```

---

## Execution Token Flow

Execution tokens are short-lived, single-use authorization tokens for governed write operations.

```
1. Client calls POST /governance/check with resource + purpose
2. Policy engine evaluates; if allowed, issues execution token (JWT, 60s TTL)
3. Execution token stored in Redis (token_id → hash)
4. Client uses execution token in subsequent write request
5. token_service validates token: not expired, not replayed, tenant matches
6. Redis entry deleted (prevent replay)
7. Audit event written to ledger
```

Token format: `et_<base64url(tenant_id)>.<jwt_payload>.<signature>`

---

## Audit Ledger

The audit ledger uses a chained SHA-256 hash to ensure tamper evidence:

```
record[0]: hash = SHA256("genesis" || event_data_0)
record[1]: hash = SHA256(record[0].hash || event_data_1)
record[n]: hash = SHA256(record[n-1].hash || event_data_n)
```

Verification: re-compute the chain and compare to stored hashes. Any inserted or modified record breaks the chain.

---

## Secrets Management

- No secrets in source code
- All credentials via environment variables
- Production secrets via GCP Secret Manager / AWS Secrets Manager
- JWT private key injected as `JWT_PRIVATE_KEY` env var (PEM format)
- Database password via `POSTGRES_PASSWORD` env var
- Redis password via `REDIS_PASSWORD` env var (if set)

---

## Data Classification

| Data Type            | Classification | RLS Required | Audit Required |
|---------------------|----------------|--------------|----------------|
| Student records      | Confidential   | Yes          | Yes            |
| Employee records     | Confidential   | Yes          | Yes            |
| UDM reference data   | Internal       | No           | No             |
| Governance policies  | Internal       | Yes          | Yes            |
| Audit logs           | Restricted     | Yes          | N/A            |
| Tenant config        | Internal       | Yes          | Yes            |

---

## Compliance

- **FERPA**: Student education records access controlled by ADVISOR/ADMIN role policies
- **HIPAA**: Health-related records require PURPOSE=HEALTHCARE_OPERATIONS
- **SOC 2 Type II**: Audit trail provides evidence for availability and confidentiality controls
- **GDPR**: Tenant data isolation ensures no cross-tenant leakage
