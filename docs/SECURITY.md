# iOSLENS Security Documentation

## Threat Model

### Trust Boundaries
1. **External Clients** → API Gateway (L2): TLS 1.3 required, JWT/SAML validated
2. **API → Database (L5/L6)**: Parameterized queries only, RLS enforced
3. **MCP Clients → MCP Server**: Execution token required, purpose-scoped
4. **Tenant Isolation**: Row-level security enforces strict tenant boundaries

### Key Threats and Mitigations

| Threat                     | Mitigation                                                  |
|----------------------------|-------------------------------------------------------------|
| SQL Injection              | SQLAlchemy ORM + parameterized asyncpg queries              |
| Horizontal Privilege Esc.  | RLS `RESTRICTIVE` policies on all tenant tables             |
| Token Replay               | Redis replay store with token JTI tracking                  |
| Audit Tampering            | Chained SHA-256 hashes on audit ledger                      |
| LLM Prompt Injection       | Context sanitization in `context_assembler.py`              |
| Insecure Secrets           | All secrets via environment variables / Secret Manager      |
| CSRF                       | SameSite cookies + CORS origin validation                   |
| Enumeration                | Resource IDs are UUIDs, not sequential integers             |

---

## Row-Level Security (RLS)

All tenant-scoped tables use `SECURITY INVOKER RESTRICTIVE` policies:

```sql
CREATE POLICY tenant_isolation ON students
  AS RESTRICTIVE
  FOR ALL
  TO ioslens_app
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

The application sets `app.tenant_id` at the start of each transaction via the database connection pool.

No row from tenant A is ever visible to tenant B.

---

## Execution Token Flow

1. Client authenticates via SAML/OIDC → receives JWT
2. JWT is validated by `auth_service.py`
3. Client requests an **execution token** for a specific purpose
4. Token service mints a short-lived (15 min) token with:
   - `sub`: user ID
   - `tenant_id`: tenant UUID
   - `purpose`: e.g., `academic_advising`
   - `jti`: unique token ID (stored in Redis for replay prevention)
5. Client passes execution token on each MCP/API call
6. Token is verified and JTI checked against Redis on each request
7. After 15 min (or explicit revocation), token is rejected

---

## Secrets Management

- **Development**: `.env` file (never committed, listed in `.gitignore`)
- **Staging / Production**: GCP Secret Manager or AWS Secrets Manager
- **Kubernetes**: Sealed Secrets or External Secrets Operator

Required environment variables:

```
DATABASE_URL          # postgres connection string
REDIS_URL             # redis connection string
JWT_SECRET            # HMAC secret for JWT signing
OPENAI_API_KEY        # (optional) OpenAI integration
ANTHROPIC_API_KEY     # (optional) Anthropic integration
SAML_CERT             # (optional) SAML IdP certificate
```

---

## Data Classification

| Level | Description                            | RLS Required |
|-------|----------------------------------------|--------------|
| L0    | Public / directory information         | No           |
| L1    | Internal / aggregate data              | Yes          |
| L2    | Sensitive / individual PII             | Yes          |
| L3    | Restricted / FERPA-protected records   | Yes + purpose|
| L4    | Regulated / HIPAA / financial          | Yes + purpose + MFA |

---

## Compliance References

- **FERPA**: Student education records protection
- **HIPAA**: Health information (if applicable)
- **SOC 2 Type II**: Access control, availability, confidentiality
- **NIST 800-53**: Federal security controls baseline
