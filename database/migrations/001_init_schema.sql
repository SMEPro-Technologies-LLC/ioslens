-- 001_init_schema.sql
-- Core tables: tenants, users, udm, audit

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tenants
CREATE TABLE IF NOT EXISTS tenants (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    domain      TEXT UNIQUE NOT NULL,
    config      JSONB NOT NULL DEFAULT '{}',
    active      BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email       TEXT NOT NULL,
    display_name TEXT,
    role        TEXT NOT NULL DEFAULT 'viewer'
                CHECK (role IN ('admin', 'manager', 'analyst', 'viewer')),
    clearance   INTEGER NOT NULL DEFAULT 1 CHECK (clearance BETWEEN 1 AND 4),
    metadata    JSONB NOT NULL DEFAULT '{}',
    active      BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, email)
);

-- UDM mappings (CIP/SOC/NAICS cross-domain)
CREATE TABLE IF NOT EXISTS udm_mappings (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cip_code    TEXT,
    soc_code    TEXT,
    naics_code  TEXT,
    label       TEXT NOT NULL,
    description TEXT,
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Governance policies
CREATE TABLE IF NOT EXISTS governance_policies (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    allowed_roles TEXT[] NOT NULL DEFAULT '{}',
    min_clearance INTEGER NOT NULL DEFAULT 1,
    allowed_purposes TEXT[] NOT NULL DEFAULT '{}',
    effect      TEXT NOT NULL DEFAULT 'PERMIT' CHECK (effect IN ('PERMIT', 'DENY')),
    active      BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audit ledger (chained-hash, append-only)
CREATE TABLE IF NOT EXISTS audit_ledger (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    sequence_no BIGINT NOT NULL,
    prev_hash   TEXT NOT NULL DEFAULT 'GENESIS',
    event_hash  TEXT NOT NULL,
    subject_id  UUID,
    action      TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID,
    decision    TEXT NOT NULL CHECK (decision IN ('PERMIT', 'DENY', 'FILTER')),
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Execution tokens
CREATE TABLE IF NOT EXISTS execution_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jti         TEXT UNIQUE NOT NULL,
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    subject_id  UUID NOT NULL,
    purpose     TEXT NOT NULL,
    issued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked     BOOLEAN NOT NULL DEFAULT false,
    revoked_at  TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_tenant ON users (tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_time ON audit_ledger (tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_sequence ON audit_ledger (tenant_id, sequence_no);
CREATE INDEX IF NOT EXISTS idx_policies_tenant ON governance_policies (tenant_id);
CREATE INDEX IF NOT EXISTS idx_tokens_jti ON execution_tokens (jti);
CREATE INDEX IF NOT EXISTS idx_tokens_expires ON execution_tokens (expires_at) WHERE revoked = false;
CREATE INDEX IF NOT EXISTS idx_udm_cip ON udm_mappings (cip_code) WHERE cip_code IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_udm_soc ON udm_mappings (soc_code) WHERE soc_code IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_udm_naics ON udm_mappings (naics_code) WHERE naics_code IS NOT NULL;
