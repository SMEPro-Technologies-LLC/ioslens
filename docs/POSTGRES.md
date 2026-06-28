# iOSLENS.ai — PostgreSQL Schema Design

## Overview

iOSLENS uses **PostgreSQL 16** with the `pgvector` extension for semantic similarity search. The schema is multi-tenant with Row-Level Security on all tenant-scoped tables.

---

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";      -- pgvector
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- fuzzy text search
```

---

## Core Tables

### `tenants`

```sql
CREATE TABLE tenants (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL,
    domain      TEXT NOT NULL UNIQUE,
    tier        TEXT NOT NULL DEFAULT 'standard',
    features    JSONB NOT NULL DEFAULT '[]',
    settings    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `users`

```sql
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    external_id TEXT NOT NULL,          -- Ethos/Banner identity
    email       TEXT NOT NULL,
    roles       TEXT[] NOT NULL DEFAULT '{}',
    clearance    INT NOT NULL DEFAULT 0,
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, external_id)
);
```

### `udm_entities`

Universal Decoding Matrix cross-domain entity table.

```sql
CREATE TABLE udm_entities (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system          TEXT NOT NULL,       -- CIP, SOC, NAICS
    code            TEXT NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT,
    parent_code     TEXT,
    embedding       halfvec(1536),       -- pgvector halfvec for OpenAI embeddings
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(system, code)
);
```

### `governance_policies`

```sql
CREATE TABLE governance_policies (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    resource_type   TEXT NOT NULL,
    allowed_roles   TEXT[] NOT NULL,
    allowed_purposes TEXT[] NOT NULL,
    conditions      JSONB NOT NULL DEFAULT '{}',
    active          BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `audit_ledger`

```sql
CREATE TABLE audit_ledger (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    user_id         UUID REFERENCES users(id),
    resource_type   TEXT NOT NULL,
    resource_id     UUID,
    action          TEXT NOT NULL,
    purpose         TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}',
    prev_hash       TEXT NOT NULL DEFAULT 'genesis',
    chain_hash      TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `execution_tokens`

```sql
CREATE TABLE execution_tokens (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    resource_type   TEXT NOT NULL,
    resource_id     UUID,
    purpose         TEXT NOT NULL,
    state           TEXT NOT NULL DEFAULT 'DESIGNED', -- DESIGNED → ISSUED → CONSUMED → EXPIRED
    token_hash      TEXT NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    consumed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## pgvector Configuration

### Index Type: HNSW

```sql
CREATE INDEX udm_entities_embedding_hnsw
  ON udm_entities
  USING hnsw (embedding halfvec_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

### Similarity Search

```sql
SELECT id, system, code, title,
       1 - (embedding <=> $1::halfvec) AS cosine_similarity
FROM udm_entities
WHERE system = ANY($2)
ORDER BY embedding <=> $1::halfvec
LIMIT $3;
```

---

## Indexing Strategy

```sql
-- Tenant isolation (used in RLS)
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_policies_tenant ON governance_policies(tenant_id);
CREATE INDEX idx_audit_tenant_time ON audit_ledger(tenant_id, created_at DESC);

-- UDM lookups
CREATE INDEX idx_udm_system_code ON udm_entities(system, code);
CREATE INDEX idx_udm_title_trgm ON udm_entities USING gin(title gin_trgm_ops);

-- Token lookups
CREATE INDEX idx_tokens_hash ON execution_tokens(token_hash);
CREATE INDEX idx_tokens_state ON execution_tokens(state) WHERE state IN ('DESIGNED', 'ISSUED');
```

---

## Connection Pool

The application uses `asyncpg` with a connection pool (min 5, max 20). On each checkout:

```python
async def _set_tenant_context(conn, tenant_id, user_id, roles):
    await conn.execute(
        "SET LOCAL app.tenant_id = $1; SET LOCAL app.user_id = $2; SET LOCAL app.roles = $3",
        str(tenant_id), str(user_id), ",".join(roles)
    )
```

---

## Migrations

Migrations are plain SQL files applied in order:

| Migration | Description |
|-----------|-------------|
| 001 | Core schema (tenants, users, policies, audit) |
| 002 | pgvector setup, UDM tables, HNSW index |
| 003 | RLS policies on all tenant-scoped tables |
| 004 | UDM seed data (CIP/SOC/NAICS reference) |
| 005 | Audit ledger functions and triggers |
| 006 | Execution token session functions |
