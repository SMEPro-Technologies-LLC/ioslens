-- 001_init_schema.sql
-- Core tables: tenants, users, governance_policies, execution_tokens
-- Run as superuser or database owner

BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ── Tenants ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS tenants (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL,
    domain      TEXT NOT NULL UNIQUE,
    tier        TEXT NOT NULL DEFAULT 'standard'
                    CHECK (tier IN ('free', 'standard', 'enterprise')),
    features    JSONB NOT NULL DEFAULT '[]',
    settings    JSONB NOT NULL DEFAULT '{}',
    active      BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Users ────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    external_id TEXT NOT NULL,
    email       TEXT NOT NULL,
    display_name TEXT,
    roles       TEXT[] NOT NULL DEFAULT '{}',
    clearance   INT NOT NULL DEFAULT 0,
    metadata    JSONB NOT NULL DEFAULT '{}',
    active      BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, external_id),
    UNIQUE (tenant_id, email)
);

-- ── Governance Policies ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS governance_policies (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id        UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name             TEXT NOT NULL,
    resource_type    TEXT NOT NULL,
    allowed_roles    TEXT[] NOT NULL DEFAULT '{}',
    allowed_purposes TEXT[] NOT NULL DEFAULT '{}',
    min_clearance    INT NOT NULL DEFAULT 0,
    conditions       JSONB NOT NULL DEFAULT '{}',
    active           BOOLEAN NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, name)
);

-- ── Execution Tokens ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS execution_tokens (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id     UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource_type TEXT NOT NULL,
    resource_id   UUID,
    purpose       TEXT NOT NULL,
    state         TEXT NOT NULL DEFAULT 'DESIGNED'
                      CHECK (state IN ('DESIGNED', 'ISSUED', 'CONSUMED', 'EXPIRED')),
    token_hash    TEXT NOT NULL UNIQUE,
    expires_at    TIMESTAMPTZ NOT NULL,
    consumed_at   TIMESTAMPTZ,
    policy_id     UUID REFERENCES governance_policies(id),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_users_tenant_id     ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email         ON users(email);
CREATE INDEX IF NOT EXISTS idx_policies_tenant_id  ON governance_policies(tenant_id);
CREATE INDEX IF NOT EXISTS idx_policies_resource   ON governance_policies(tenant_id, resource_type);
CREATE INDEX IF NOT EXISTS idx_tokens_hash         ON execution_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_tokens_user         ON execution_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_tokens_state        ON execution_tokens(state)
    WHERE state IN ('DESIGNED', 'ISSUED');
CREATE INDEX IF NOT EXISTS idx_tokens_expires      ON execution_tokens(expires_at)
    WHERE state IN ('DESIGNED', 'ISSUED');

-- ── Update trigger helper ─────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER policies_updated_at
    BEFORE UPDATE ON governance_policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

COMMIT;
