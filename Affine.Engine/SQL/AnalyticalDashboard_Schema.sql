-- ============================================================================
-- ANALYTICAL DASHBOARD SCHEMA - Organizational Hierarchy & Drill-Down Reporting
-- ============================================================================
-- This script creates the complete schema for:
-- 1. Organizational hierarchy (Audit Universe)
-- 2. Audit findings and control testing
-- 3. Extensions to existing tables for hierarchy linking
-- 4. Comprehensive mock data for testing
-- ============================================================================

-- Set schema search path
SET search_path TO "Risk_Assess_Framework", public;

-- ============================================================================
-- PART 1: LOOKUP TABLES
-- ============================================================================

-- Engagement Status Lookup
CREATE TABLE IF NOT EXISTS ra_engagementstatus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_engagementstatus (name, description, sort_order) VALUES
('Planning', 'Engagement is in planning phase', 1),
('Fieldwork', 'Active fieldwork in progress', 2),
('Review', 'Under management review', 3),
('Draft Report', 'Draft report issued', 4),
('Final Report', 'Final report issued', 5),
('Closed', 'Engagement closed', 6)
ON CONFLICT (name) DO NOTHING;

-- Finding Status Lookup
CREATE TABLE IF NOT EXISTS ra_findingstatus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_findingstatus (name, description, sort_order) VALUES
('Open', 'Finding awaiting remediation', 1),
('In Progress', 'Remediation in progress', 2),
('Pending Verification', 'Remediation complete, awaiting verification', 3),
('Closed', 'Finding verified and closed', 4),
('Overdue', 'Finding past due date', 5)
ON CONFLICT (name) DO NOTHING;

-- Risk Treatment Status Lookup
CREATE TABLE IF NOT EXISTS ra_treatmentstatus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_treatmentstatus (name, description, sort_order) VALUES
('Not Started', 'Treatment not yet initiated', 1),
('In Progress', 'Treatment being implemented', 2),
('Implemented', 'Treatment implemented, pending verification', 3),
('Verified', 'Treatment verified as effective', 4),
('Deferred', 'Treatment deferred to future period', 5),
('Accepted', 'Risk accepted without treatment', 6)
ON CONFLICT (name) DO NOTHING;

-- Finding Severity Lookup
CREATE TABLE IF NOT EXISTS ra_findingseverity (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_findingseverity (name, description, color, sort_order) VALUES
('Critical', 'Requires immediate action - significant business impact', '#8B0000', 1),
('High', 'Requires urgent attention - material impact', '#e74c3c', 2),
('Medium', 'Should be addressed within normal timeframes', '#f39c12', 3),
('Low', 'Minor issue - address when convenient', '#2ecc71', 4)
ON CONFLICT (name) DO NOTHING;

-- Control Test Result Lookup
CREATE TABLE IF NOT EXISTS ra_testresult (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_testresult (name, description, color, sort_order) VALUES
('Effective', 'Control operating effectively as designed', '#2ecc71', 1),
('Partially Effective', 'Control has some deficiencies but provides reasonable assurance', '#f39c12', 2),
('Ineffective', 'Control not operating as designed - remediation required', '#e74c3c', 3),
('Not Tested', 'Control not tested in this period', '#95a5a6', 4)
ON CONFLICT (name) DO NOTHING;

-- Industry Types Lookup
CREATE TABLE IF NOT EXISTS ra_industry (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_industry (name, description, sort_order) VALUES
('Financial Services', 'Banks, insurance, investment firms', 1),
('Healthcare', 'Hospitals, pharmaceuticals, medical devices', 2),
('Manufacturing', 'Industrial production, assembly', 3),
('Retail', 'Consumer goods, e-commerce', 4),
('Technology', 'Software, hardware, IT services', 5),
('Energy', 'Oil, gas, utilities, renewables', 6),
('Telecommunications', 'Mobile, broadband, media', 7),
('Government', 'Public sector, municipalities', 8),
('Education', 'Universities, schools, training', 9),
('Non-Profit', 'Charities, NGOs, foundations', 10)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- PART 2: CORE HIERARCHY TABLES
-- ============================================================================

-- 1. AUDIT CLIENTS (Top Level - Audit Universe)
CREATE TABLE IF NOT EXISTS audit_clients (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(500),
    industry_id INTEGER REFERENCES ra_industry(id),
    fiscal_year_end INTEGER DEFAULT 12 CHECK (fiscal_year_end >= 1 AND fiscal_year_end <= 12),
    risk_appetite VARCHAR(50) DEFAULT 'Moderate' CHECK (risk_appetite IN ('Conservative', 'Moderate', 'Aggressive')),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    parent_client_id INTEGER REFERENCES audit_clients(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. AUDIT REGIONS (Geographic Segmentation)
CREATE TABLE IF NOT EXISTS audit_regions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    country_code CHAR(2),
    country_name VARCHAR(100),
    region_type VARCHAR(50) DEFAULT 'Country' CHECK (region_type IN ('Country', 'Region', 'Zone', 'Territory')),
    regulatory_jurisdiction VARCHAR(100),
    timezone VARCHAR(50),
    currency_code CHAR(3),
    is_active BOOLEAN DEFAULT TRUE,
    parent_region_id INTEGER REFERENCES audit_regions(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. BUSINESS UNITS (Divisions/Subsidiaries)
CREATE TABLE IF NOT EXISTS business_units (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    client_id INTEGER NOT NULL REFERENCES audit_clients(id) ON DELETE CASCADE,
    region_id INTEGER REFERENCES audit_regions(id) ON DELETE SET NULL,
    unit_type VARCHAR(50) DEFAULT 'Division' CHECK (unit_type IN ('Division', 'Subsidiary', 'Branch', 'Department', 'Cost Center')),
    cost_center VARCHAR(50),
    revenue_center VARCHAR(50),
    risk_level_id INTEGER REFERENCES ra_risklevels(id) DEFAULT 2,
    head_name VARCHAR(255),
    head_email VARCHAR(255),
    employee_count INTEGER,
    annual_revenue DECIMAL(18, 2),
    is_active BOOLEAN DEFAULT TRUE,
    parent_unit_id INTEGER REFERENCES business_units(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. FISCAL PERIODS (Audit Cycles)
CREATE TABLE IF NOT EXISTS fiscal_periods (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES audit_clients(id) ON DELETE CASCADE,
    period_name VARCHAR(100) NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('Year', 'Quarter', 'Month', 'Custom')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    is_closed BOOLEAN DEFAULT FALSE,
    budget_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_id, period_name),
    CHECK (end_date > start_date)
);

-- 5. AUDIT ENGAGEMENTS (Links assessments to hierarchy)
CREATE TABLE IF NOT EXISTS audit_engagements (
    id SERIAL PRIMARY KEY,
    engagement_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    engagement_type VARCHAR(50) DEFAULT 'Operational' CHECK (engagement_type IN ('Financial', 'Operational', 'Compliance', 'IT', 'Forensic', 'Performance', 'Integrated')),
    client_id INTEGER NOT NULL REFERENCES audit_clients(id) ON DELETE CASCADE,
    region_id INTEGER REFERENCES audit_regions(id) ON DELETE SET NULL,
    business_unit_id INTEGER REFERENCES business_units(id) ON DELETE SET NULL,
    fiscal_period_id INTEGER REFERENCES fiscal_periods(id) ON DELETE SET NULL,
    lead_auditor_id INTEGER,
    status_id INTEGER REFERENCES ra_engagementstatus(id) DEFAULT 1,
    priority VARCHAR(20) DEFAULT 'Medium' CHECK (priority IN ('Critical', 'High', 'Medium', 'Low')),
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    budget_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    scope_summary TEXT,
    objectives TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PART 3: AUDIT FINDINGS & CONTROL TESTING TABLES
-- ============================================================================

-- 6. AUDIT FINDINGS (Issues identified during audits)
CREATE TABLE IF NOT EXISTS audit_findings (
    id SERIAL PRIMARY KEY,
    finding_code VARCHAR(50) UNIQUE NOT NULL,
    engagement_id INTEGER REFERENCES audit_engagements(id) ON DELETE CASCADE,
    reference_id INTEGER,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    root_cause TEXT,
    business_impact TEXT,
    finding_type VARCHAR(50) DEFAULT 'Control Deficiency' CHECK (finding_type IN ('Control Deficiency', 'Process Gap', 'Compliance Issue', 'Data Quality', 'Security Vulnerability', 'Fraud Indicator')),
    severity_id INTEGER REFERENCES ra_findingseverity(id) DEFAULT 3,
    status_id INTEGER REFERENCES ra_findingstatus(id) DEFAULT 1,
    treatment_status_id INTEGER REFERENCES ra_treatmentstatus(id) DEFAULT 1,
    owner_id INTEGER,
    owner_name VARCHAR(255),
    owner_email VARCHAR(255),
    due_date DATE,
    closed_date DATE,
    management_response TEXT,
    agreed_action TEXT,
    identified_date DATE DEFAULT CURRENT_DATE,
    repeat_finding BOOLEAN DEFAULT FALSE,
    prior_finding_id INTEGER REFERENCES audit_findings(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. CONTROL TESTS (Control Testing Records)
CREATE TABLE IF NOT EXISTS control_tests (
    id SERIAL PRIMARY KEY,
    test_code VARCHAR(50) UNIQUE NOT NULL,
    engagement_id INTEGER REFERENCES audit_engagements(id) ON DELETE CASCADE,
    control_name VARCHAR(255) NOT NULL,
    control_description TEXT,
    control_type VARCHAR(50) DEFAULT 'Detective' CHECK (control_type IN ('Preventive', 'Detective', 'Corrective', 'Directive')),
    control_category VARCHAR(50) DEFAULT 'Manual' CHECK (control_category IN ('Manual', 'Automated', 'IT-Dependent Manual')),
    tester_id INTEGER,
    tester_name VARCHAR(255),
    test_procedure TEXT,
    sample_size INTEGER,
    exceptions_found INTEGER DEFAULT 0,
    test_date DATE,
    result_id INTEGER REFERENCES ra_testresult(id) DEFAULT 4,
    conclusion TEXT,
    recommendations TEXT,
    evidence_reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PART 4: ALTER EXISTING TABLES FOR HIERARCHY LINKING
-- ============================================================================

-- Add hierarchy columns to departments (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'departments' AND column_name = 'business_unit_id') THEN
        ALTER TABLE departments ADD COLUMN business_unit_id INTEGER REFERENCES business_units(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'departments' AND column_name = 'client_id') THEN
        ALTER TABLE departments ADD COLUMN client_id INTEGER REFERENCES audit_clients(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Add hierarchy columns to projects (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'projects' AND column_name = 'business_unit_id') THEN
        ALTER TABLE projects ADD COLUMN business_unit_id INTEGER REFERENCES business_units(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'projects' AND column_name = 'engagement_id') THEN
        ALTER TABLE projects ADD COLUMN engagement_id INTEGER REFERENCES audit_engagements(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Add hierarchy columns to riskassessmentreference (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'riskassessmentreference' AND column_name = 'engagement_id') THEN
        ALTER TABLE riskassessmentreference ADD COLUMN engagement_id INTEGER REFERENCES audit_engagements(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'riskassessmentreference' AND column_name = 'client_id') THEN
        ALTER TABLE riskassessmentreference ADD COLUMN client_id INTEGER REFERENCES audit_clients(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'riskassessmentreference' AND column_name = 'region_id') THEN
        ALTER TABLE riskassessmentreference ADD COLUMN region_id INTEGER REFERENCES audit_regions(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'riskassessmentreference' AND column_name = 'business_unit_id') THEN
        ALTER TABLE riskassessmentreference ADD COLUMN business_unit_id INTEGER REFERENCES business_units(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'Risk_Assess_Framework' AND table_name = 'riskassessmentreference' AND column_name = 'fiscal_period_id') THEN
        ALTER TABLE riskassessmentreference ADD COLUMN fiscal_period_id INTEGER REFERENCES fiscal_periods(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================================
-- PART 5: INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_audit_clients_code ON audit_clients(code);
CREATE INDEX IF NOT EXISTS idx_audit_clients_parent ON audit_clients(parent_client_id);
CREATE INDEX IF NOT EXISTS idx_audit_clients_industry ON audit_clients(industry_id);
CREATE INDEX IF NOT EXISTS idx_audit_clients_active ON audit_clients(is_active);

CREATE INDEX IF NOT EXISTS idx_audit_regions_code ON audit_regions(code);
CREATE INDEX IF NOT EXISTS idx_audit_regions_country ON audit_regions(country_code);
CREATE INDEX IF NOT EXISTS idx_audit_regions_parent ON audit_regions(parent_region_id);
CREATE INDEX IF NOT EXISTS idx_audit_regions_active ON audit_regions(is_active);

CREATE INDEX IF NOT EXISTS idx_business_units_client ON business_units(client_id);
CREATE INDEX IF NOT EXISTS idx_business_units_region ON business_units(region_id);
CREATE INDEX IF NOT EXISTS idx_business_units_code ON business_units(code);
CREATE INDEX IF NOT EXISTS idx_business_units_parent ON business_units(parent_unit_id);
CREATE INDEX IF NOT EXISTS idx_business_units_active ON business_units(is_active);

CREATE INDEX IF NOT EXISTS idx_fiscal_periods_client ON fiscal_periods(client_id);
CREATE INDEX IF NOT EXISTS idx_fiscal_periods_dates ON fiscal_periods(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_fiscal_periods_current ON fiscal_periods(is_current);

CREATE INDEX IF NOT EXISTS idx_audit_engagements_client ON audit_engagements(client_id);
CREATE INDEX IF NOT EXISTS idx_audit_engagements_region ON audit_engagements(region_id);
CREATE INDEX IF NOT EXISTS idx_audit_engagements_unit ON audit_engagements(business_unit_id);
CREATE INDEX IF NOT EXISTS idx_audit_engagements_period ON audit_engagements(fiscal_period_id);
CREATE INDEX IF NOT EXISTS idx_audit_engagements_status ON audit_engagements(status_id);
CREATE INDEX IF NOT EXISTS idx_audit_engagements_code ON audit_engagements(engagement_code);

CREATE INDEX IF NOT EXISTS idx_audit_findings_engagement ON audit_findings(engagement_id);
CREATE INDEX IF NOT EXISTS idx_audit_findings_status ON audit_findings(status_id);
CREATE INDEX IF NOT EXISTS idx_audit_findings_severity ON audit_findings(severity_id);
CREATE INDEX IF NOT EXISTS idx_audit_findings_due_date ON audit_findings(due_date);
CREATE INDEX IF NOT EXISTS idx_audit_findings_code ON audit_findings(finding_code);
CREATE INDEX IF NOT EXISTS idx_audit_findings_treatment ON audit_findings(treatment_status_id);

CREATE INDEX IF NOT EXISTS idx_control_tests_engagement ON control_tests(engagement_id);
CREATE INDEX IF NOT EXISTS idx_control_tests_result ON control_tests(result_id);
CREATE INDEX IF NOT EXISTS idx_control_tests_code ON control_tests(test_code);
CREATE INDEX IF NOT EXISTS idx_control_tests_date ON control_tests(test_date);

-- ============================================================================
-- PART 6: COMPREHENSIVE MOCK DATA
-- ============================================================================

-- 6.1 AUDIT CLIENTS (5 clients across industries)
INSERT INTO audit_clients (code, name, legal_name, industry_id, fiscal_year_end, risk_appetite, contact_name, contact_email, is_active) VALUES
('CLI-001', 'Affine Financial Services', 'Affine Financial Services (Pty) Ltd', 1, 12, 'Conservative', 'John Smith', 'john.smith@affine.co.za', TRUE),
('CLI-002', 'MedCare Holdings', 'MedCare Holdings International Ltd', 2, 6, 'Moderate', 'Sarah Johnson', 'sjohnson@medcare.com', TRUE),
('CLI-003', 'TechNova Solutions', 'TechNova Solutions Inc.', 5, 12, 'Aggressive', 'Michael Chen', 'm.chen@technova.io', TRUE),
('CLI-004', 'Global Retail Group', 'Global Retail Group Plc', 4, 3, 'Moderate', 'Emma Williams', 'e.williams@grg.co.uk', TRUE),
('CLI-005', 'Energy Partners SA', 'Energy Partners South Africa (Pty) Ltd', 6, 12, 'Conservative', 'David Nkosi', 'd.nkosi@energypartners.co.za', TRUE)
ON CONFLICT (code) DO NOTHING;

-- 6.2 AUDIT REGIONS (10 regions across countries)
INSERT INTO audit_regions (code, name, country_code, country_name, region_type, regulatory_jurisdiction, timezone, currency_code, is_active) VALUES
('REG-ZA', 'South Africa', 'ZA', 'South Africa', 'Country', 'SARB/FSB', 'Africa/Johannesburg', 'ZAR', TRUE),
('REG-GB', 'United Kingdom', 'GB', 'United Kingdom', 'Country', 'FCA/PRA', 'Europe/London', 'GBP', TRUE),
('REG-US', 'United States', 'US', 'United States', 'Country', 'SEC/FDIC', 'America/New_York', 'USD', TRUE),
('REG-DE', 'Germany', 'DE', 'Germany', 'Country', 'BaFin', 'Europe/Berlin', 'EUR', TRUE),
('REG-AU', 'Australia', 'AU', 'Australia', 'Country', 'APRA/ASIC', 'Australia/Sydney', 'AUD', TRUE),
('REG-SG', 'Singapore', 'SG', 'Singapore', 'Country', 'MAS', 'Asia/Singapore', 'SGD', TRUE),
('REG-AE', 'United Arab Emirates', 'AE', 'United Arab Emirates', 'Country', 'DFSA/CBUAE', 'Asia/Dubai', 'AED', TRUE),
('REG-KE', 'Kenya', 'KE', 'Kenya', 'Country', 'CBK/CMA', 'Africa/Nairobi', 'KES', TRUE),
('REG-NG', 'Nigeria', 'NG', 'Nigeria', 'Country', 'CBN/SEC', 'Africa/Lagos', 'NGN', TRUE),
('REG-EMEA', 'EMEA Region', NULL, NULL, 'Region', 'Multiple', 'Europe/London', 'EUR', TRUE)
ON CONFLICT (code) DO NOTHING;

-- Set EMEA as parent for European countries
UPDATE audit_regions SET parent_region_id = (SELECT id FROM audit_regions WHERE code = 'REG-EMEA') WHERE code IN ('REG-GB', 'REG-DE', 'REG-AE');

-- 6.3 BUSINESS UNITS (15 units across clients)
INSERT INTO business_units (code, name, description, client_id, region_id, unit_type, cost_center, risk_level_id, head_name, head_email, employee_count, annual_revenue, is_active) VALUES
-- Affine Financial Services units
('BU-AFF-CORP', 'Corporate Banking', 'Corporate and commercial banking division', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), 'Division', 'CC-1001', 1, 'Peter Molefe', 'p.molefe@affine.co.za', 450, 2500000000.00, TRUE),
('BU-AFF-RET', 'Retail Banking', 'Consumer retail banking operations', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), 'Division', 'CC-1002', 2, 'Linda Dlamini', 'l.dlamini@affine.co.za', 1200, 1800000000.00, TRUE),
('BU-AFF-TREAS', 'Treasury', 'Treasury and capital markets', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), 'Division', 'CC-1003', 1, 'James van der Berg', 'j.vanderberg@affine.co.za', 85, 500000000.00, TRUE),
-- MedCare Holdings units
('BU-MED-HOSP', 'Hospital Services', 'Hospital management and operations', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), 'Division', 'CC-2001', 2, 'Dr. Robert Hughes', 'r.hughes@medcare.com', 3500, 800000000.00, TRUE),
('BU-MED-PHARM', 'Pharmaceuticals', 'Drug distribution and pharmacy services', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), 'Division', 'CC-2002', 2, 'Helen Brown', 'h.brown@medcare.com', 800, 450000000.00, TRUE),
('BU-MED-DIAG', 'Diagnostics', 'Laboratory and diagnostic services', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-US'), 'Subsidiary', 'CC-2003', 3, 'Mark Stevens', 'm.stevens@medcare.com', 250, 120000000.00, TRUE),
-- TechNova Solutions units
('BU-TECH-DEV', 'Product Development', 'Software product development', (SELECT id FROM audit_clients WHERE code = 'CLI-003'), (SELECT id FROM audit_regions WHERE code = 'REG-US'), 'Division', 'CC-3001', 2, 'Jennifer Lee', 'j.lee@technova.io', 500, 300000000.00, TRUE),
('BU-TECH-CLOUD', 'Cloud Services', 'Cloud infrastructure and managed services', (SELECT id FROM audit_clients WHERE code = 'CLI-003'), (SELECT id FROM audit_regions WHERE code = 'REG-SG'), 'Division', 'CC-3002', 1, 'Raj Patel', 'r.patel@technova.io', 200, 180000000.00, TRUE),
('BU-TECH-SEC', 'Cybersecurity', 'Security products and consulting', (SELECT id FROM audit_clients WHERE code = 'CLI-003'), (SELECT id FROM audit_regions WHERE code = 'REG-DE'), 'Subsidiary', 'CC-3003', 1, 'Klaus Mueller', 'k.mueller@technova.io', 150, 95000000.00, TRUE),
-- Global Retail Group units
('BU-GRG-STORES', 'Retail Stores', 'Physical retail store operations', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), 'Division', 'CC-4001', 2, 'Tom Wilson', 't.wilson@grg.co.uk', 8000, 1200000000.00, TRUE),
('BU-GRG-ECOM', 'E-Commerce', 'Online retail platform', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), 'Division', 'CC-4002', 2, 'Sophie Turner', 's.turner@grg.co.uk', 350, 650000000.00, TRUE),
('BU-GRG-SUPPLY', 'Supply Chain', 'Logistics and supply chain management', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-DE'), 'Division', 'CC-4003', 2, 'Hans Weber', 'h.weber@grg.co.uk', 450, 200000000.00, TRUE),
-- Energy Partners units
('BU-EP-GEN', 'Power Generation', 'Electricity generation plants', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), 'Division', 'CC-5001', 1, 'Thabo Mabasa', 't.mabasa@energypartners.co.za', 600, 900000000.00, TRUE),
('BU-EP-DIST', 'Distribution', 'Power distribution network', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), 'Division', 'CC-5002', 2, 'Nomsa Khumalo', 'n.khumalo@energypartners.co.za', 400, 350000000.00, TRUE),
('BU-EP-RENEW', 'Renewable Energy', 'Solar and wind power projects', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-KE'), 'Subsidiary', 'CC-5003', 3, 'Joseph Ochieng', 'j.ochieng@energypartners.co.za', 120, 80000000.00, TRUE)
ON CONFLICT (code) DO NOTHING;

-- 6.4 FISCAL PERIODS (20 periods - current + historical)
INSERT INTO fiscal_periods (client_id, period_name, period_type, start_date, end_date, is_current, is_closed, budget_hours) VALUES
-- Affine Financial Services (Dec year-end)
((SELECT id FROM audit_clients WHERE code = 'CLI-001'), 'FY 2023', 'Year', '2023-01-01', '2023-12-31', FALSE, TRUE, 5000),
((SELECT id FROM audit_clients WHERE code = 'CLI-001'), 'FY 2024', 'Year', '2024-01-01', '2024-12-31', FALSE, TRUE, 5500),
((SELECT id FROM audit_clients WHERE code = 'CLI-001'), 'FY 2025', 'Year', '2025-01-01', '2025-12-31', TRUE, FALSE, 6000),
((SELECT id FROM audit_clients WHERE code = 'CLI-001'), 'Q1 2025', 'Quarter', '2025-01-01', '2025-03-31', FALSE, TRUE, 1500),
((SELECT id FROM audit_clients WHERE code = 'CLI-001'), 'Q2 2025', 'Quarter', '2025-04-01', '2025-06-30', FALSE, TRUE, 1500),
((SELECT id FROM audit_clients WHERE code = 'CLI-001'), 'Q3 2025', 'Quarter', '2025-07-01', '2025-09-30', FALSE, TRUE, 1500),
((SELECT id FROM audit_clients WHERE code = 'CLI-001'), 'Q4 2025', 'Quarter', '2025-10-01', '2025-12-31', TRUE, FALSE, 1500),
-- MedCare Holdings (Jun year-end)
((SELECT id FROM audit_clients WHERE code = 'CLI-002'), 'FY 2023/24', 'Year', '2023-07-01', '2024-06-30', FALSE, TRUE, 4000),
((SELECT id FROM audit_clients WHERE code = 'CLI-002'), 'FY 2024/25', 'Year', '2024-07-01', '2025-06-30', FALSE, TRUE, 4200),
((SELECT id FROM audit_clients WHERE code = 'CLI-002'), 'FY 2025/26', 'Year', '2025-07-01', '2026-06-30', TRUE, FALSE, 4500),
-- TechNova Solutions (Dec year-end)
((SELECT id FROM audit_clients WHERE code = 'CLI-003'), 'FY 2024', 'Year', '2024-01-01', '2024-12-31', FALSE, TRUE, 3000),
((SELECT id FROM audit_clients WHERE code = 'CLI-003'), 'FY 2025', 'Year', '2025-01-01', '2025-12-31', TRUE, FALSE, 3500),
-- Global Retail Group (Mar year-end)
((SELECT id FROM audit_clients WHERE code = 'CLI-004'), 'FY 2023/24', 'Year', '2023-04-01', '2024-03-31', FALSE, TRUE, 4500),
((SELECT id FROM audit_clients WHERE code = 'CLI-004'), 'FY 2024/25', 'Year', '2024-04-01', '2025-03-31', FALSE, TRUE, 4800),
((SELECT id FROM audit_clients WHERE code = 'CLI-004'), 'FY 2025/26', 'Year', '2025-04-01', '2026-03-31', TRUE, FALSE, 5000),
-- Energy Partners (Dec year-end)
((SELECT id FROM audit_clients WHERE code = 'CLI-005'), 'FY 2023', 'Year', '2023-01-01', '2023-12-31', FALSE, TRUE, 3500),
((SELECT id FROM audit_clients WHERE code = 'CLI-005'), 'FY 2024', 'Year', '2024-01-01', '2024-12-31', FALSE, TRUE, 3800),
((SELECT id FROM audit_clients WHERE code = 'CLI-005'), 'FY 2025', 'Year', '2025-01-01', '2025-12-31', TRUE, FALSE, 4000),
((SELECT id FROM audit_clients WHERE code = 'CLI-005'), 'H1 2025', 'Custom', '2025-01-01', '2025-06-30', FALSE, TRUE, 2000),
((SELECT id FROM audit_clients WHERE code = 'CLI-005'), 'H2 2025', 'Custom', '2025-07-01', '2025-12-31', TRUE, FALSE, 2000)
ON CONFLICT (client_id, period_name) DO NOTHING;

-- 6.5 AUDIT ENGAGEMENTS (30 engagements across clients and periods)
INSERT INTO audit_engagements (engagement_code, title, description, engagement_type, client_id, region_id, business_unit_id, fiscal_period_id, status_id, priority, planned_start_date, planned_end_date, actual_start_date, budget_hours, scope_summary) VALUES
-- Affine Financial Services engagements
('ENG-2025-001', 'Corporate Lending Review', 'Annual review of corporate lending processes and credit risk management', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-AFF-CORP'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 2, 'High', '2025-01-15', '2025-03-15', '2025-01-15', 800, 'Credit origination, approval, monitoring and collections'),
('ENG-2025-002', 'Retail Branch Operations', 'Audit of retail branch operational controls', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-AFF-RET'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 3, 'Medium', '2025-02-01', '2025-04-30', '2025-02-01', 600, 'Cash handling, teller operations, customer service'),
('ENG-2025-003', 'Treasury Compliance', 'Regulatory compliance review of treasury operations', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-AFF-TREAS'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 4, 'Critical', '2025-03-01', '2025-05-31', '2025-03-01', 500, 'SARB compliance, market risk limits, trading controls'),
('ENG-2025-004', 'IT General Controls', 'Annual ITGC assessment across all divisions', 'IT', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), NULL, (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 2, 'High', '2025-04-01', '2025-06-30', '2025-04-01', 700, 'Access management, change management, operations'),
('ENG-2024-005', 'AML/KYC Effectiveness', 'Review of anti-money laundering controls', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-AFF-RET'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2024' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 6, 'High', '2024-06-01', '2024-08-31', '2024-06-01', 550, 'Customer due diligence, transaction monitoring, reporting'),
-- MedCare Holdings engagements
('ENG-2025-006', 'Clinical Quality Assurance', 'Review of clinical quality and patient safety', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-MED-HOSP'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025/26' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-002')), 2, 'Critical', '2025-08-01', '2025-10-31', '2025-08-01', 650, 'Clinical protocols, incident reporting, quality metrics'),
('ENG-2025-007', 'Pharmaceutical Supply Chain', 'Audit of drug supply chain and inventory', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-MED-PHARM'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025/26' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-002')), 1, 'High', '2025-09-01', '2025-11-30', NULL, 500, 'Procurement, storage, distribution, expiry management'),
('ENG-2025-008', 'HIPAA Compliance Review', 'US healthcare data privacy compliance', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-US'), (SELECT id FROM business_units WHERE code = 'BU-MED-DIAG'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025/26' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-002')), 3, 'High', '2025-07-15', '2025-09-15', '2025-07-15', 400, 'PHI protection, access controls, breach notification'),
-- TechNova Solutions engagements
('ENG-2025-009', 'Software Development Lifecycle', 'Review of SDLC and DevOps practices', 'IT', (SELECT id FROM audit_clients WHERE code = 'CLI-003'), (SELECT id FROM audit_regions WHERE code = 'REG-US'), (SELECT id FROM business_units WHERE code = 'BU-TECH-DEV'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-003')), 5, 'Medium', '2025-02-01', '2025-04-30', '2025-02-01', 500, 'Code review, testing, deployment, version control'),
('ENG-2025-010', 'Cloud Security Assessment', 'Security review of cloud infrastructure', 'IT', (SELECT id FROM audit_clients WHERE code = 'CLI-003'), (SELECT id FROM audit_regions WHERE code = 'REG-SG'), (SELECT id FROM business_units WHERE code = 'BU-TECH-CLOUD'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-003')), 2, 'Critical', '2025-03-01', '2025-05-31', '2025-03-01', 600, 'Infrastructure security, data protection, access management'),
('ENG-2025-011', 'SOC 2 Type II Preparation', 'Prepare for SOC 2 certification audit', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-003'), (SELECT id FROM audit_regions WHERE code = 'REG-US'), (SELECT id FROM business_units WHERE code = 'BU-TECH-CLOUD'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-003')), 4, 'High', '2025-05-01', '2025-07-31', '2025-05-01', 450, 'Security, availability, processing integrity, confidentiality'),
('ENG-2025-012', 'Penetration Testing', 'Annual penetration testing of products', 'IT', (SELECT id FROM audit_clients WHERE code = 'CLI-003'), (SELECT id FROM audit_regions WHERE code = 'REG-DE'), (SELECT id FROM business_units WHERE code = 'BU-TECH-SEC'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-003')), 6, 'High', '2024-11-01', '2024-12-15', '2024-11-01', 300, 'Network, application, social engineering testing'),
-- Global Retail Group engagements
('ENG-2025-013', 'Store Inventory Management', 'Audit of store inventory controls', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-GRG-STORES'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025/26' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-004')), 2, 'Medium', '2025-05-01', '2025-07-31', '2025-05-01', 550, 'Stock counts, shrinkage, receiving, transfers'),
('ENG-2025-014', 'E-Commerce Platform Security', 'Security review of online platform', 'IT', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-GRG-ECOM'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025/26' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-004')), 3, 'High', '2025-04-15', '2025-06-30', '2025-04-15', 480, 'Payment security, customer data, fraud prevention'),
('ENG-2025-015', 'Supply Chain Resilience', 'Review of supply chain risk management', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-DE'), (SELECT id FROM business_units WHERE code = 'BU-GRG-SUPPLY'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025/26' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-004')), 1, 'High', '2025-06-01', '2025-08-31', NULL, 520, 'Supplier management, logistics, business continuity'),
('ENG-2025-016', 'GDPR Compliance', 'EU data protection compliance review', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-GRG-ECOM'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025/26' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-004')), 4, 'High', '2025-03-01', '2025-05-31', '2025-03-01', 400, 'Data processing, consent, subject rights, retention'),
-- Energy Partners engagements
('ENG-2025-017', 'Power Plant Safety', 'Health and safety compliance at generation facilities', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-EP-GEN'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-005')), 2, 'Critical', '2025-01-15', '2025-03-31', '2025-01-15', 600, 'OHS compliance, incident management, training'),
('ENG-2025-018', 'Revenue Assurance', 'Review of billing and revenue recognition', 'Financial', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-EP-DIST'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-005')), 3, 'High', '2025-02-01', '2025-04-30', '2025-02-01', 450, 'Meter reading, billing accuracy, collections'),
('ENG-2025-019', 'Environmental Compliance', 'Environmental regulatory compliance', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-EP-GEN'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-005')), 4, 'High', '2025-04-01', '2025-06-30', '2025-04-01', 400, 'Emissions, waste management, permits'),
('ENG-2025-020', 'Renewable Projects Review', 'Audit of renewable energy projects', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-KE'), (SELECT id FROM business_units WHERE code = 'BU-EP-RENEW'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-005')), 1, 'Medium', '2025-07-01', '2025-09-30', NULL, 350, 'Project governance, contractor management, performance'),
-- Additional historical engagements for YoY trends
('ENG-2024-021', 'Corporate Lending Review 2024', 'Annual review of corporate lending', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-AFF-CORP'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2024' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 6, 'High', '2024-01-15', '2024-03-15', '2024-01-15', 750, 'Credit origination and monitoring'),
('ENG-2024-022', 'IT General Controls 2024', 'Annual ITGC assessment', 'IT', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), NULL, (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2024' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 6, 'High', '2024-04-01', '2024-06-30', '2024-04-01', 680, 'Access, change management, operations'),
('ENG-2024-023', 'Clinical Quality 2024', 'Clinical quality review', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-MED-HOSP'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2024/25' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-002')), 6, 'Critical', '2024-08-01', '2024-10-31', '2024-08-01', 620, 'Clinical protocols and safety'),
('ENG-2024-024', 'Store Operations 2024', 'Retail store audit', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-GRG-STORES'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2024/25' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-004')), 6, 'Medium', '2024-05-01', '2024-07-31', '2024-05-01', 530, 'Inventory and cash handling'),
('ENG-2024-025', 'Power Plant Safety 2024', 'H&S compliance audit', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-EP-GEN'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2024' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-005')), 6, 'Critical', '2024-01-15', '2024-03-31', '2024-01-15', 580, 'OHS compliance'),
-- More 2023 historical data
('ENG-2023-026', 'Corporate Banking 2023', 'Corporate banking review', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-AFF-CORP'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2023' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 6, 'High', '2023-01-15', '2023-03-15', '2023-01-15', 700, 'Credit risk management'),
('ENG-2023-027', 'Treasury Operations 2023', 'Treasury compliance', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-001'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-AFF-TREAS'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2023' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001')), 6, 'Critical', '2023-03-01', '2023-05-31', '2023-03-01', 480, 'Market risk and compliance'),
('ENG-2023-028', 'Hospital Services 2023', 'Clinical quality 2023', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-002'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-MED-HOSP'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2023/24' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-002')), 6, 'Critical', '2023-08-01', '2023-10-31', '2023-08-01', 600, 'Patient safety'),
('ENG-2023-029', 'Power Generation 2023', 'Safety compliance', 'Compliance', (SELECT id FROM audit_clients WHERE code = 'CLI-005'), (SELECT id FROM audit_regions WHERE code = 'REG-ZA'), (SELECT id FROM business_units WHERE code = 'BU-EP-GEN'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2023' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-005')), 6, 'Critical', '2023-01-15', '2023-03-31', '2023-01-15', 550, 'OHS compliance'),
('ENG-2023-030', 'Retail Operations 2023', 'Store operations review', 'Operational', (SELECT id FROM audit_clients WHERE code = 'CLI-004'), (SELECT id FROM audit_regions WHERE code = 'REG-GB'), (SELECT id FROM business_units WHERE code = 'BU-GRG-STORES'), (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2023/24' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-004')), 6, 'Medium', '2023-05-01', '2023-07-31', '2023-05-01', 500, 'Inventory controls')
ON CONFLICT (engagement_code) DO NOTHING;

-- 6.6 AUDIT FINDINGS (50+ findings across engagements)
INSERT INTO audit_findings (finding_code, engagement_id, title, description, root_cause, business_impact, finding_type, severity_id, status_id, treatment_status_id, owner_name, owner_email, due_date, management_response, identified_date, repeat_finding) VALUES
-- Critical findings
('FND-2025-001', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-003'), 'Inadequate Segregation of Duties in Treasury', 'Single trader can initiate, approve, and settle large transactions without independent review', 'Staffing constraints and outdated system design', 'Potential for unauthorized trading losses and regulatory penalties', 'Control Deficiency', 1, 1, 2, 'James van der Berg', 'j.vanderberg@affine.co.za', '2025-06-30', 'Implementing dual authorization for trades over R10M', '2025-03-15', FALSE),
('FND-2025-002', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Medication Administration Errors', 'Multiple instances of incorrect medication dosage administered to patients', 'Inadequate verification procedures and understaffing', 'Patient safety risk and potential liability', 'Process Gap', 1, 2, 2, 'Dr. Robert Hughes', 'r.hughes@medcare.com', '2025-09-30', 'Implementing barcode scanning for medication verification', '2025-08-20', TRUE),
('FND-2025-003', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-010'), 'Unpatched Critical Vulnerabilities', 'Production servers running with known critical CVEs for over 90 days', 'Lack of automated patch management', 'Risk of data breach and service disruption', 'Security Vulnerability', 1, 1, 1, 'Raj Patel', 'r.patel@technova.io', '2025-04-15', 'Implementing automated patch management solution', '2025-03-10', FALSE),
('FND-2025-004', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'Incomplete Safety Training Records', 'Unable to verify completion of mandatory safety training for 25% of plant workers', 'Manual training tracking system', 'Regulatory non-compliance and safety risk', 'Compliance Issue', 1, 2, 2, 'Thabo Mabasa', 't.mabasa@energypartners.co.za', '2025-05-31', 'Migrating to digital training management system', '2025-02-01', TRUE),
-- High severity findings
('FND-2025-005', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Excessive Credit Limit Exceptions', 'High volume of credit limit breaches approved without proper justification', 'Pressure to meet lending targets', 'Increased credit risk exposure', 'Control Deficiency', 2, 1, 1, 'Peter Molefe', 'p.molefe@affine.co.za', '2025-04-30', 'Reviewing exception approval process', '2025-02-10', FALSE),
('FND-2025-006', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Incomplete Credit File Documentation', '35% of sampled credit files missing required supporting documentation', 'Inconsistent file management practices', 'Regulatory and credit decision risk', 'Process Gap', 2, 2, 2, 'Peter Molefe', 'p.molefe@affine.co.za', '2025-05-15', 'Implementing checklist verification', '2025-02-15', FALSE),
('FND-2025-007', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Cash Handling Discrepancies', 'Recurring differences between physical cash and system records at multiple branches', 'Inadequate dual control procedures', 'Financial loss and fraud risk', 'Control Deficiency', 2, 1, 2, 'Linda Dlamini', 'l.dlamini@affine.co.za', '2025-05-31', 'Enhancing cash count procedures', '2025-03-01', FALSE),
('FND-2025-008', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'Privileged Access Not Reviewed', 'No evidence of quarterly privileged access reviews for past 6 months', 'Manual review process breakdown', 'Unauthorized access risk', 'Control Deficiency', 2, 3, 3, 'IT Security Manager', 'itsec@affine.co.za', '2025-07-31', 'Review completed, implementing automated reminders', '2025-04-20', TRUE),
('FND-2025-009', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-008'), 'PHI Stored on Unencrypted Laptops', 'Patient health information found on unencrypted portable devices', 'Lack of device management enforcement', 'HIPAA violation and data breach risk', 'Compliance Issue', 2, 1, 2, 'Mark Stevens', 'm.stevens@medcare.com', '2025-10-15', 'Rolling out full disk encryption', '2025-08-01', FALSE),
('FND-2025-010', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Insufficient Code Review Coverage', 'Only 40% of code changes undergo peer review before deployment', 'Developer time constraints', 'Quality and security defects', 'Process Gap', 2, 2, 2, 'Jennifer Lee', 'j.lee@technova.io', '2025-05-31', 'Implementing mandatory PR reviews', '2025-02-28', FALSE),
('FND-2025-011', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Inventory Shrinkage Above Threshold', 'Shrinkage rate of 2.8% exceeds acceptable threshold of 1.5%', 'Weak physical security and stock monitoring', 'Significant financial loss', 'Control Deficiency', 2, 1, 1, 'Tom Wilson', 't.wilson@grg.co.uk', '2025-08-31', 'Installing additional security cameras and RFID tagging', '2025-05-15', FALSE),
('FND-2025-012', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-014'), 'PCI DSS Compliance Gaps', 'Several requirements not fully met including network segmentation', 'Recent platform migration', 'Payment card data breach risk', 'Compliance Issue', 2, 2, 2, 'Sophie Turner', 's.turner@grg.co.uk', '2025-07-31', 'Engaging PCI consultant for remediation', '2025-05-01', FALSE),
('FND-2025-013', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-018'), 'Unbilled Consumption', 'Estimated R15M in electricity consumption not billed due to faulty meters', 'Aging meter infrastructure', 'Revenue leakage', 'Data Quality', 2, 1, 2, 'Nomsa Khumalo', 'n.khumalo@energypartners.co.za', '2025-06-30', 'Accelerating smart meter rollout', '2025-02-20', FALSE),
-- Medium severity findings
('FND-2025-014', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Delayed Credit Reviews', 'Annual credit reviews completed late for 20% of corporate clients', 'Resource constraints', 'Credit risk monitoring gaps', 'Process Gap', 3, 2, 2, 'Peter Molefe', 'p.molefe@affine.co.za', '2025-06-30', 'Adding additional credit analyst', '2025-02-20', FALSE),
('FND-2025-015', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Incomplete Customer ID Verification', 'KYC documents not verified against original for 15% of new accounts', 'Training gaps', 'AML compliance risk', 'Compliance Issue', 3, 3, 3, 'Linda Dlamini', 'l.dlamini@affine.co.za', '2025-06-15', 'Refresher training completed', '2025-03-10', FALSE),
('FND-2025-016', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'Change Management Documentation Gaps', 'Emergency changes lacking post-implementation documentation', 'Time pressure', 'Audit trail and accountability gaps', 'Process Gap', 3, 1, 1, 'IT Change Manager', 'itchange@affine.co.za', '2025-08-15', 'Updating change management procedures', '2025-05-01', FALSE),
('FND-2025-017', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Incomplete Incident Reports', 'Clinical incident reports missing required root cause analysis', 'Staff unfamiliarity with requirements', 'Reduced learning from incidents', 'Process Gap', 3, 2, 2, 'Quality Manager', 'quality@medcare.com', '2025-10-31', 'Revising incident report template', '2025-08-25', FALSE),
('FND-2025-018', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Outdated Third-Party Libraries', 'Multiple applications using deprecated library versions', 'Lack of dependency management', 'Security vulnerabilities', 'Security Vulnerability', 3, 2, 2, 'Jennifer Lee', 'j.lee@technova.io', '2025-06-30', 'Implementing Dependabot', '2025-03-05', FALSE),
('FND-2025-019', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-011'), 'Incomplete Vendor Risk Assessments', 'Annual risk assessments not completed for 30% of critical vendors', 'Manual tracking process', 'Third-party risk exposure', 'Process Gap', 3, 1, 1, 'Procurement Manager', 'procurement@technova.io', '2025-08-31', 'Implementing vendor management system', '2025-05-20', FALSE),
('FND-2025-020', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Stock Count Frequency', 'Cycle counts not performed at required frequency in 5 stores', 'Staff shortages', 'Inventory accuracy concerns', 'Control Deficiency', 3, 2, 2, 'Regional Manager', 'regional@grg.co.uk', '2025-08-15', 'Reviewing staffing levels', '2025-05-20', FALSE),
('FND-2025-021', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-016'), 'Data Retention Policy Gaps', 'Customer data retained beyond required periods', 'System limitations', 'GDPR compliance risk', 'Compliance Issue', 3, 1, 2, 'Data Protection Officer', 'dpo@grg.co.uk', '2025-06-30', 'Implementing automated data deletion', '2025-04-01', FALSE),
('FND-2025-022', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'Permit Renewal Delays', 'Operating permits renewed after expiry date in 2 instances', 'Manual tracking', 'Regulatory risk', 'Compliance Issue', 3, 4, 4, 'Compliance Manager', 'compliance@energypartners.co.za', '2025-04-30', 'Permits renewed, implementing reminder system', '2025-02-15', FALSE),
('FND-2025-023', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-019'), 'Environmental Monitoring Gaps', 'Air quality monitoring data incomplete for 3 months', 'Equipment malfunction', 'Regulatory reporting gaps', 'Data Quality', 3, 3, 3, 'Environmental Manager', 'enviro@energypartners.co.za', '2025-07-31', 'Equipment replaced, backfilling data where possible', '2025-04-20', FALSE),
-- Low severity findings
('FND-2025-024', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Branch Opening Procedures', 'Minor deviations from standard branch opening checklist', 'Staff convenience', 'Operational inconsistency', 'Process Gap', 4, 4, 4, 'Branch Manager', 'branch@affine.co.za', '2025-04-30', 'Addressed in team meeting', '2025-03-15', FALSE),
('FND-2025-025', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'Service Account Documentation', 'Service account purposes not fully documented', 'Documentation oversight', 'Access management clarity', 'Process Gap', 4, 3, 3, 'IT Admin', 'itadmin@affine.co.za', '2025-08-31', 'Documentation update in progress', '2025-05-10', FALSE),
('FND-2025-026', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Code Comment Standards', 'Inconsistent code commenting practices across teams', 'Lack of standards', 'Code maintainability', 'Process Gap', 4, 2, 2, 'Tech Lead', 'techlead@technova.io', '2025-07-31', 'Developing coding standards document', '2025-03-10', FALSE),
-- Historical findings (closed) for trends
('FND-2024-027', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2024-021'), 'Credit Limit Exceptions 2024', 'Similar credit limit exception issues as current year', 'Target pressure', 'Credit risk', 'Control Deficiency', 2, 4, 4, 'Peter Molefe', 'p.molefe@affine.co.za', '2024-05-31', 'Process improvements implemented', '2024-02-10', FALSE),
('FND-2024-028', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2024-022'), 'Access Reviews 2024', 'Delayed privileged access reviews', 'Manual process', 'Unauthorized access risk', 'Control Deficiency', 2, 4, 4, 'IT Security', 'itsec@affine.co.za', '2024-08-31', 'Reviews completed', '2024-05-01', FALSE),
('FND-2024-029', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2024-023'), 'Clinical Documentation 2024', 'Incomplete clinical incident documentation', 'Staff training', 'Learning gaps', 'Process Gap', 3, 4, 4, 'Quality Manager', 'quality@medcare.com', '2024-12-31', 'Training completed', '2024-09-01', FALSE),
('FND-2024-030', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2024-024'), 'Inventory Shrinkage 2024', 'Elevated shrinkage at select stores', 'Security gaps', 'Financial loss', 'Control Deficiency', 2, 4, 4, 'Regional Manager', 'regional@grg.co.uk', '2024-09-30', 'Security enhanced', '2024-06-01', FALSE),
('FND-2024-031', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2024-025'), 'Safety Training 2024', 'Training record gaps', 'Manual system', 'Compliance risk', 'Compliance Issue', 1, 4, 4, 'HR Manager', 'hr@energypartners.co.za', '2024-05-31', 'Records updated', '2024-02-15', FALSE),
-- More findings for comprehensive data
('FND-2025-032', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-003'), 'Market Risk Limit Breaches', 'Trading desk exceeded VaR limits on 5 occasions without escalation', 'System alerting failure', 'Regulatory breach and financial risk', 'Control Deficiency', 2, 1, 1, 'Risk Manager', 'risk@affine.co.za', '2025-06-15', 'Implementing automated escalation', '2025-03-20', FALSE),
('FND-2025-033', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-007'), 'Cold Chain Temperature Excursions', 'Temperature monitoring gaps for refrigerated pharmaceuticals', 'Equipment reliability', 'Product efficacy risk', 'Control Deficiency', 2, 1, 1, 'Supply Chain Manager', 'supply@medcare.com', '2025-12-31', 'Installing redundant monitoring', '2025-09-15', FALSE),
('FND-2025-034', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-010'), 'Multi-Factor Authentication Gaps', 'MFA not enforced for all administrative access', 'Legacy system constraints', 'Account compromise risk', 'Security Vulnerability', 2, 2, 2, 'Security Lead', 'security@technova.io', '2025-05-31', 'MFA rollout in progress', '2025-03-15', FALSE),
('FND-2025-035', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-012'), 'Web Application Vulnerabilities', 'SQL injection vulnerabilities found in customer portal', 'Code review gaps', 'Data breach risk', 'Security Vulnerability', 1, 4, 4, 'Dev Lead', 'dev@technova.io', '2025-01-15', 'Vulnerabilities patched', '2024-11-20', FALSE),
('FND-2025-036', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-014'), 'Payment Fraud Prevention', 'Insufficient velocity checks on card transactions', 'Configuration oversight', 'Fraud loss exposure', 'Control Deficiency', 2, 2, 2, 'Payments Manager', 'payments@grg.co.uk', '2025-07-15', 'Implementing enhanced rules', '2025-05-10', FALSE),
('FND-2025-037', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-015'), 'Supplier Financial Monitoring', 'No ongoing monitoring of critical supplier financial health', 'Process gap', 'Supply continuity risk', 'Process Gap', 3, 1, 1, 'Procurement Head', 'procurement@grg.co.uk', '2025-09-30', 'Implementing quarterly reviews', '2025-06-20', FALSE),
('FND-2025-038', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-018'), 'Meter Data Validation', 'Insufficient validation of large consumption variances', 'System limitations', 'Billing accuracy risk', 'Data Quality', 3, 2, 2, 'Billing Manager', 'billing@energypartners.co.za', '2025-05-31', 'Implementing exception reports', '2025-02-25', FALSE),
('FND-2025-039', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-019'), 'Emissions Reporting Accuracy', 'Manual calculations introduce errors in emissions reports', 'Spreadsheet reliance', 'Regulatory reporting risk', 'Data Quality', 3, 3, 3, 'Environmental Lead', 'enviro@energypartners.co.za', '2025-07-31', 'Implementing automated calculations', '2025-05-01', FALSE),
-- Additional overdue findings for status distribution
('FND-2024-040', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2024-021'), 'Credit Model Validation', 'Credit scoring model not independently validated', 'Resource constraints', 'Model risk', 'Control Deficiency', 2, 5, 2, 'Model Risk Manager', 'modelrisk@affine.co.za', '2024-12-31', 'Validation scheduled for Q2', '2024-03-01', FALSE),
('FND-2024-041', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2024-023'), 'Patient Consent Forms', 'Consent forms not consistently obtained for procedures', 'Process adherence', 'Legal liability', 'Compliance Issue', 2, 5, 2, 'Clinical Director', 'clinical@medcare.com', '2024-11-30', 'Implementing digital consent', '2024-09-15', FALSE),
('FND-2025-042', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Collateral Valuation Timeliness', 'Property valuations older than 12 months for secured loans', 'Valuation backlog', 'Credit risk underestimation', 'Control Deficiency', 2, 1, 1, 'Credit Admin', 'creditadmin@affine.co.za', '2025-05-31', 'Engaging additional valuers', '2025-02-28', FALSE),
('FND-2025-043', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Infection Control Compliance', 'Hand hygiene compliance below 80% target in ICU', 'Behavioral compliance', 'HAI risk', 'Compliance Issue', 2, 2, 2, 'Infection Control', 'ic@medcare.com', '2025-10-31', 'Implementing monitoring program', '2025-08-30', FALSE),
('FND-2025-044', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-011'), 'Business Continuity Testing', 'DR failover not tested within required timeframe', 'Schedule conflicts', 'Recovery capability uncertainty', 'Control Deficiency', 2, 1, 1, 'BC Manager', 'bc@technova.io', '2025-08-15', 'Test scheduled for July', '2025-06-01', FALSE),
('FND-2025-045', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Receiving Verification', 'Goods received not consistently verified against PO', 'Staff shortcuts', 'Inventory accuracy and fraud risk', 'Control Deficiency', 3, 2, 2, 'Warehouse Manager', 'warehouse@grg.co.uk', '2025-08-31', 'Implementing mandatory scanning', '2025-06-01', FALSE),
('FND-2025-046', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'Contractor Safety Induction', 'Contractor safety briefings not consistently documented', 'Manual process', 'Liability risk', 'Compliance Issue', 3, 2, 2, 'Site Manager', 'site@energypartners.co.za', '2025-05-15', 'Implementing digital sign-off', '2025-02-20', FALSE),
('FND-2025-047', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Branch Physical Security', 'Security camera coverage gaps identified at 3 branches', 'Equipment failure', 'Physical security risk', 'Control Deficiency', 3, 3, 3, 'Security Manager', 'security@affine.co.za', '2025-06-30', 'Cameras being installed', '2025-03-25', FALSE),
('FND-2025-048', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-008'), 'Data Backup Verification', 'Backup restoration not tested for critical systems', 'Process oversight', 'Data recovery risk', 'Control Deficiency', 2, 1, 1, 'IT Operations', 'itops@medcare.com', '2025-11-30', 'Test schedule being created', '2025-08-10', FALSE),
('FND-2025-049', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Production Access Controls', 'Developers with direct production database access', 'Operational convenience', 'Data integrity risk', 'Control Deficiency', 2, 2, 2, 'DBA Lead', 'dba@technova.io', '2025-06-15', 'Implementing break-glass procedures', '2025-03-01', FALSE),
('FND-2025-050', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-016'), 'Cookie Consent Management', 'Website cookie consent not compliant with GDPR requirements', 'Third-party integration', 'Regulatory penalty risk', 'Compliance Issue', 3, 3, 3, 'Legal Team', 'legal@grg.co.uk', '2025-06-15', 'Implementing consent management platform', '2025-04-05', FALSE)
ON CONFLICT (finding_code) DO NOTHING;

-- 6.7 CONTROL TESTS (100+ tests across engagements)
INSERT INTO control_tests (test_code, engagement_id, control_name, control_description, control_type, control_category, tester_name, test_procedure, sample_size, exceptions_found, test_date, result_id, conclusion, evidence_reference) VALUES
-- Affine Financial Services control tests
('TST-2025-001', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Credit Approval Authority', 'Credit limits approved within delegated authority levels', 'Preventive', 'Manual', 'Audit Senior', 'Selected sample of credit approvals and verified approval authority', 30, 2, '2025-02-01', 1, 'Control effective with minor exceptions', 'WP-CL-001'),
('TST-2025-002', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Credit File Documentation', 'Required documents maintained in credit files', 'Detective', 'Manual', 'Audit Senior', 'Reviewed credit files for completeness against checklist', 25, 9, '2025-02-05', 3, 'Control ineffective - significant documentation gaps', 'WP-CL-002'),
('TST-2025-003', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Collateral Valuation', 'Collateral values updated annually', 'Detective', 'Manual', 'Audit Manager', 'Verified valuation dates for secured facilities', 20, 5, '2025-02-10', 2, 'Partially effective - backlog identified', 'WP-CL-003'),
('TST-2025-004', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Credit Risk Rating', 'Risk ratings reviewed and updated quarterly', 'Detective', 'IT-Dependent Manual', 'Audit Senior', 'Tested risk rating changes against supporting analysis', 30, 3, '2025-02-15', 1, 'Control effective', 'WP-CL-004'),
('TST-2025-005', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Cash Count Reconciliation', 'Daily cash counts reconciled to system', 'Detective', 'Manual', 'Audit Associate', 'Observed cash counts and reviewed reconciliations', 15, 4, '2025-03-01', 2, 'Partially effective - discrepancies noted', 'WP-BR-001'),
('TST-2025-006', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Teller Transaction Limits', 'System enforces teller transaction limits', 'Preventive', 'Automated', 'Audit Senior', 'Tested transaction limit enforcement in system', 50, 0, '2025-03-05', 1, 'Control effective', 'WP-BR-002'),
('TST-2025-007', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Dual Authorization', 'High-value transactions require dual authorization', 'Preventive', 'IT-Dependent Manual', 'Audit Senior', 'Tested sample of high-value transactions', 20, 1, '2025-03-10', 1, 'Control effective', 'WP-BR-003'),
('TST-2025-008', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Customer Verification', 'Customer identity verified for account opening', 'Preventive', 'Manual', 'Audit Associate', 'Reviewed KYC documentation for new accounts', 30, 5, '2025-03-15', 2, 'Partially effective - verification gaps', 'WP-BR-004'),
('TST-2025-009', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-003'), 'Trading Limit Monitoring', 'System monitors and alerts on limit breaches', 'Detective', 'Automated', 'IT Auditor', 'Reviewed limit breach alerts and escalation', 40, 5, '2025-04-01', 2, 'Partially effective - escalation gaps', 'WP-TR-001'),
('TST-2025-010', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-003'), 'Trade Confirmation', 'All trades confirmed within T+1', 'Detective', 'IT-Dependent Manual', 'Audit Senior', 'Tested confirmation timeliness for sample trades', 50, 3, '2025-04-05', 1, 'Control effective', 'WP-TR-002'),
('TST-2025-011', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-003'), 'Segregation of Duties', 'Front/back office segregation maintained', 'Preventive', 'Manual', 'Audit Manager', 'Reviewed access rights and reporting lines', 10, 2, '2025-04-10', 3, 'Control ineffective - SOD violations', 'WP-TR-003'),
('TST-2025-012', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'User Access Provisioning', 'Access provisioned based on approved requests', 'Preventive', 'IT-Dependent Manual', 'IT Auditor', 'Tested sample of access provisioning requests', 25, 2, '2025-05-01', 1, 'Control effective', 'WP-IT-001'),
('TST-2025-013', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'Privileged Access Review', 'Quarterly review of privileged accounts', 'Detective', 'Manual', 'IT Auditor', 'Reviewed evidence of privileged access reviews', 4, 2, '2025-05-05', 3, 'Control ineffective - reviews not completed', 'WP-IT-002'),
('TST-2025-014', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'User Termination', 'Access removed promptly upon termination', 'Corrective', 'IT-Dependent Manual', 'IT Auditor', 'Tested access removal for terminated users', 15, 1, '2025-05-10', 1, 'Control effective', 'WP-IT-003'),
('TST-2025-015', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'Change Approval', 'Changes approved before implementation', 'Preventive', 'Manual', 'IT Auditor', 'Reviewed change records for approval evidence', 30, 4, '2025-05-15', 2, 'Partially effective - emergency change gaps', 'WP-IT-004'),
-- MedCare Holdings control tests
('TST-2025-016', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Medication Verification', 'Five rights verification before administration', 'Preventive', 'Manual', 'Clinical Auditor', 'Observed medication administration process', 50, 8, '2025-08-20', 3, 'Control ineffective - verification gaps', 'WP-CQ-001'),
('TST-2025-017', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Clinical Documentation', 'Patient notes documented within 24 hours', 'Detective', 'IT-Dependent Manual', 'Clinical Auditor', 'Tested documentation timeliness', 40, 5, '2025-08-25', 2, 'Partially effective', 'WP-CQ-002'),
('TST-2025-018', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Incident Reporting', 'Clinical incidents reported within 4 hours', 'Detective', 'Manual', 'Clinical Auditor', 'Reviewed incident reporting timeliness', 20, 3, '2025-08-30', 1, 'Control effective', 'WP-CQ-003'),
('TST-2025-019', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Patient Consent', 'Informed consent obtained before procedures', 'Preventive', 'Manual', 'Clinical Auditor', 'Reviewed consent forms for procedures', 35, 6, '2025-09-05', 2, 'Partially effective - gaps identified', 'WP-CQ-004'),
('TST-2025-020', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-008'), 'PHI Access Logging', 'All PHI access logged and reviewable', 'Detective', 'Automated', 'IT Auditor', 'Tested access logging completeness', 100, 0, '2025-07-25', 1, 'Control effective', 'WP-HP-001'),
('TST-2025-021', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-008'), 'Device Encryption', 'Portable devices encrypted', 'Preventive', 'Automated', 'IT Auditor', 'Scanned devices for encryption status', 50, 12, '2025-07-30', 3, 'Control ineffective - unencrypted devices', 'WP-HP-002'),
('TST-2025-022', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-008'), 'Breach Notification', 'Breach procedures documented and tested', 'Corrective', 'Manual', 'IT Auditor', 'Reviewed breach response procedures', 1, 0, '2025-08-05', 1, 'Control effective', 'WP-HP-003'),
-- TechNova Solutions control tests
('TST-2025-023', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Code Review', 'Peer review before merge to main branch', 'Preventive', 'IT-Dependent Manual', 'IT Auditor', 'Tested sample of merged pull requests', 40, 24, '2025-02-20', 3, 'Control ineffective - low review coverage', 'WP-SD-001'),
('TST-2025-024', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Automated Testing', 'Unit tests run on all builds', 'Detective', 'Automated', 'IT Auditor', 'Reviewed CI pipeline test execution', 30, 2, '2025-02-25', 1, 'Control effective', 'WP-SD-002'),
('TST-2025-025', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Deployment Approval', 'Production deployments require approval', 'Preventive', 'IT-Dependent Manual', 'IT Auditor', 'Tested deployment approval workflow', 20, 3, '2025-03-01', 1, 'Control effective', 'WP-SD-003'),
('TST-2025-026', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-009'), 'Rollback Capability', 'Failed deployments can be rolled back', 'Corrective', 'Automated', 'IT Auditor', 'Tested rollback procedure', 5, 0, '2025-03-05', 1, 'Control effective', 'WP-SD-004'),
('TST-2025-027', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-010'), 'Vulnerability Scanning', 'Weekly vulnerability scans executed', 'Detective', 'Automated', 'Security Auditor', 'Reviewed scan execution logs', 12, 2, '2025-03-15', 1, 'Control effective', 'WP-CS-001'),
('TST-2025-028', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-010'), 'Patch Management', 'Critical patches applied within 72 hours', 'Corrective', 'IT-Dependent Manual', 'Security Auditor', 'Tested patch deployment timeliness', 20, 8, '2025-03-20', 3, 'Control ineffective - patching delays', 'WP-CS-002'),
('TST-2025-029', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-010'), 'Network Segmentation', 'Production network isolated from corporate', 'Preventive', 'Automated', 'Security Auditor', 'Tested network access restrictions', 15, 3, '2025-03-25', 2, 'Partially effective', 'WP-CS-003'),
('TST-2025-030', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-010'), 'MFA Enforcement', 'MFA required for administrative access', 'Preventive', 'Automated', 'Security Auditor', 'Tested MFA configuration', 25, 5, '2025-03-30', 2, 'Partially effective - coverage gaps', 'WP-CS-004'),
('TST-2025-031', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-011'), 'Incident Response', 'Security incidents escalated per procedure', 'Detective', 'Manual', 'Security Auditor', 'Reviewed incident response records', 10, 1, '2025-06-01', 1, 'Control effective', 'WP-SC-001'),
('TST-2025-032', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-011'), 'Access Monitoring', 'Suspicious access patterns detected and reviewed', 'Detective', 'Automated', 'Security Auditor', 'Tested SIEM alert generation', 50, 3, '2025-06-05', 1, 'Control effective', 'WP-SC-002'),
-- Global Retail Group control tests
('TST-2025-033', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Inventory Count Accuracy', 'Cycle counts accurate within tolerance', 'Detective', 'Manual', 'Audit Senior', 'Observed and reperformed cycle counts', 100, 15, '2025-05-20', 2, 'Partially effective - variances noted', 'WP-IN-001'),
('TST-2025-034', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Receiving Verification', 'Goods verified against PO on receipt', 'Preventive', 'Manual', 'Audit Associate', 'Tested receiving documentation', 30, 8, '2025-05-25', 2, 'Partially effective', 'WP-IN-002'),
('TST-2025-035', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Stock Transfer Authorization', 'Inter-store transfers authorized', 'Preventive', 'IT-Dependent Manual', 'Audit Senior', 'Tested transfer authorization', 25, 2, '2025-05-30', 1, 'Control effective', 'WP-IN-003'),
('TST-2025-036', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Shrinkage Investigation', 'High shrinkage stores investigated', 'Corrective', 'Manual', 'Audit Manager', 'Reviewed shrinkage investigation files', 10, 3, '2025-06-05', 2, 'Partially effective', 'WP-IN-004'),
('TST-2025-037', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-014'), 'Payment Card Encryption', 'Card data encrypted in transit and at rest', 'Preventive', 'Automated', 'IT Auditor', 'Tested encryption implementation', 1, 0, '2025-05-01', 1, 'Control effective', 'WP-EC-001'),
('TST-2025-038', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-014'), 'Fraud Detection Rules', 'Suspicious transactions flagged for review', 'Detective', 'Automated', 'IT Auditor', 'Tested fraud detection rules', 100, 8, '2025-05-05', 2, 'Partially effective - rule gaps', 'WP-EC-002'),
('TST-2025-039', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-014'), 'PCI Network Segmentation', 'Cardholder data environment segmented', 'Preventive', 'Automated', 'IT Auditor', 'Tested network segmentation', 20, 4, '2025-05-10', 2, 'Partially effective', 'WP-EC-003'),
('TST-2025-040', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-016'), 'Consent Collection', 'Marketing consent obtained and recorded', 'Preventive', 'IT-Dependent Manual', 'Audit Senior', 'Tested consent collection process', 50, 5, '2025-04-01', 2, 'Partially effective', 'WP-GD-001'),
('TST-2025-041', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-016'), 'Data Subject Access', 'DSARs processed within 30 days', 'Corrective', 'Manual', 'Audit Senior', 'Tested DSAR response timeliness', 15, 2, '2025-04-05', 1, 'Control effective', 'WP-GD-002'),
('TST-2025-042', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-016'), 'Data Retention', 'Data deleted per retention schedule', 'Corrective', 'IT-Dependent Manual', 'IT Auditor', 'Tested data deletion process', 20, 6, '2025-04-10', 3, 'Control ineffective - retention gaps', 'WP-GD-003'),
-- Energy Partners control tests
('TST-2025-043', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'Safety Training Completion', 'Mandatory safety training completed', 'Preventive', 'Manual', 'Audit Senior', 'Verified training completion records', 50, 13, '2025-02-01', 3, 'Control ineffective - training gaps', 'WP-HS-001'),
('TST-2025-044', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'PPE Compliance', 'PPE used in required areas', 'Preventive', 'Manual', 'Audit Associate', 'Site observations of PPE usage', 100, 5, '2025-02-05', 1, 'Control effective', 'WP-HS-002'),
('TST-2025-045', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'Incident Investigation', 'Safety incidents investigated timely', 'Corrective', 'Manual', 'Audit Senior', 'Reviewed incident investigation files', 15, 2, '2025-02-10', 1, 'Control effective', 'WP-HS-003'),
('TST-2025-046', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'Permit to Work', 'High-risk work permits issued and controlled', 'Preventive', 'Manual', 'Audit Manager', 'Tested permit issuance process', 20, 3, '2025-02-15', 1, 'Control effective', 'WP-HS-004'),
('TST-2025-047', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-018'), 'Meter Reading Accuracy', 'Meter readings validated against consumption patterns', 'Detective', 'IT-Dependent Manual', 'Audit Senior', 'Tested meter data validation', 50, 10, '2025-02-25', 2, 'Partially effective', 'WP-RA-001'),
('TST-2025-048', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-018'), 'Billing Calculation', 'Bills calculated per approved tariffs', 'Preventive', 'Automated', 'Audit Senior', 'Recalculated sample bills', 30, 2, '2025-03-01', 1, 'Control effective', 'WP-RA-002'),
('TST-2025-049', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-018'), 'Disputed Bills Review', 'Bill disputes investigated and resolved', 'Corrective', 'Manual', 'Audit Associate', 'Reviewed dispute resolution process', 20, 3, '2025-03-05', 1, 'Control effective', 'WP-RA-003'),
('TST-2025-050', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-019'), 'Emissions Monitoring', 'Continuous emissions monitoring operational', 'Detective', 'Automated', 'Environmental Auditor', 'Tested monitoring equipment functionality', 30, 5, '2025-04-20', 2, 'Partially effective - equipment issues', 'WP-EN-001'),
('TST-2025-051', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-019'), 'Waste Disposal', 'Hazardous waste disposed per regulations', 'Corrective', 'Manual', 'Environmental Auditor', 'Reviewed waste disposal manifests', 25, 1, '2025-04-25', 1, 'Control effective', 'WP-EN-002'),
('TST-2025-052', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-019'), 'Permit Compliance', 'Operating permits current and compliant', 'Preventive', 'Manual', 'Environmental Auditor', 'Verified permit status and conditions', 10, 2, '2025-04-30', 2, 'Partially effective - delays noted', 'WP-EN-003'),
-- Additional tests for comprehensive coverage
('TST-2025-053', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Loan Covenant Monitoring', 'Covenant compliance monitored quarterly', 'Detective', 'Manual', 'Audit Senior', 'Tested covenant monitoring process', 20, 2, '2025-02-20', 1, 'Control effective', 'WP-CL-005'),
('TST-2025-054', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Problem Loan Classification', 'Non-performing loans correctly classified', 'Detective', 'IT-Dependent Manual', 'Audit Manager', 'Tested NPL classification accuracy', 25, 3, '2025-02-25', 1, 'Control effective', 'WP-CL-006'),
('TST-2025-055', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-002'), 'Branch Security', 'Security procedures followed at opening/closing', 'Preventive', 'Manual', 'Audit Associate', 'Observed branch opening procedures', 10, 2, '2025-03-20', 1, 'Control effective', 'WP-BR-005'),
('TST-2025-056', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-003'), 'Counterparty Limits', 'Counterparty exposure within limits', 'Preventive', 'IT-Dependent Manual', 'Audit Senior', 'Tested counterparty limit monitoring', 30, 1, '2025-04-15', 1, 'Control effective', 'WP-TR-004'),
('TST-2025-057', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-004'), 'Backup Integrity', 'Backup restore testing performed', 'Detective', 'IT-Dependent Manual', 'IT Auditor', 'Reviewed backup test documentation', 12, 3, '2025-05-20', 2, 'Partially effective', 'WP-IT-005'),
('TST-2025-058', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-006'), 'Hand Hygiene', 'Hand hygiene compliance monitored', 'Preventive', 'Manual', 'Clinical Auditor', 'Observed hand hygiene compliance', 100, 22, '2025-09-10', 3, 'Control ineffective - below target', 'WP-CQ-005'),
('TST-2025-059', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-010'), 'Log Retention', 'Security logs retained per policy', 'Detective', 'Automated', 'Security Auditor', 'Verified log retention periods', 20, 0, '2025-04-01', 1, 'Control effective', 'WP-CS-005'),
('TST-2025-060', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-013'), 'Price Accuracy', 'Shelf prices match system prices', 'Detective', 'Manual', 'Audit Associate', 'Tested price accuracy at stores', 200, 12, '2025-06-10', 2, 'Partially effective', 'WP-IN-005'),
-- More test variety
('TST-2025-061', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-017'), 'Emergency Response Drills', 'Emergency drills conducted quarterly', 'Directive', 'Manual', 'Audit Senior', 'Reviewed drill records and observations', 4, 1, '2025-02-20', 1, 'Control effective', 'WP-HS-005'),
('TST-2025-062', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-018'), 'Credit Collection', 'Overdue accounts followed up timely', 'Corrective', 'Manual', 'Audit Associate', 'Tested collection follow-up process', 30, 5, '2025-03-10', 2, 'Partially effective', 'WP-RA-004'),
('TST-2025-063', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-011'), 'Vendor Due Diligence', 'Critical vendors assessed before onboarding', 'Preventive', 'Manual', 'Audit Senior', 'Tested vendor assessment process', 15, 5, '2025-06-10', 2, 'Partially effective - gaps noted', 'WP-SC-003'),
('TST-2025-064', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-001'), 'Early Warning System', 'Credit early warning indicators monitored', 'Detective', 'Automated', 'IT Auditor', 'Tested EWS alert generation', 50, 4, '2025-03-01', 1, 'Control effective', 'WP-CL-007'),
('TST-2025-065', (SELECT id FROM audit_engagements WHERE engagement_code = 'ENG-2025-014'), 'Session Timeout', 'User sessions timeout after inactivity', 'Preventive', 'Automated', 'IT Auditor', 'Tested session timeout settings', 10, 0, '2025-05-15', 1, 'Control effective', 'WP-EC-004')
ON CONFLICT (test_code) DO NOTHING;

-- ============================================================================
-- PART 7: LINK EXISTING DATA TO HIERARCHY
-- ============================================================================

-- Update existing departments with hierarchy links (if departments table has data)
UPDATE departments SET client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001') WHERE client_id IS NULL AND id <= 3;
UPDATE departments SET client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-002') WHERE client_id IS NULL AND id > 3 AND id <= 6;
UPDATE departments SET business_unit_id = (SELECT id FROM business_units WHERE code = 'BU-AFF-CORP') WHERE business_unit_id IS NULL AND id = 1;
UPDATE departments SET business_unit_id = (SELECT id FROM business_units WHERE code = 'BU-AFF-RET') WHERE business_unit_id IS NULL AND id = 2;

-- Update existing risk assessment references with hierarchy links (if they exist)
UPDATE riskassessmentreference SET
    client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001'),
    region_id = (SELECT id FROM audit_regions WHERE code = 'REG-ZA'),
    fiscal_period_id = (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001'))
WHERE reference_id = 1;

UPDATE riskassessmentreference SET
    client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001'),
    region_id = (SELECT id FROM audit_regions WHERE code = 'REG-ZA'),
    business_unit_id = (SELECT id FROM business_units WHERE code = 'BU-AFF-CORP'),
    fiscal_period_id = (SELECT id FROM fiscal_periods WHERE period_name = 'FY 2025' AND client_id = (SELECT id FROM audit_clients WHERE code = 'CLI-001'))
WHERE reference_id = 2;

-- ============================================================================
-- PART 8: CREATE VIEWS FOR REPORTING
-- ============================================================================

-- Drop existing views if they exist
DROP VIEW IF EXISTS vw_findings_summary;
DROP VIEW IF EXISTS vw_control_test_summary;
DROP VIEW IF EXISTS vw_engagement_status;
DROP VIEW IF EXISTS vw_risk_by_hierarchy;

-- Findings summary view
CREATE VIEW vw_findings_summary AS
SELECT
    ac.id as client_id,
    ac.name as client_name,
    ar.id as region_id,
    ar.name as region_name,
    bu.id as business_unit_id,
    bu.name as business_unit_name,
    fp.id as fiscal_period_id,
    fp.period_name,
    fs.name as severity,
    fst.name as status,
    COUNT(af.id) as finding_count,
    SUM(CASE WHEN af.due_date < CURRENT_DATE AND fst.name != 'Closed' THEN 1 ELSE 0 END) as overdue_count
FROM audit_findings af
JOIN audit_engagements ae ON af.engagement_id = ae.id
JOIN audit_clients ac ON ae.client_id = ac.id
LEFT JOIN audit_regions ar ON ae.region_id = ar.id
LEFT JOIN business_units bu ON ae.business_unit_id = bu.id
LEFT JOIN fiscal_periods fp ON ae.fiscal_period_id = fp.id
LEFT JOIN ra_findingseverity fs ON af.severity_id = fs.id
LEFT JOIN ra_findingstatus fst ON af.status_id = fst.id
GROUP BY ac.id, ac.name, ar.id, ar.name, bu.id, bu.name, fp.id, fp.period_name, fs.name, fst.name;

-- Control test summary view
CREATE VIEW vw_control_test_summary AS
SELECT
    ac.id as client_id,
    ac.name as client_name,
    ar.id as region_id,
    ar.name as region_name,
    bu.id as business_unit_id,
    bu.name as business_unit_name,
    fp.id as fiscal_period_id,
    fp.period_name,
    tr.name as test_result,
    COUNT(ct.id) as test_count,
    SUM(ct.exceptions_found) as total_exceptions
FROM control_tests ct
JOIN audit_engagements ae ON ct.engagement_id = ae.id
JOIN audit_clients ac ON ae.client_id = ac.id
LEFT JOIN audit_regions ar ON ae.region_id = ar.id
LEFT JOIN business_units bu ON ae.business_unit_id = bu.id
LEFT JOIN fiscal_periods fp ON ae.fiscal_period_id = fp.id
LEFT JOIN ra_testresult tr ON ct.result_id = tr.id
GROUP BY ac.id, ac.name, ar.id, ar.name, bu.id, bu.name, fp.id, fp.period_name, tr.name;

-- Engagement status view
CREATE VIEW vw_engagement_status AS
SELECT
    ac.id as client_id,
    ac.name as client_name,
    ar.id as region_id,
    ar.name as region_name,
    fp.id as fiscal_period_id,
    fp.period_name,
    es.name as engagement_status,
    ae.engagement_type,
    COUNT(ae.id) as engagement_count,
    SUM(ae.budget_hours) as total_budget_hours,
    SUM(ae.actual_hours) as total_actual_hours
FROM audit_engagements ae
JOIN audit_clients ac ON ae.client_id = ac.id
LEFT JOIN audit_regions ar ON ae.region_id = ar.id
LEFT JOIN fiscal_periods fp ON ae.fiscal_period_id = fp.id
LEFT JOIN ra_engagementstatus es ON ae.status_id = es.id
GROUP BY ac.id, ac.name, ar.id, ar.name, fp.id, fp.period_name, es.name, ae.engagement_type;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Uncomment these to verify data after running script:
-- SELECT 'audit_clients' as table_name, COUNT(*) as row_count FROM audit_clients
-- UNION ALL SELECT 'audit_regions', COUNT(*) FROM audit_regions
-- UNION ALL SELECT 'business_units', COUNT(*) FROM business_units
-- UNION ALL SELECT 'fiscal_periods', COUNT(*) FROM fiscal_periods
-- UNION ALL SELECT 'audit_engagements', COUNT(*) FROM audit_engagements
-- UNION ALL SELECT 'audit_findings', COUNT(*) FROM audit_findings
-- UNION ALL SELECT 'control_tests', COUNT(*) FROM control_tests;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
