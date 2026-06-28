# iOSLENS PostgreSQL Schema Reference

## Overview

iOSLENS uses PostgreSQL 16 with the `pgvector` extension for semantic search and HNSW indexing.

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";
```

## Core Tables

### `tenants`
Multi-tenant root table. Every other table references `tenant_id`.

```sql
CREATE TABLE tenants (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    domain      TEXT UNIQUE NOT NULL,
    config      JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `users`
Application users scoped to a tenant.

```sql
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    email       TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'viewer',
    clearance   INTEGER NOT NULL DEFAULT 1,
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `udm_mappings`
Universal Decoding Matrix cross-domain code mappings.

```sql
CREATE TABLE udm_mappings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cip_code        TEXT,
    soc_code        TEXT,
    naics_code      TEXT,
    label           TEXT NOT NULL,
    embedding       halfvec(1536),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `audit_ledger`
Chained-hash immutable audit trail.

```sql
CREATE TABLE audit_ledger (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    sequence_no     BIGINT NOT NULL,
    prev_hash       TEXT NOT NULL,
    event_hash      TEXT NOT NULL,
    subject_id      UUID,
    action          TEXT NOT NULL,
    resource_type   TEXT NOT NULL,
    resource_id     UUID,
    decision        TEXT NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Indexing Strategy

### B-tree indexes
- All foreign keys (`tenant_id`, `user_id`, etc.)
- `audit_ledger.sequence_no` for chain traversal
- `udm_mappings.cip_code`, `soc_code`, `naics_code`

### HNSW indexes (pgvector)
```sql
CREATE INDEX ON udm_mappings USING hnsw (embedding halfvec_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Partial indexes
```sql
CREATE INDEX ON audit_ledger (tenant_id, created_at DESC)
    WHERE created_at > now() - INTERVAL '90 days';
```

## Row-Level Security

RLS is enabled on all tenant-scoped tables:

```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE udm_mappings ENABLE ROW LEVEL SECURITY;
```

See `database/migrations/003_rls_policies.sql` for the full policy set.

## pgvector Configuration

- Vector dimensions: 1536 (OpenAI `text-embedding-3-small`)
- Storage type: `halfvec` (half-precision float, 50% storage reduction)
- Distance metric: cosine similarity
- HNSW parameters: `m=16`, `ef_construction=64`, `ef_search=40`

## Migration Sequence

| File                          | Description                          |
|-------------------------------|--------------------------------------|
| `001_init_schema.sql`         | Core tables and extensions           |
| `002_pgvector_setup.sql`      | Vector extension and HNSW indexes    |
| `003_rls_policies.sql`        | Row-level security policies          |
| `004_udm_seed.sql`            | UDM reference data loading           |
| `005_audit_ledger.sql`        | Audit chain functions and triggers   |
| `006_token_verification.sql`  | Execution token session functions    |
