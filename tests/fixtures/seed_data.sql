-- tests/fixtures/seed_data.sql
-- Test fixture data for iOSLENS integration tests.
-- Applied to a test database before running integration tests.

-- Test tenant
INSERT INTO tenants (id, name, domain)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Test University',
    'test.ioslens.local'
) ON CONFLICT DO NOTHING;

-- Test users
INSERT INTO users (id, tenant_id, email, role, clearance)
VALUES
    ('00000000-0000-0000-0000-000000000010',
     '00000000-0000-0000-0000-000000000001',
     'admin@test.ioslens.local', 'admin', 4),
    ('00000000-0000-0000-0000-000000000011',
     '00000000-0000-0000-0000-000000000001',
     'analyst@test.ioslens.local', 'analyst', 2),
    ('00000000-0000-0000-0000-000000000012',
     '00000000-0000-0000-0000-000000000001',
     'viewer@test.ioslens.local', 'viewer', 1)
ON CONFLICT DO NOTHING;

-- Test UDM mappings
INSERT INTO udm_mappings (cip_code, soc_code, naics_code, label)
VALUES
    ('11.0701', '15-1252', '541511', 'Test: Software Development'),
    ('52.0201', '13-2011', '522110', 'Test: Accounting')
ON CONFLICT DO NOTHING;
