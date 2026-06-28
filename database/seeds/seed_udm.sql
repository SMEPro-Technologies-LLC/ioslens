-- seed_udm.sql
-- Comprehensive UDM seed: loads CIP, SOC, NAICS from staging tables
-- and builds cross-domain mappings.

-- Load CSV data into staging tables first (done externally by migrate script):
-- \COPY _cip_stage FROM 'database/seeds/cip_codes.csv' CSV HEADER;
-- \COPY _soc_stage FROM 'database/seeds/soc_codes.csv' CSV HEADER;
-- \COPY _naics_stage FROM 'database/seeds/naics_codes.csv' CSV HEADER;

-- Insert UDM cross-domain mappings for well-known combinations
INSERT INTO udm_mappings (cip_code, soc_code, naics_code, label, description)
VALUES
    ('11.0701', '15-1252', '541511',
     'Software Development',
     'Computer Science graduates entering custom software development'),
    ('11.0701', '15-1253', '541512',
     'Software QA Engineering',
     'Computer Science graduates in software quality assurance roles'),
    ('11.0701', '15-1212', '541511',
     'Information Security',
     'Computer Science graduates in cybersecurity roles'),
    ('52.0201', '13-2011', '522110',
     'Accounting and Commercial Banking',
     'Business Administration graduates in accounting at commercial banks'),
    ('51.3801', '29-1141', '622110',
     'Registered Nursing in Hospitals',
     'Registered Nursing graduates working in general hospitals'),
    ('13.1202', '25-2021', '611110',
     'Elementary Education',
     'Elementary Education graduates teaching in K-12 schools'),
    ('14.0901', '17-2071', '541330',
     'Electrical Engineering Services',
     'Electrical Engineering graduates in engineering services firms'),
    ('22.0101', '23-1011', '541110',
     'Law Practice',
     'Law graduates in law firms'),
    ('27.0101', '15-1211', '541511',
     'Applied Mathematics in Tech',
     'Mathematics graduates in computer research roles'),
    ('26.0101', '29-1215', '621111',
     'Biology to Medicine',
     'Biology graduates advancing to physician roles')
ON CONFLICT DO NOTHING;

-- Update statistics
ANALYZE udm_mappings;
