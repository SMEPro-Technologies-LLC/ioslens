-- 003_rls_policies.sql
-- SECURITY INVOKER RESTRICTIVE policies for tenant isolation

-- Create application role
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ioslens_app') THEN
        CREATE ROLE ioslens_app LOGIN;
    END IF;
END $$;

-- Grant privileges to app role
GRANT CONNECT ON DATABASE ioslens TO ioslens_app;
GRANT USAGE ON SCHEMA public TO ioslens_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ioslens_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO ioslens_app;

-- Enable RLS on all tenant-scoped tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE governance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_tokens ENABLE ROW LEVEL SECURITY;

-- ── USERS ────────────────────────────────────────────────────────────
CREATE POLICY users_tenant_isolation ON users
    AS RESTRICTIVE
    FOR ALL
    TO ioslens_app
    USING (
        current_setting('app.tenant_id', false) <> ''
        AND tenant_id = current_setting('app.tenant_id', false)::uuid
    );

-- ── GOVERNANCE POLICIES ──────────────────────────────────────────────
CREATE POLICY policies_tenant_isolation ON governance_policies
    AS RESTRICTIVE
    FOR ALL
    TO ioslens_app
    USING (
        current_setting('app.tenant_id', false) <> ''
        AND tenant_id = current_setting('app.tenant_id', false)::uuid
    );

-- ── AUDIT LEDGER (read-only via RLS; inserts use elevated role) ───────
CREATE POLICY audit_tenant_read ON audit_ledger
    AS RESTRICTIVE
    FOR SELECT
    TO ioslens_app
    USING (
        current_setting('app.tenant_id', false) <> ''
        AND tenant_id = current_setting('app.tenant_id', false)::uuid
    );

CREATE POLICY audit_tenant_insert ON audit_ledger
    AS RESTRICTIVE
    FOR INSERT
    TO ioslens_app
    WITH CHECK (
        current_setting('app.tenant_id', false) <> ''
        AND tenant_id = current_setting('app.tenant_id', false)::uuid
    );

-- ── EXECUTION TOKENS ─────────────────────────────────────────────────
CREATE POLICY tokens_tenant_isolation ON execution_tokens
    AS RESTRICTIVE
    FOR ALL
    TO ioslens_app
    USING (
        current_setting('app.tenant_id', false) <> ''
        AND tenant_id = current_setting('app.tenant_id', false)::uuid
    );

-- Helper function to set tenant context
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    PERFORM set_config('app.tenant_id', p_tenant_id::text, true);
END;
$$;

REVOKE ALL ON FUNCTION set_tenant_context FROM PUBLIC;
GRANT EXECUTE ON FUNCTION set_tenant_context TO ioslens_app;
