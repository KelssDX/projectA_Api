-- ===============================================
-- AUDIT EXECUTION PHASE 2 COMPLETION SCHEMA
-- ===============================================
-- This script completes the remaining Phase 2 execution
-- modules: planning, scoping, risk/control matrix, and walkthroughs.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-07
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

-- ===============================================
-- SECTION 1: PLANNING LOOKUPS
-- ===============================================

CREATE TABLE IF NOT EXISTS ra_engagement_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_engagement_type (name, description, sort_order) VALUES
('Internal Audit', 'Internal assurance or advisory engagement', 1),
('External Audit', 'External statutory or financial statement audit engagement', 2)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS ra_planning_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    is_closed BOOLEAN DEFAULT FALSE,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_planning_status (name, description, color, is_closed, sort_order) VALUES
('Draft', 'Planning record has been created but not finalized', '#64748B', FALSE, 1),
('In Progress', 'Planning and scoping are still being prepared', '#2563EB', FALSE, 2),
('Ready for Sign-off', 'Planning is ready for approval or sign-off', '#F59E0B', FALSE, 3),
('Signed Off', 'Planning has been approved and signed off', '#16A34A', TRUE, 4)
ON CONFLICT (name) DO NOTHING;

-- ===============================================
-- SECTION 2: PLANNING AND SCOPING
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_engagement_plans (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL UNIQUE REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    engagement_title VARCHAR(500) NOT NULL,
    engagement_type_id INTEGER REFERENCES ra_engagement_type(id) ON DELETE SET NULL,
    plan_year INTEGER,
    annual_plan_name VARCHAR(255),
    business_unit VARCHAR(255),
    process_area VARCHAR(255),
    subprocess_area VARCHAR(255),
    fsli VARCHAR(255),
    scope_summary TEXT,
    materiality TEXT,
    risk_strategy TEXT,
    planning_status_id INTEGER REFERENCES ra_planning_status(id) DEFAULT 1,
    scope_letter_document_id INTEGER REFERENCES audit_documents(id) ON DELETE SET NULL,
    is_signed_off BOOLEAN DEFAULT FALSE,
    signed_off_by_name VARCHAR(255),
    signed_off_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    signed_off_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_audit_engagement_plan_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_engagement_plan_updated_at ON audit_engagement_plans;
CREATE TRIGGER trigger_update_audit_engagement_plan_updated_at
    BEFORE UPDATE ON audit_engagement_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_engagement_plan_updated_at();

CREATE TABLE IF NOT EXISTS audit_scope_items (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES audit_engagement_plans(id) ON DELETE CASCADE,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    business_unit VARCHAR(255),
    process_name VARCHAR(255),
    subprocess_name VARCHAR(255),
    fsli VARCHAR(255),
    scope_status VARCHAR(100) DEFAULT 'Planned',
    include_in_scope BOOLEAN DEFAULT TRUE,
    risk_reference TEXT,
    control_reference TEXT,
    procedure_id INTEGER REFERENCES audit_procedures(id) ON DELETE SET NULL,
    owner VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_scope_items_reference_id ON audit_scope_items(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_scope_items_plan_id ON audit_scope_items(plan_id);
CREATE INDEX IF NOT EXISTS idx_audit_scope_items_procedure_id ON audit_scope_items(procedure_id);

-- ===============================================
-- SECTION 3: RISK AND CONTROL MATRIX
-- ===============================================

CREATE TABLE IF NOT EXISTS ra_control_classification (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_control_classification (name, description, sort_order) VALUES
('Preventive', 'Control is designed to prevent an issue before it occurs', 1),
('Detective', 'Control is designed to identify an issue after it occurs', 2),
('Corrective', 'Control is designed to remediate or correct an identified issue', 3)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS ra_control_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_control_type (name, description, sort_order) VALUES
('Manual', 'Control is executed manually by a user', 1),
('Automated', 'Control is executed automatically by a system', 2),
('IT Dependent', 'Control is manual but depends on system-generated information', 3)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS ra_control_frequency (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_control_frequency (name, description, sort_order) VALUES
('Daily', 'Control is performed daily', 1),
('Weekly', 'Control is performed weekly', 2),
('Monthly', 'Control is performed monthly', 3),
('Quarterly', 'Control is performed quarterly', 4),
('Annually', 'Control is performed annually', 5),
('Ad Hoc', 'Control is performed as needed', 6)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS audit_risk_control_matrix (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    scope_item_id INTEGER REFERENCES audit_scope_items(id) ON DELETE SET NULL,
    procedure_id INTEGER REFERENCES audit_procedures(id) ON DELETE SET NULL,
    risk_title VARCHAR(500) NOT NULL,
    risk_description TEXT,
    control_name VARCHAR(500) NOT NULL,
    control_description TEXT,
    control_adequacy VARCHAR(100),
    control_effectiveness VARCHAR(100),
    control_classification_id INTEGER REFERENCES ra_control_classification(id) ON DELETE SET NULL,
    control_type_id INTEGER REFERENCES ra_control_type(id) ON DELETE SET NULL,
    control_frequency_id INTEGER REFERENCES ra_control_frequency(id) ON DELETE SET NULL,
    control_owner VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_audit_rcm_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_rcm_updated_at ON audit_risk_control_matrix;
CREATE TRIGGER trigger_update_audit_rcm_updated_at
    BEFORE UPDATE ON audit_risk_control_matrix
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_rcm_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_risk_control_matrix_reference_id ON audit_risk_control_matrix(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_risk_control_matrix_scope_item_id ON audit_risk_control_matrix(scope_item_id);
CREATE INDEX IF NOT EXISTS idx_audit_risk_control_matrix_procedure_id ON audit_risk_control_matrix(procedure_id);

-- ===============================================
-- SECTION 4: WALKTHROUGHS
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_walkthroughs (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    scope_item_id INTEGER REFERENCES audit_scope_items(id) ON DELETE SET NULL,
    procedure_id INTEGER REFERENCES audit_procedures(id) ON DELETE SET NULL,
    risk_control_matrix_id INTEGER REFERENCES audit_risk_control_matrix(id) ON DELETE SET NULL,
    process_name VARCHAR(255) NOT NULL,
    walkthrough_date DATE,
    participants TEXT,
    process_narrative TEXT,
    evidence_summary TEXT,
    control_design_conclusion TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_audit_walkthrough_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_walkthrough_updated_at ON audit_walkthroughs;
CREATE TRIGGER trigger_update_audit_walkthrough_updated_at
    BEFORE UPDATE ON audit_walkthroughs
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_walkthrough_updated_at();

CREATE TABLE IF NOT EXISTS audit_walkthrough_exceptions (
    id SERIAL PRIMARY KEY,
    walkthrough_id INTEGER NOT NULL REFERENCES audit_walkthroughs(id) ON DELETE CASCADE,
    exception_title VARCHAR(500) NOT NULL,
    exception_description TEXT,
    severity VARCHAR(100) DEFAULT 'Medium',
    linked_finding_id INTEGER REFERENCES audit_findings(id) ON DELETE SET NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_walkthroughs_reference_id ON audit_walkthroughs(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_walkthroughs_scope_item_id ON audit_walkthroughs(scope_item_id);
CREATE INDEX IF NOT EXISTS idx_audit_walkthroughs_procedure_id ON audit_walkthroughs(procedure_id);
CREATE INDEX IF NOT EXISTS idx_audit_walkthrough_exceptions_walkthrough_id ON audit_walkthrough_exceptions(walkthrough_id);

