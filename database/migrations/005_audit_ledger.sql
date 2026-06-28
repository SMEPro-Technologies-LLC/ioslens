-- 005_audit_ledger.sql
-- Chained-hash audit ledger table and helper functions

BEGIN;

-- ── Audit Ledger Table ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS audit_ledger (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id     UUID NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    user_id       UUID REFERENCES users(id) ON DELETE SET NULL,
    resource_type TEXT NOT NULL,
    resource_id   UUID,
    action        TEXT NOT NULL,
    purpose       TEXT,
    outcome       TEXT NOT NULL DEFAULT 'success' CHECK (outcome IN ('success', 'denied', 'error')),
    metadata      JSONB NOT NULL DEFAULT '{}',
    ip_address    INET,
    user_agent    TEXT,
    prev_hash     TEXT NOT NULL DEFAULT 'genesis',
    chain_hash    TEXT NOT NULL,
    seq           BIGSERIAL NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Immutable: prevent updates and deletes
CREATE RULE audit_no_update AS ON UPDATE TO audit_ledger DO INSTEAD NOTHING;
CREATE RULE audit_no_delete AS ON DELETE TO audit_ledger DO INSTEAD NOTHING;

-- ── Indexes ───────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_audit_tenant_time
    ON audit_ledger(tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_user
    ON audit_ledger(user_id, created_at DESC)
    WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_audit_resource
    ON audit_ledger(tenant_id, resource_type, resource_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_seq
    ON audit_ledger(seq);

-- ── RLS on Audit Ledger ───────────────────────────────────────────────────────

ALTER TABLE audit_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_ledger FORCE ROW LEVEL SECURITY;

CREATE POLICY audit_tenant_isolation ON audit_ledger
    AS RESTRICTIVE
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY audit_read ON audit_ledger
    FOR SELECT
    USING (
        'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
        OR 'AUDITOR' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

CREATE POLICY audit_insert ON audit_ledger
    FOR INSERT WITH CHECK (
        tenant_id = current_setting('app.tenant_id', true)::uuid
    );

-- ── Chain Hash Function ───────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION compute_audit_chain_hash(
    p_prev_hash TEXT,
    p_id UUID,
    p_tenant_id UUID,
    p_user_id UUID,
    p_resource_type TEXT,
    p_action TEXT,
    p_created_at TIMESTAMPTZ
) RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_data TEXT;
BEGIN
    v_data := p_prev_hash
        || '|' || p_id::text
        || '|' || p_tenant_id::text
        || '|' || COALESCE(p_user_id::text, 'null')
        || '|' || p_resource_type
        || '|' || p_action
        || '|' || p_created_at::text;
    RETURN encode(digest(v_data, 'sha256'), 'hex');
END;
$$;

-- ── Trigger: auto-compute chain hash on insert ────────────────────────────────

CREATE OR REPLACE FUNCTION audit_ledger_chain_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_prev_hash TEXT;
BEGIN
    -- Get previous hash for this tenant (most recent record)
    SELECT chain_hash INTO v_prev_hash
    FROM audit_ledger
    WHERE tenant_id = NEW.tenant_id
    ORDER BY seq DESC
    LIMIT 1;

    IF v_prev_hash IS NULL THEN
        v_prev_hash := 'genesis';
    END IF;

    NEW.prev_hash := v_prev_hash;
    NEW.chain_hash := compute_audit_chain_hash(
        v_prev_hash,
        NEW.id,
        NEW.tenant_id,
        NEW.user_id,
        NEW.resource_type,
        NEW.action,
        NEW.created_at
    );

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER audit_ledger_chain
    BEFORE INSERT ON audit_ledger
    FOR EACH ROW EXECUTE FUNCTION audit_ledger_chain_trigger();

-- ── Verify chain function ─────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION verify_audit_chain(p_tenant_id UUID)
RETURNS TABLE (valid BOOLEAN, records_checked BIGINT, broken_at UUID)
LANGUAGE plpgsql
AS $$
DECLARE
    v_prev_hash TEXT := 'genesis';
    v_expected  TEXT;
    v_count     BIGINT := 0;
    rec         RECORD;
BEGIN
    FOR rec IN
        SELECT id, tenant_id, user_id, resource_type, action, created_at,
               prev_hash, chain_hash
        FROM audit_ledger
        WHERE tenant_id = p_tenant_id
        ORDER BY seq ASC
    LOOP
        IF rec.prev_hash <> v_prev_hash THEN
            RETURN QUERY SELECT false, v_count, rec.id;
            RETURN;
        END IF;

        v_expected := compute_audit_chain_hash(
            v_prev_hash, rec.id, rec.tenant_id, rec.user_id,
            rec.resource_type, rec.action, rec.created_at
        );

        IF rec.chain_hash <> v_expected THEN
            RETURN QUERY SELECT false, v_count, rec.id;
            RETURN;
        END IF;

        v_prev_hash := rec.chain_hash;
        v_count := v_count + 1;
    END LOOP;

    RETURN QUERY SELECT true, v_count, NULL::UUID;
END;
$$;

GRANT SELECT, INSERT ON audit_ledger TO ioslens_app;
GRANT EXECUTE ON FUNCTION verify_audit_chain(UUID) TO ioslens_app;

COMMIT;
