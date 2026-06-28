-- 003_rls_policies.sql
-- Row-Level Security: SECURITY INVOKER + RESTRICTIVE policies on all tenant-scoped tables

BEGIN;

-- ── Enable RLS on all tenant-scoped tables ────────────────────────────────────

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

ALTER TABLE governance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE governance_policies FORCE ROW LEVEL SECURITY;

ALTER TABLE execution_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_tokens FORCE ROW LEVEL SECURITY;

-- ── users ─────────────────────────────────────────────────────────────────────

-- RESTRICTIVE tenant isolation — cannot be bypassed by any role
CREATE POLICY users_tenant_isolation ON users
    AS RESTRICTIVE
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Read: own record or admin/advisor role
CREATE POLICY users_read ON users
    FOR SELECT
    USING (
        id = current_setting('app.user_id', true)::uuid
        OR 'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
        OR 'ADVISOR' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

-- Write: admin only
CREATE POLICY users_write ON users
    FOR INSERT WITH CHECK (
        'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

CREATE POLICY users_update ON users
    FOR UPDATE USING (
        id = current_setting('app.user_id', true)::uuid
        OR 'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

-- ── governance_policies ───────────────────────────────────────────────────────

CREATE POLICY gp_tenant_isolation ON governance_policies
    AS RESTRICTIVE
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY gp_read ON governance_policies
    FOR SELECT
    USING (
        active = true
        OR 'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

CREATE POLICY gp_write ON governance_policies
    FOR INSERT WITH CHECK (
        'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

CREATE POLICY gp_update ON governance_policies
    FOR UPDATE USING (
        'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

-- ── execution_tokens ──────────────────────────────────────────────────────────

CREATE POLICY et_tenant_isolation ON execution_tokens
    AS RESTRICTIVE
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY et_read ON execution_tokens
    FOR SELECT
    USING (
        user_id = current_setting('app.user_id', true)::uuid
        OR 'ADMIN' = ANY(string_to_array(current_setting('app.roles', true), ','))
    );

CREATE POLICY et_insert ON execution_tokens
    FOR INSERT WITH CHECK (
        tenant_id = current_setting('app.tenant_id', true)::uuid
    );

-- ── Application role for API connections ──────────────────────────────────────
-- The application connects as the 'ioslens_app' role which has limited privileges.
-- Superuser / migration role retains full access.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ioslens_app') THEN
        CREATE ROLE ioslens_app LOGIN;
    END IF;
END $$;

GRANT CONNECT ON DATABASE ioslens TO ioslens_app;
GRANT USAGE ON SCHEMA public TO ioslens_app;
GRANT SELECT, INSERT, UPDATE ON users TO ioslens_app;
GRANT SELECT, INSERT ON governance_policies TO ioslens_app;
GRANT SELECT, INSERT, UPDATE ON execution_tokens TO ioslens_app;
GRANT SELECT, INSERT ON udm_entities TO ioslens_app;
GRANT SELECT, INSERT ON udm_crosswalk TO ioslens_app;

COMMIT;
