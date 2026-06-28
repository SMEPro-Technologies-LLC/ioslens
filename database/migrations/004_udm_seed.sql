-- 004_udm_seed.sql
-- Seed CIP, SOC, and NAICS reference codes (representative sample)
-- Full data loaded from CSV via COPY in production

BEGIN;

-- ── CIP Codes (Classification of Instructional Programs) ─────────────────────

INSERT INTO udm_entities (system, code, title, description, parent_code, level) VALUES
('CIP', '11', 'Computer and Information Sciences and Support Services', 'Programs that focus on computer hardware, software, and information systems.', NULL, 1),
('CIP', '11.01', 'Computer and Information Sciences, General', 'General programs in computer and information sciences.', '11', 2),
('CIP', '11.0101', 'Computer and Information Sciences, General', 'A general program that focuses on computer and information sciences.', '11.01', 3),
('CIP', '11.0201', 'Computer Programming/Programmer, General', 'A general program that prepares individuals to write and execute programs.', '11.02', 3),
('CIP', '11.0401', 'Information Science/Studies', 'A program that focuses on collecting, organizing, storing, retrieving, and disseminating information.', '11.04', 3),
('CIP', '11.0501', 'Computer Systems Analysis/Analyst', 'A program that prepares individuals to apply programming and systems analysis principles.', '11.05', 3),
('CIP', '11.0701', 'Computer Science', 'A program that focuses on computer theory, computing problems and solutions, and the design of computer systems.', '11.07', 3),
('CIP', '11.0801', 'Web Page, Digital/Multimedia and Information Resources Design', 'A program that prepares individuals to apply HTML, XML, and related tools to design web pages.', '11.08', 3),
('CIP', '51', 'Health Professions and Related Programs', 'Programs that prepare individuals to work in the health professions.', NULL, 1),
('CIP', '51.38', 'Registered Nursing, Nursing Administration, Nursing Research and Clinical Nursing', 'Programs in registered nursing and related fields.', '51', 2),
('CIP', '51.3801', 'Registered Nursing/Registered Nurse', 'A program that prepares individuals to take the NCLEX-RN examination.', '51.38', 3),
('CIP', '52', 'Business, Management, Marketing, and Related Support Services', 'Programs that prepare individuals for careers in business.', NULL, 1),
('CIP', '52.01', 'Business/Commerce, General', 'General programs in business and commerce.', '52', 2),
('CIP', '52.0101', 'Business/Commerce, General', 'A general program that focuses on the general study of business.', '52.01', 3),
('CIP', '52.1201', 'Management Information Systems, General', 'A program that prepares individuals to provide and manage data systems.', '52.12', 3)
ON CONFLICT (system, code) DO NOTHING;

-- ── SOC Codes (Standard Occupational Classification) ─────────────────────────

INSERT INTO udm_entities (system, code, title, description, parent_code, level) VALUES
('SOC', '15', 'Computer and Mathematical Occupations', 'Workers who apply mathematical or computing principles to solve problems.', NULL, 1),
('SOC', '15-1200', 'Computer Occupations', 'Workers who design, develop, test, and maintain software and computer systems.', '15', 2),
('SOC', '15-1211', 'Computer Systems Analysts', 'Analyze science, engineering, business, and other data processing problems.', '15-1200', 3),
('SOC', '15-1221', 'Computer and Information Research Scientists', 'Invent and design new approaches to computing technology.', '15-1200', 3),
('SOC', '15-1231', 'Computer Network Support Specialists', 'Analyze, test, troubleshoot, and evaluate existing network systems.', '15-1200', 3),
('SOC', '15-1241', 'Computer Network Architects', 'Design and implement computer and information networks.', '15-1200', 3),
('SOC', '15-1251', 'Computer Programmers', 'Create, modify, and test the code and scripts that allow computer applications to run.', '15-1200', 3),
('SOC', '15-1252', 'Software Developers', 'Research, design, and develop computer and network software or specialized utility programs.', '15-1200', 3),
('SOC', '15-1253', 'Software Quality Assurance Analysts and Testers', 'Develop and execute software tests.', '15-1200', 3),
('SOC', '29', 'Healthcare Practitioners and Technical Occupations', 'Workers who diagnose and treat patients or provide technical support.', NULL, 1),
('SOC', '29-1141', 'Registered Nurses', 'Assess patient health problems and needs, develop and implement nursing care plans.', '29', 3),
('SOC', '11', 'Management Occupations', 'Plan, direct, or coordinate activities of organizations or departments.', NULL, 1),
('SOC', '11-3021', 'Computer and Information Systems Managers', 'Plan, direct, or coordinate activities in such fields as electronic data processing.', '11', 3)
ON CONFLICT (system, code) DO NOTHING;

-- ── NAICS Codes (North American Industry Classification System) ───────────────

INSERT INTO udm_entities (system, code, title, description, parent_code, level) VALUES
('NAICS', '51', 'Information', 'Establishments engaged in the production and distribution of information and cultural products.', NULL, 1),
('NAICS', '511', 'Publishing Industries', 'Establishments engaged in publishing newspapers, magazines, books, etc.', '51', 2),
('NAICS', '5112', 'Software Publishers', 'Establishments primarily engaged in publishing computer software.', '511', 3),
('NAICS', '51121', 'Software Publishers', 'Establishments engaged in computer software publishing and/or reproduction.', '5112', 4),
('NAICS', '519', 'Other Information Services', 'Establishments engaged in information services not classified elsewhere.', '51', 2),
('NAICS', '5191', 'Other Information Services', 'Data processing, hosting, and related services.', '519', 3),
('NAICS', '61', 'Educational Services', 'Establishments engaged in providing instruction and training.', NULL, 1),
('NAICS', '611', 'Educational Services', 'Schools, colleges, universities, and training centers.', '61', 2),
('NAICS', '6111', 'Elementary and Secondary Schools', 'Establishments primarily engaged in furnishing academic courses.', '611', 3),
('NAICS', '6113', 'Colleges, Universities, and Professional Schools', 'Establishments engaged in furnishing academic courses and granting degrees.', '611', 3),
('NAICS', '62', 'Health Care and Social Assistance', 'Establishments providing health care and social assistance.', NULL, 1),
('NAICS', '621', 'Ambulatory Health Care Services', 'Establishments providing ambulatory health care services.', '62', 2),
('NAICS', '6211', 'Offices of Physicians', 'Establishments engaged in the practice of medicine under doctors of medicine.', '621', 3)
ON CONFLICT (system, code) DO NOTHING;

-- ── CIP-SOC Crosswalk (sample) ────────────────────────────────────────────────

INSERT INTO udm_crosswalk (from_system, from_code, to_system, to_code, confidence, source) VALUES
('CIP', '11.0101', 'SOC', '15-1252', 0.9200, 'NCES'),
('CIP', '11.0101', 'SOC', '15-1211', 0.8100, 'NCES'),
('CIP', '11.0701', 'SOC', '15-1252', 0.9500, 'NCES'),
('CIP', '11.0701', 'SOC', '15-1221', 0.8700, 'NCES'),
('CIP', '51.3801', 'SOC', '29-1141', 0.9800, 'NCES'),
('CIP', '52.0101', 'SOC', '11-3021', 0.7500, 'NCES'),
('CIP', '52.1201', 'SOC', '15-1211', 0.8900, 'NCES')
ON CONFLICT (from_system, from_code, to_system, to_code) DO NOTHING;

COMMIT;
