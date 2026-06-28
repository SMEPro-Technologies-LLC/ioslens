-- 004_udm_seed.sql
-- Load CIP/SOC/NAICS reference data from seed CSVs.
-- This migration references the seeds directory files loaded via COPY.

-- Staging table for CIP codes
CREATE TEMP TABLE IF NOT EXISTS _cip_stage (
    code    TEXT,
    title   TEXT,
    level   TEXT,
    series  TEXT
);

-- Staging table for SOC codes
CREATE TEMP TABLE IF NOT EXISTS _soc_stage (
    code        TEXT,
    title       TEXT,
    major_group TEXT
);

-- Staging table for NAICS codes
CREATE TEMP TABLE IF NOT EXISTS _naics_stage (
    code    TEXT,
    title   TEXT,
    sector  TEXT
);

-- In production, these COPY commands are run by the seed script
-- with the CSV files available on the database server path.
-- Example (adjust path as needed for your environment):
-- \COPY _cip_stage FROM 'database/seeds/cip_codes.csv' CSV HEADER;
-- \COPY _soc_stage FROM 'database/seeds/soc_codes.csv' CSV HEADER;
-- \COPY _naics_stage FROM 'database/seeds/naics_codes.csv' CSV HEADER;

-- Populate a few representative UDM mapping samples for dev/test environments
INSERT INTO udm_mappings (cip_code, soc_code, naics_code, label, description)
VALUES
    ('11.0701', '15-1252', '541511', 'Software Development',
     'CIP Computer Science → SOC Software Developers → NAICS Custom Programming'),
    ('52.0201', '13-2011', '522110', 'Accounting & Finance',
     'CIP Accounting → SOC Accountants → NAICS Commercial Banking'),
    ('51.3801', '29-1141', '622110', 'Nursing & Healthcare',
     'CIP Registered Nursing → SOC Registered Nurses → NAICS General Medical'),
    ('13.0101', '25-2021', '611110', 'Elementary Education',
     'CIP Education Administration → SOC Elementary Teachers → NAICS Elementary Schools'),
    ('14.0901', '17-2071', '541330', 'Electrical Engineering',
     'CIP Electrical Engineering → SOC Electrical Engineers → NAICS Engineering Services')
ON CONFLICT DO NOTHING;
