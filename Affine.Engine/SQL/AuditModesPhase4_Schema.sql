-- ===============================================
-- AUDIT MODES PHASE 4 SCHEMA
-- ===============================================
-- This script differentiates internal and external
-- audit execution through planning fields, template
-- applicability, and management action tracking.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-08
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

-- ===============================================
-- SECTION 1: PLANNING AND SCOPING ENHANCEMENTS
-- ===============================================

ALTER TABLE audit_engagement_plans
    ADD COLUMN IF NOT EXISTS materiality_basis VARCHAR(255),
    ADD COLUMN IF NOT EXISTS overall_materiality NUMERIC(18, 2),
    ADD COLUMN IF NOT EXISTS performance_materiality NUMERIC(18, 2),
    ADD COLUMN IF NOT EXISTS clearly_trivial_threshold NUMERIC(18, 2);

ALTER TABLE audit_scope_items
    ADD COLUMN IF NOT EXISTS assertions TEXT,
    ADD COLUMN IF NOT EXISTS scoping_rationale TEXT;

-- ===============================================
-- SECTION 2: TEMPLATE APPLICABILITY
-- ===============================================

ALTER TABLE audit_procedures
    ADD COLUMN IF NOT EXISTS applicable_engagement_type_id INTEGER REFERENCES ra_engagement_type(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS template_pack VARCHAR(150),
    ADD COLUMN IF NOT EXISTS template_tags TEXT;

CREATE INDEX IF NOT EXISTS idx_audit_procedures_applicable_engagement_type_id
    ON audit_procedures(applicable_engagement_type_id);

ALTER TABLE audit_working_papers
    ADD COLUMN IF NOT EXISTS applicable_engagement_type_id INTEGER REFERENCES ra_engagement_type(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS template_pack VARCHAR(150),
    ADD COLUMN IF NOT EXISTS template_tags TEXT;

CREATE INDEX IF NOT EXISTS idx_audit_working_papers_applicable_engagement_type_id
    ON audit_working_papers(applicable_engagement_type_id);

-- ===============================================
-- SECTION 3: MANAGEMENT ACTION TRACKING
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_management_actions (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    finding_id INTEGER REFERENCES audit_findings(id) ON DELETE SET NULL,
    recommendation_id INTEGER REFERENCES audit_recommendations(id) ON DELETE SET NULL,
    action_title VARCHAR(500) NOT NULL,
    action_description TEXT,
    owner_name VARCHAR(255),
    owner_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    due_date DATE,
    status VARCHAR(100) DEFAULT 'Open',
    progress_percent INTEGER DEFAULT 0,
    management_response TEXT,
    closure_notes TEXT,
    validated_by_name VARCHAR(255),
    validated_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    validated_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_audit_management_action_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_management_action_updated_at ON audit_management_actions;
CREATE TRIGGER trigger_update_audit_management_action_updated_at
    BEFORE UPDATE ON audit_management_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_management_action_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_management_actions_reference_id
    ON audit_management_actions(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_management_actions_recommendation_id
    ON audit_management_actions(recommendation_id);
CREATE INDEX IF NOT EXISTS idx_audit_management_actions_due_date
    ON audit_management_actions(due_date);
CREATE INDEX IF NOT EXISTS idx_audit_management_actions_status
    ON audit_management_actions(status);

-- ===============================================
-- SECTION 4: INTERNAL AND EXTERNAL PROCEDURE PACKS
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
    is_template,
    applicable_engagement_type_id,
    template_pack,
    template_tags
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
    TRUE,
    et.id,
    seed.template_pack,
    seed.template_tags
FROM (
    VALUES
    (
        'PROC-TPL-INT-PLAN-001',
        'Control coverage scoping review',
        'Confirm that scope selections cover the key processes, business units, and control themes for the internal audit.',
        'Review the annual audit plan, risk universe, and prior observations. Confirm the engagement scope is control-focused and linked to auditable units.',
        'Planning',
        'Completed',
        NULL,
        'Annual plan, audit universe, prior reports, scoping memo',
        'Audit Manager',
        'Internal audit planning template.',
        'Internal Audit',
        'Internal Planning',
        'internal audit,control coverage,scoping'
    ),
    (
        'PROC-TPL-INT-FUP-001',
        'Management action follow-up validation',
        'Validate that agreed management actions were implemented and are operating as intended.',
        'Inspect remediation evidence, confirm action owners completed agreed steps, and assess whether the underlying observation has been addressed.',
        'Reporting',
        'Completed',
        1,
        'Action tracker, remediation evidence, validation memo',
        'Audit Manager',
        'Internal audit follow-up template.',
        'Internal Audit',
        'Internal Follow-Up',
        'internal audit,management action,follow-up,remediation'
    ),
    (
        'PROC-TPL-EXT-PLAN-001',
        'Overall and performance materiality assessment',
        'Establish and document overall materiality, performance materiality, and trivial posting thresholds.',
        'Determine the benchmark, apply the selected percentage, and document rationale for overall materiality, performance materiality, and clearly trivial thresholds.',
        'Planning',
        'Completed',
        NULL,
        'Trial balance, planning memo, materiality calculation',
        'Audit Manager',
        'External audit planning template.',
        'External Audit',
        'External Planning',
        'external audit,materiality,planning'
    ),
    (
        'PROC-TPL-EXT-PLAN-002',
        'FSLI and assertion mapping',
        'Map scoped financial statement line items to relevant assertions and planned procedures.',
        'For each scoped FSLI, document the key assertions, identified risks, and whether tests of controls or substantive procedures will address them.',
        'Planning',
        'Completed',
        NULL,
        'FSLI matrix, assertion map, planning analytics',
        'Senior Auditor',
        'External audit scoping template.',
        'External Audit',
        'External Planning',
        'external audit,fsli,assertions'
    ),
    (
        'PROC-TPL-EXT-ST-002',
        'Journal entry testing and management override review',
        'Test journal entries and management override indicators for unusual or unsupported postings.',
        'Extract journals, define risk-based filters, inspect supporting evidence, and investigate unusual manual postings near period end.',
        'Substantive Testing',
        'Completed',
        40,
        'Journal listing, filter logic, support for selected entries',
        'Data Auditor',
        'External audit completion template.',
        'External Audit',
        'External Completion',
        'external audit,journal testing,management override'
    ),
    (
        'PROC-TPL-EXT-ST-003',
        'Recalculation and reperformance procedure',
        'Recalculate key balances or reperform control calculations for selected samples.',
        'Independently recalculate complex estimates or reperform control calculations and compare to client outputs, investigating any differences.',
        'Substantive Testing',
        'Completed',
        15,
        'Client schedules, recalculation workbook, reperformance results',
        'Audit Associate',
        'External audit detailed testing template.',
        'External Audit',
        'External Detailed Testing',
        'external audit,recalculation,reperformance'
    )
) AS seed(
    procedure_code,
    procedure_title,
    objective,
    procedure_description,
    procedure_type_name,
    status_name,
    sample_size,
    expected_evidence,
    owner,
    notes,
    engagement_type_name,
    template_pack,
    template_tags
)
INNER JOIN ra_procedure_type pt ON pt.name = seed.procedure_type_name
INNER JOIN ra_procedure_status ps ON ps.name = seed.status_name
INNER JOIN ra_engagement_type et ON et.name = seed.engagement_type_name
WHERE NOT EXISTS (
    SELECT 1
    FROM audit_procedures existing
    WHERE existing.procedure_code = seed.procedure_code
);

-- ===============================================
-- SECTION 5: INTERNAL AND EXTERNAL WORKPAPER PACKS
-- ===============================================

INSERT INTO audit_working_papers
(
    working_paper_code,
    title,
    objective,
    description,
    status_id,
    prepared_by,
    reviewer_name,
    conclusion,
    notes,
    is_template,
    applicable_engagement_type_id,
    template_pack,
    template_tags
)
SELECT
    seed.working_paper_code,
    seed.title,
    seed.objective,
    seed.description,
    st.id,
    seed.prepared_by,
    seed.reviewer_name,
    seed.conclusion,
    seed.notes,
    TRUE,
    et.id,
    seed.template_pack,
    seed.template_tags
FROM (
    VALUES
    (
        'WP-TPL-INT-001',
        'Observation and management action tracker',
        'Track internal audit observations, agreed actions, due dates, and validation status.',
        'Use this working paper to monitor action ownership, implementation status, and follow-up validation for internal audit work.',
        'Approved',
        'Audit Manager',
        'Head of Audit',
        'Tracker is current and supports follow-up conclusions.',
        'Internal audit follow-up template.',
        'Internal Audit',
        'Internal Follow-Up',
        'internal audit,observation tracker,management actions'
    ),
    (
        'WP-TPL-INT-002',
        'Control coverage scoping memo',
        'Document why selected processes and controls were included in scope for the engagement.',
        'Capture business rationale, auditable entities, and linkage to control objectives and prior observations.',
        'Approved',
        'Senior Auditor',
        'Audit Manager',
        'Control-focused scope approved.',
        'Internal audit planning template.',
        'Internal Audit',
        'Internal Planning',
        'internal audit,scope memo,control coverage'
    ),
    (
        'WP-TPL-EXT-001',
        'Materiality and FSLI planning worksheet',
        'Document planning materiality thresholds and scoped financial statement line items.',
        'Capture benchmark selection, overall materiality, performance materiality, clearly trivial threshold, and the scoped FSLI population.',
        'Approved',
        'Audit Manager',
        'Engagement Partner',
        'Materiality and FSLI scope documented.',
        'External audit planning template.',
        'External Audit',
        'External Planning',
        'external audit,materiality,fsli'
    ),
    (
        'WP-TPL-EXT-002',
        'Journal testing results sheet',
        'Capture population, filters, selected journals, and conclusions for journal entry testing.',
        'Document extraction logic, risk factors, sampled journals, exceptions, and conclusion for management override testing.',
        'Approved',
        'Data Auditor',
        'Audit Manager',
        'Journal testing completed and concluded.',
        'External audit detailed testing template.',
        'External Audit',
        'External Completion',
        'external audit,journal testing,management override'
    ),
    (
        'WP-TPL-EXT-003',
        'Assertion mapping worksheet',
        'Map scoped balances to assertions, procedures, and results.',
        'Track which assertions are addressed for each FSLI and how substantive procedures respond to identified risks.',
        'Approved',
        'Senior Auditor',
        'Audit Manager',
        'Assertion coverage documented.',
        'External audit scoping template.',
        'External Audit',
        'External Planning',
        'external audit,assertions,planning'
    )
) AS seed(
    working_paper_code,
    title,
    objective,
    description,
    status_name,
    prepared_by,
    reviewer_name,
    conclusion,
    notes,
    engagement_type_name,
    template_pack,
    template_tags
)
INNER JOIN ra_working_paper_status st ON st.name = seed.status_name
INNER JOIN ra_engagement_type et ON et.name = seed.engagement_type_name
WHERE NOT EXISTS (
    SELECT 1
    FROM audit_working_papers existing
    WHERE existing.working_paper_code = seed.working_paper_code
);
