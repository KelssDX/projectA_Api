-- ===============================================
-- AUDIT PROCEDURE LIBRARY SCHEMA
-- ===============================================
-- This script creates reusable audit procedures and
-- assessment-linked execution records.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-06
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

-- ===============================================
-- SECTION 1: LOOKUPS
-- ===============================================

CREATE TABLE IF NOT EXISTS ra_procedure_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_procedure_type (name, description, color, sort_order) VALUES
('Planning', 'Planning and scoping procedures for the engagement', '#2563EB', 1),
('Walkthrough', 'Process walkthroughs and narrative confirmation procedures', '#7C3AED', 2),
('Control Testing', 'Tests of controls and design/operating effectiveness procedures', '#EA580C', 3),
('Substantive Analytics', 'Analytical procedures and expectation-driven review work', '#0891B2', 4),
('Substantive Testing', 'Detailed substantive testing of balances, classes, and transactions', '#16A34A', 5),
('Reporting', 'Completion and reporting procedures before final sign-off', '#4B5563', 6)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS ra_procedure_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    is_closed BOOLEAN DEFAULT FALSE,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_procedure_status (name, description, color, is_closed, sort_order) VALUES
('Planned', 'Procedure has been planned but not yet started', '#3B82F6', FALSE, 1),
('In Progress', 'Procedure execution is underway', '#8B5CF6', FALSE, 2),
('Performed', 'Procedure has been performed and awaits review', '#F59E0B', FALSE, 3),
('Under Review', 'Procedure evidence is being reviewed', '#6366F1', FALSE, 4),
('Completed', 'Procedure has been completed and accepted', '#10B981', TRUE, 5),
('Not Applicable', 'Procedure is no longer applicable to the engagement', '#6B7280', TRUE, 6)
ON CONFLICT (name) DO NOTHING;

-- ===============================================
-- SECTION 2: PROCEDURES
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_procedures (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    audit_universe_id INTEGER REFERENCES audit_universe(id) ON DELETE SET NULL,
    procedure_code VARCHAR(50) UNIQUE,
    procedure_title VARCHAR(500) NOT NULL,
    objective TEXT,
    procedure_description TEXT,
    procedure_type_id INTEGER REFERENCES ra_procedure_type(id) DEFAULT 1,
    status_id INTEGER REFERENCES ra_procedure_status(id) DEFAULT 1,
    sample_size INTEGER,
    expected_evidence TEXT,
    working_paper_ref VARCHAR(100),
    owner VARCHAR(255),
    performer_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewer_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    planned_date DATE,
    performed_date DATE,
    reviewed_date DATE,
    conclusion TEXT,
    notes TEXT,
    is_template BOOLEAN DEFAULT FALSE,
    source_template_id INTEGER REFERENCES audit_procedures(id) ON DELETE SET NULL,
    created_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_procedures IS 'Reusable audit procedure library templates and engagement-linked procedures';
COMMENT ON COLUMN audit_procedures.is_template IS 'True when the record is a reusable library procedure';
COMMENT ON COLUMN audit_procedures.source_template_id IS 'Original library template used to create this procedure';

CREATE OR REPLACE FUNCTION generate_audit_procedure_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.procedure_code IS NULL THEN
        NEW.procedure_code := 'PROC-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                              LPAD(nextval('audit_procedures_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_generate_audit_procedure_code ON audit_procedures;
CREATE TRIGGER trigger_generate_audit_procedure_code
    BEFORE INSERT ON audit_procedures
    FOR EACH ROW
    EXECUTE FUNCTION generate_audit_procedure_code();

CREATE OR REPLACE FUNCTION update_audit_procedure_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_procedure_updated_at ON audit_procedures;
CREATE TRIGGER trigger_update_audit_procedure_updated_at
    BEFORE UPDATE ON audit_procedures
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_procedure_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_procedures_reference_id ON audit_procedures(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedures_audit_universe_id ON audit_procedures(audit_universe_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedures_type_id ON audit_procedures(procedure_type_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedures_status_id ON audit_procedures(status_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedures_is_template ON audit_procedures(is_template);

-- ===============================================
-- SECTION 3: SEED LIBRARY TEMPLATES
-- ===============================================

INSERT INTO audit_procedures
(
    procedure_code,
    procedure_title,
    objective,
    procedure_description,
    procedure_type_id,
    status_id,
    sample_size,
    expected_evidence,
    owner,
    notes,
    is_template
)
SELECT
    seed.procedure_code,
    seed.procedure_title,
    seed.objective,
    seed.procedure_description,
    pt.id,
    ps.id,
    seed.sample_size,
    seed.expected_evidence,
    seed.owner,
    seed.notes,
    TRUE
FROM (
    VALUES
    (
        'PROC-TPL-PLAN-001',
        'Planning scope confirmation',
        'Confirm that the audit scope covers the agreed processes, locations, and period.',
        'Inspect the signed scope letter, risk register, and planning memo. Verify that planned coverage aligns to the approved scope and business process selection.',
        'Planning',
        'Completed',
        NULL,
        'Signed scope letter, planning memo, approved scope list',
        'Audit Manager',
        'Useful for both internal and external audits during planning.'
    ),
    (
        'PROC-TPL-WALK-001',
        'Revenue process walkthrough',
        'Understand end-to-end revenue processing and identify key control points.',
        'Perform a walkthrough from source transaction through general ledger posting. Confirm system handoffs, approvals, and exception handling.',
        'Walkthrough',
        'Completed',
        1,
        'Narrative, screenshots, process map, walkthrough notes',
        'Senior Auditor',
        'Adaptable to order-to-cash and similar revenue streams.'
    ),
    (
        'PROC-TPL-CTRL-001',
        'Approval control operating effectiveness test',
        'Determine whether key approvals operated effectively for the selected sample.',
        'Select a sample of transactions and inspect evidence that the required approval took place before processing or posting.',
        'Control Testing',
        'Completed',
        25,
        'Approved transactions, system logs, approval matrix',
        'Audit Associate',
        'Can be reused for purchase orders, journals, payments, and access approvals.'
    ),
    (
        'PROC-TPL-SA-001',
        'Month-over-month variance analytics',
        'Identify unusual fluctuations that require further investigation.',
        'Develop an expectation, compare recorded results to the expectation, and investigate variances outside threshold.',
        'Substantive Analytics',
        'Completed',
        NULL,
        'Trial balance extract, supporting schedules, variance analysis',
        'Data Auditor',
        'Works well as a bridge between analytics and detailed testing.'
    ),
    (
        'PROC-TPL-ST-001',
        'Detailed vouching of material transactions',
        'Obtain evidence that sampled transactions are valid, accurate, and supported.',
        'Select a sample of material transactions and inspect supporting documentation, authorization, accuracy, and correct posting.',
        'Substantive Testing',
        'Completed',
        30,
        'Invoices, contracts, approvals, ledger support',
        'Audit Associate',
        'Typical external audit detailed testing procedure.'
    ),
    (
        'PROC-TPL-REP-001',
        'Final reporting completion checklist',
        'Confirm that findings, management responses, and sign-offs are complete before report issuance.',
        'Review the engagement for unresolved findings, missing responses, missing working paper sign-offs, and outstanding review notes.',
        'Reporting',
        'Completed',
        NULL,
        'Draft report, sign-off records, review checklist',
        'Audit Manager',
        'Completion-stage procedure before issuing the report.'
    )
) AS seed(procedure_code, procedure_title, objective, procedure_description, procedure_type_name, status_name, sample_size, expected_evidence, owner, notes)
INNER JOIN ra_procedure_type pt ON pt.name = seed.procedure_type_name
INNER JOIN ra_procedure_status ps ON ps.name = seed.status_name
WHERE NOT EXISTS (
    SELECT 1
    FROM audit_procedures existing
    WHERE existing.procedure_code = seed.procedure_code
);

-- ===============================================
-- END OF SCRIPT
-- ===============================================
