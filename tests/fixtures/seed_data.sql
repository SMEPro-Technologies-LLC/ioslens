-- Test fixture seed data
-- Used by integration tests via PYTHONPATH=src pytest tests/integration

BEGIN;

-- Test tenant
INSERT INTO tenants (id, name, domain, tier, features)
VALUES (
    '10000000-0000-0000-0000-000000000001',
    'Test University',
    'test.university.edu',
    'enterprise',
    '["udm","audit","mcp"]'
) ON CONFLICT DO NOTHING;

-- Test users
INSERT INTO users (id, tenant_id, external_id, email, roles, clearance)
VALUES
    ('20000000-0000-0000-0000-000000000001',
     '10000000-0000-0000-0000-000000000001',
     'ext_admin_001',
     'admin@test.university.edu',
     '{ADMIN}',
     10),
    ('20000000-0000-0000-0000-000000000002',
     '10000000-0000-0000-0000-000000000001',
     'ext_advisor_001',
     'advisor@test.university.edu',
     '{ADVISOR}',
     3),
    ('20000000-0000-0000-0000-000000000003',
     '10000000-0000-0000-0000-000000000001',
     'ext_user_001',
     'user@test.university.edu',
     '{USER}',
     0)
ON CONFLICT DO NOTHING;

-- Test governance policies
INSERT INTO governance_policies (tenant_id, name, resource_type, allowed_roles, allowed_purposes, min_clearance)
VALUES
    ('10000000-0000-0000-0000-000000000001',
     'STUDENT_RECORD_ADVISOR_READ',
     'student_record',
     '{ADVISOR,ADMIN}',
     '{academic_advising,reporting}',
     0),
    ('10000000-0000-0000-0000-000000000001',
     'EMPLOYEE_RECORD_ADMIN_READ',
     'employee_record',
     '{ADMIN}',
     '{hr_management}',
     5)
ON CONFLICT DO NOTHING;

COMMIT;
