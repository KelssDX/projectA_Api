-- =====================================================
-- Database Workstream Closeout
-- Purpose:
--   Add the remaining generic audit-domain tables that
--   were still open in the Database Workstream tracker.
--   These tables complement, rather than replace,
--   Elsa-linked workflow tables.
-- =====================================================

SET search_path TO "Risk_Assess_Framework";

CREATE OR REPLACE FUNCTION set_audit_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Procedure detail and assignment tables
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_procedure_steps (
    id SERIAL PRIMARY KEY,
    procedure_id INTEGER NOT NULL REFERENCES audit_procedures(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_title VARCHAR(255) NOT NULL,
    instruction_text TEXT,
    expected_result TEXT,
    sample_guidance TEXT,
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (procedure_id, step_number)
);

COMMENT ON TABLE audit_procedure_steps IS 'Ordered steps that define how a procedure should be executed.';

DROP TRIGGER IF EXISTS trigger_update_audit_procedure_steps_updated_at ON audit_procedure_steps;
CREATE TRIGGER trigger_update_audit_procedure_steps_updated_at
    BEFORE UPDATE ON audit_procedure_steps
    FOR EACH ROW
    EXECUTE FUNCTION set_audit_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_procedure_steps_procedure_id
    ON audit_procedure_steps(procedure_id, step_number);

CREATE TABLE IF NOT EXISTS audit_procedure_assignments (
    id SERIAL PRIMARY KEY,
    procedure_id INTEGER NOT NULL REFERENCES audit_procedures(id) ON DELETE CASCADE,
    procedure_step_id INTEGER REFERENCES audit_procedure_steps(id) ON DELETE SET NULL,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    scope_item_id INTEGER REFERENCES audit_scope_items(id) ON DELETE SET NULL,
    risk_control_matrix_id INTEGER REFERENCES audit_risk_control_matrix(id) ON DELETE SET NULL,
    walkthrough_id INTEGER REFERENCES audit_walkthroughs(id) ON DELETE SET NULL,
    working_paper_id INTEGER REFERENCES audit_working_papers(id) ON DELETE SET NULL,
    assignment_type VARCHAR(100) NOT NULL DEFAULT 'Primary',
    status VARCHAR(100) NOT NULL DEFAULT 'Assigned',
    assigned_to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_name VARCHAR(255),
    assigned_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_by_name VARCHAR(255),
    due_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_procedure_assignments IS 'Links procedures or specific procedure steps to scope, RCM, walkthrough, or working-paper execution context.';

DROP TRIGGER IF EXISTS trigger_update_audit_procedure_assignments_updated_at ON audit_procedure_assignments;
CREATE TRIGGER trigger_update_audit_procedure_assignments_updated_at
    BEFORE UPDATE ON audit_procedure_assignments
    FOR EACH ROW
    EXECUTE FUNCTION set_audit_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_procedure_assignments_procedure_id
    ON audit_procedure_assignments(procedure_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedure_assignments_reference_id
    ON audit_procedure_assignments(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedure_assignments_scope_item_id
    ON audit_procedure_assignments(scope_item_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedure_assignments_working_paper_id
    ON audit_procedure_assignments(working_paper_id);
CREATE INDEX IF NOT EXISTS idx_audit_procedure_assignments_assignee
    ON audit_procedure_assignments(assigned_to_user_id, status);

-- =====================================================
-- Working paper structure tables
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_working_paper_sections (
    id SERIAL PRIMARY KEY,
    working_paper_id INTEGER NOT NULL REFERENCES audit_working_papers(id) ON DELETE CASCADE,
    section_order INTEGER NOT NULL DEFAULT 1,
    section_code VARCHAR(50),
    section_title VARCHAR(255) NOT NULL,
    section_type VARCHAR(100) NOT NULL DEFAULT 'Narrative',
    content_text TEXT,
    is_required BOOLEAN DEFAULT TRUE,
    prepared_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    review_status VARCHAR(100) NOT NULL DEFAULT 'Draft',
    last_reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (working_paper_id, section_order)
);

COMMENT ON TABLE audit_working_paper_sections IS 'Structured sections within a working paper to support preparation, review, and sign-off at subsection level.';

DROP TRIGGER IF EXISTS trigger_update_audit_working_paper_sections_updated_at ON audit_working_paper_sections;
CREATE TRIGGER trigger_update_audit_working_paper_sections_updated_at
    BEFORE UPDATE ON audit_working_paper_sections
    FOR EACH ROW
    EXECUTE FUNCTION set_audit_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_working_paper_sections_working_paper_id
    ON audit_working_paper_sections(working_paper_id, section_order);

-- =====================================================
-- Control testing tables
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_control_tests (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    scope_item_id INTEGER REFERENCES audit_scope_items(id) ON DELETE SET NULL,
    risk_control_matrix_id INTEGER REFERENCES audit_risk_control_matrix(id) ON DELETE SET NULL,
    procedure_id INTEGER REFERENCES audit_procedures(id) ON DELETE SET NULL,
    working_paper_id INTEGER REFERENCES audit_working_papers(id) ON DELETE SET NULL,
    control_name VARCHAR(500) NOT NULL,
    control_description TEXT,
    test_objective TEXT,
    test_method VARCHAR(100),
    population_description TEXT,
    sample_size INTEGER,
    sample_basis TEXT,
    test_frequency VARCHAR(100),
    tester_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewer_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    planned_test_date DATE,
    performed_test_date DATE,
    status VARCHAR(100) NOT NULL DEFAULT 'Planned',
    conclusion VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_control_tests IS 'Engagement-level control test records linked to procedures, RCM items, and working papers.';

DROP TRIGGER IF EXISTS trigger_update_audit_control_tests_updated_at ON audit_control_tests;
CREATE TRIGGER trigger_update_audit_control_tests_updated_at
    BEFORE UPDATE ON audit_control_tests
    FOR EACH ROW
    EXECUTE FUNCTION set_audit_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_control_tests_reference_id
    ON audit_control_tests(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_control_tests_rcm_id
    ON audit_control_tests(risk_control_matrix_id);
CREATE INDEX IF NOT EXISTS idx_audit_control_tests_working_paper_id
    ON audit_control_tests(working_paper_id);
CREATE INDEX IF NOT EXISTS idx_audit_control_tests_status
    ON audit_control_tests(status);

CREATE TABLE IF NOT EXISTS audit_control_test_results (
    id SERIAL PRIMARY KEY,
    control_test_id INTEGER NOT NULL REFERENCES audit_control_tests(id) ON DELETE CASCADE,
    sample_reference VARCHAR(100),
    attribute_tested VARCHAR(255),
    expected_result TEXT,
    actual_result TEXT,
    is_exception BOOLEAN DEFAULT FALSE,
    exception_description TEXT,
    evidence_document_id INTEGER REFERENCES audit_documents(id) ON DELETE SET NULL,
    evidence_working_paper_id INTEGER REFERENCES audit_working_papers(id) ON DELETE SET NULL,
    result_status VARCHAR(100) NOT NULL DEFAULT 'Pass',
    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tested_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

COMMENT ON TABLE audit_control_test_results IS 'Sample-level or attribute-level results captured under a control test.';

CREATE INDEX IF NOT EXISTS idx_audit_control_test_results_control_test_id
    ON audit_control_test_results(control_test_id);
CREATE INDEX IF NOT EXISTS idx_audit_control_test_results_exception
    ON audit_control_test_results(is_exception, result_status);

-- =====================================================
-- Generic review, note, sign-off, and task tables
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_tasks (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    workflow_instance_id VARCHAR(255) REFERENCES audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL,
    task_type VARCHAR(100) NOT NULL DEFAULT 'Action',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_name VARCHAR(255),
    assigned_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_by_name VARCHAR(255),
    status VARCHAR(100) NOT NULL DEFAULT 'Open',
    priority VARCHAR(50) NOT NULL DEFAULT 'Medium',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    completed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    completion_notes TEXT,
    source VARCHAR(50) NOT NULL DEFAULT 'Manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_tasks IS 'Generic audit work items for manual or application-managed actions outside the Elsa task list.';

DROP TRIGGER IF EXISTS trigger_update_audit_tasks_updated_at ON audit_tasks;
CREATE TRIGGER trigger_update_audit_tasks_updated_at
    BEFORE UPDATE ON audit_tasks
    FOR EACH ROW
    EXECUTE FUNCTION set_audit_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_tasks_reference_id
    ON audit_tasks(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_tasks_assignee
    ON audit_tasks(assigned_to_user_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_tasks_workflow_instance_id
    ON audit_tasks(workflow_instance_id);

CREATE TABLE IF NOT EXISTS audit_reviews (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER NOT NULL,
    review_type VARCHAR(100) NOT NULL DEFAULT 'Manager Review',
    status VARCHAR(100) NOT NULL DEFAULT 'Open',
    task_id INTEGER REFERENCES audit_tasks(id) ON DELETE SET NULL,
    workflow_instance_id VARCHAR(255) REFERENCES audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL,
    assigned_reviewer_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_reviewer_name VARCHAR(255),
    requested_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    requested_by_name VARCHAR(255),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    completed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_reviews IS 'Generic review records for working papers, findings, procedures, planning packs, and report packs.';

DROP TRIGGER IF EXISTS trigger_update_audit_reviews_updated_at ON audit_reviews;
CREATE TRIGGER trigger_update_audit_reviews_updated_at
    BEFORE UPDATE ON audit_reviews
    FOR EACH ROW
    EXECUTE FUNCTION set_audit_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_reviews_reference_id
    ON audit_reviews(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_reviews_entity
    ON audit_reviews(entity_type, entity_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_reviews_reviewer
    ON audit_reviews(assigned_reviewer_user_id, status);

CREATE TABLE IF NOT EXISTS audit_review_notes (
    id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL REFERENCES audit_reviews(id) ON DELETE CASCADE,
    working_paper_section_id INTEGER REFERENCES audit_working_paper_sections(id) ON DELETE SET NULL,
    note_type VARCHAR(100) NOT NULL DEFAULT 'Review Note',
    severity VARCHAR(50) NOT NULL DEFAULT 'Medium',
    status VARCHAR(100) NOT NULL DEFAULT 'Open',
    note_text TEXT NOT NULL,
    response_text TEXT,
    raised_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    raised_by_name VARCHAR(255),
    raised_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cleared_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    cleared_by_name VARCHAR(255),
    cleared_at TIMESTAMP
);

COMMENT ON TABLE audit_review_notes IS 'Notes, exceptions, and rework comments raised during reviews.';

CREATE INDEX IF NOT EXISTS idx_audit_review_notes_review_id
    ON audit_review_notes(review_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_review_notes_section_id
    ON audit_review_notes(working_paper_section_id);

CREATE TABLE IF NOT EXISTS audit_signoffs (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER NOT NULL,
    review_id INTEGER REFERENCES audit_reviews(id) ON DELETE SET NULL,
    workflow_instance_id VARCHAR(255) REFERENCES audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL,
    signoff_type VARCHAR(100) NOT NULL,
    signoff_level VARCHAR(100),
    status VARCHAR(100) NOT NULL DEFAULT 'Signed',
    signed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    signed_by_name VARCHAR(255),
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comment TEXT
);

COMMENT ON TABLE audit_signoffs IS 'Generic sign-off records across planning, execution, review, and reporting stages.';

CREATE INDEX IF NOT EXISTS idx_audit_signoffs_reference_id
    ON audit_signoffs(reference_id, signed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_signoffs_entity
    ON audit_signoffs(entity_type, entity_id, signoff_type);

-- =====================================================
-- Access and authentication audit logs
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_document_access_logs (
    id BIGSERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES audit_documents(id) ON DELETE CASCADE,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    accessed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    accessed_by_name VARCHAR(255),
    ip_address VARCHAR(100),
    client_context VARCHAR(100),
    correlation_id VARCHAR(255),
    success BOOLEAN NOT NULL DEFAULT TRUE,
    details_json JSONB,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_document_access_logs IS 'Immutable log of document opens, downloads, previews, shares, deletes, and uploads.';

CREATE INDEX IF NOT EXISTS idx_audit_document_access_logs_document_id
    ON audit_document_access_logs(document_id, accessed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_document_access_logs_reference_id
    ON audit_document_access_logs(reference_id, accessed_at DESC);

CREATE TABLE IF NOT EXISTS audit_login_events (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(255),
    display_name VARCHAR(255),
    event_type VARCHAR(50) NOT NULL DEFAULT 'Login',
    status VARCHAR(50) NOT NULL DEFAULT 'Success',
    ip_address VARCHAR(100),
    user_agent TEXT,
    client_context VARCHAR(100),
    failure_reason TEXT,
    correlation_id VARCHAR(255),
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_login_events IS 'Authentication and session lifecycle log for auditability of platform access.';

CREATE INDEX IF NOT EXISTS idx_audit_login_events_user_id
    ON audit_login_events(user_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_login_events_status
    ON audit_login_events(status, occurred_at DESC);

-- =====================================================
-- Seed template-level procedure steps
-- =====================================================

INSERT INTO audit_procedure_steps (procedure_id, step_number, step_title, instruction_text, expected_result, sample_guidance, is_mandatory)
SELECT p.id, seed.step_number, seed.step_title, seed.instruction_text, seed.expected_result, seed.sample_guidance, seed.is_mandatory
FROM audit_procedures p
INNER JOIN (
    VALUES
        ('PROC-TPL-PLAN-001', 1, 'Inspect scope letter', 'Inspect the approved scope letter and verify period, business process, and location coverage.', 'Scope letter agrees to the current plan.', NULL, TRUE),
        ('PROC-TPL-PLAN-001', 2, 'Match scope to planned coverage', 'Compare approved scope to selected scope items and planned audit coverage.', 'Scope items align to approved scope.', 'Trace high-risk areas first.', TRUE),
        ('PROC-TPL-WALK-001', 1, 'Trace a source transaction', 'Select one transaction and trace it from initiation to general ledger posting.', 'End-to-end flow is understood and documented.', 'Prefer a recent material transaction.', TRUE),
        ('PROC-TPL-WALK-001', 2, 'Identify control points', 'Document approvals, system controls, and exception handling observed during the walkthrough.', 'Key controls and gaps are recorded.', NULL, TRUE),
        ('PROC-TPL-CTRL-001', 1, 'Define sample', 'Document the population and select a sample using the agreed sampling basis.', 'Sample is complete and reproducible.', 'Retain evidence of sample selection.', TRUE),
        ('PROC-TPL-CTRL-001', 2, 'Inspect control evidence', 'Inspect approval or execution evidence for each sampled item.', 'Control operated as designed for each sampled item.', NULL, TRUE),
        ('PROC-TPL-SA-001', 1, 'Develop expectation', 'Develop an independent expectation using prior periods, budgets, or operational drivers.', 'Expectation is documented and supportable.', NULL, TRUE),
        ('PROC-TPL-SA-001', 2, 'Investigate variances', 'Investigate and document variances that exceed threshold.', 'Unusual movements are explained or escalated.', NULL, TRUE),
        ('PROC-TPL-ST-001', 1, 'Select material sample', 'Select a sample of material transactions for detailed testing.', 'Sample addresses risk and materiality.', NULL, TRUE),
        ('PROC-TPL-ST-001', 2, 'Inspect source support', 'Inspect source documents, approvals, and posting accuracy for sampled items.', 'Transactions are valid, accurate, and supported.', NULL, TRUE),
        ('PROC-TPL-REP-001', 1, 'Check unresolved items', 'Check unresolved findings, missing management responses, and outstanding review notes.', 'Outstanding reporting blockers are identified.', NULL, TRUE),
        ('PROC-TPL-REP-001', 2, 'Confirm sign-off completeness', 'Confirm working paper and report sign-offs before issue.', 'Audit pack is complete for report issue.', NULL, TRUE)
) AS seed(procedure_code, step_number, step_title, instruction_text, expected_result, sample_guidance, is_mandatory)
    ON seed.procedure_code = p.procedure_code
WHERE p.is_template = TRUE
  AND NOT EXISTS (
      SELECT 1
      FROM audit_procedure_steps existing
      WHERE existing.procedure_id = p.id
        AND existing.step_number = seed.step_number
  );

-- =====================================================
-- Seed template-level working paper sections
-- =====================================================

INSERT INTO audit_working_paper_sections (working_paper_id, section_order, section_code, section_title, section_type, content_text, is_required, review_status)
SELECT wp.id, seed.section_order, seed.section_code, seed.section_title, seed.section_type, seed.content_text, seed.is_required, 'Draft'
FROM audit_working_papers wp
INNER JOIN (
    VALUES
        ('WP-TPL-PLAN-001', 1, 'OBJ', 'Objective and Background', 'Narrative', 'Capture engagement purpose, business context, and planning objective.', TRUE),
        ('WP-TPL-PLAN-001', 2, 'SCOPE', 'Scope and Coverage', 'Narrative', 'Document planned scope, exclusions, and coverage rationale.', TRUE),
        ('WP-TPL-PLAN-001', 3, 'RISK', 'Risk Focus', 'Narrative', 'Document key risk themes, materiality, and strategy alignment.', TRUE),
        ('WP-TPL-WALK-001', 1, 'FLOW', 'Process Narrative', 'Narrative', 'Document process flow, key actors, and handoffs.', TRUE),
        ('WP-TPL-WALK-001', 2, 'EVID', 'Evidence Inspected', 'Evidence', 'List screenshots, reports, and documents inspected during the walkthrough.', TRUE),
        ('WP-TPL-WALK-001', 3, 'EXC', 'Exceptions', 'Conclusion', 'Record observed exceptions and resulting actions.', TRUE),
        ('WP-TPL-CTRL-001', 1, 'POP', 'Population and Sampling', 'Schedule', 'Document population details, sample size, and sample basis.', TRUE),
        ('WP-TPL-CTRL-001', 2, 'TEST', 'Test Results', 'Schedule', 'Document sample-by-sample results and exceptions.', TRUE),
        ('WP-TPL-CTRL-001', 3, 'CONC', 'Conclusion', 'Conclusion', 'Summarize control design and operating effectiveness conclusion.', TRUE),
        ('WP-TPL-REPORT-001', 1, 'FIND', 'Findings Summary', 'Narrative', 'Summarize final findings and ratings.', TRUE),
        ('WP-TPL-REPORT-001', 2, 'RESP', 'Management Responses', 'Narrative', 'Capture management responses and remediation commitments.', TRUE),
        ('WP-TPL-REPORT-001', 3, 'ISSUE', 'Issue Readiness', 'Checklist', 'Confirm unresolved items, review notes, and sign-offs before report issue.', TRUE)
) AS seed(working_paper_code, section_order, section_code, section_title, section_type, content_text, is_required)
    ON seed.working_paper_code = wp.working_paper_code
WHERE wp.is_template = TRUE
  AND NOT EXISTS (
      SELECT 1
      FROM audit_working_paper_sections existing
      WHERE existing.working_paper_id = wp.id
        AND existing.section_order = seed.section_order
  );
