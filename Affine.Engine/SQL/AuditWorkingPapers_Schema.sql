-- ===============================================
-- AUDIT WORKING PAPERS SCHEMA
-- ===============================================
-- This script creates working papers, sign-offs,
-- cross-references, and reusable templates.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-06
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

-- ===============================================
-- SECTION 1: STATUS LOOKUP
-- ===============================================

CREATE TABLE IF NOT EXISTS ra_working_paper_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    is_closed BOOLEAN DEFAULT FALSE,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_working_paper_status (name, description, color, is_closed, sort_order) VALUES
('Draft', 'Working paper has been created but not yet prepared', '#6B7280', FALSE, 1),
('In Preparation', 'Working paper is being prepared by the audit team', '#2563EB', FALSE, 2),
('Ready for Review', 'Working paper is complete and ready for review', '#F59E0B', FALSE, 3),
('Review Notes Raised', 'Reviewer has raised notes that require rework', '#DC2626', FALSE, 4),
('Approved', 'Working paper has been reviewed and signed off', '#16A34A', TRUE, 5),
('Archived', 'Working paper is complete and archived', '#374151', TRUE, 6)
ON CONFLICT (name) DO NOTHING;

-- ===============================================
-- SECTION 2: WORKING PAPERS
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_working_papers (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    audit_universe_id INTEGER REFERENCES audit_universe(id) ON DELETE SET NULL,
    procedure_id INTEGER REFERENCES audit_procedures(id) ON DELETE SET NULL,
    working_paper_code VARCHAR(50) UNIQUE,
    title VARCHAR(500) NOT NULL,
    objective TEXT,
    description TEXT,
    status_id INTEGER REFERENCES ra_working_paper_status(id) DEFAULT 1,
    prepared_by VARCHAR(255),
    prepared_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewer_name VARCHAR(255),
    reviewer_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    conclusion TEXT,
    notes TEXT,
    prepared_date DATE,
    reviewed_date DATE,
    is_template BOOLEAN DEFAULT FALSE,
    source_template_id INTEGER REFERENCES audit_working_papers(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_working_papers IS 'Audit working papers and reusable working paper templates';
COMMENT ON COLUMN audit_working_papers.is_template IS 'True when the record is a reusable working paper template';
COMMENT ON COLUMN audit_working_papers.source_template_id IS 'Original template used to create this working paper';

CREATE OR REPLACE FUNCTION generate_working_paper_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.working_paper_code IS NULL THEN
        NEW.working_paper_code := 'WP-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                                  LPAD(nextval('audit_working_papers_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_generate_working_paper_code ON audit_working_papers;
CREATE TRIGGER trigger_generate_working_paper_code
    BEFORE INSERT ON audit_working_papers
    FOR EACH ROW
    EXECUTE FUNCTION generate_working_paper_code();

CREATE OR REPLACE FUNCTION update_working_paper_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_working_paper_updated_at ON audit_working_papers;
CREATE TRIGGER trigger_update_working_paper_updated_at
    BEFORE UPDATE ON audit_working_papers
    FOR EACH ROW
    EXECUTE FUNCTION update_working_paper_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_working_papers_reference_id ON audit_working_papers(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_working_papers_status_id ON audit_working_papers(status_id);
CREATE INDEX IF NOT EXISTS idx_audit_working_papers_procedure_id ON audit_working_papers(procedure_id);
CREATE INDEX IF NOT EXISTS idx_audit_working_papers_is_template ON audit_working_papers(is_template);

-- ===============================================
-- SECTION 3: SIGN-OFF HISTORY
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_working_paper_signoffs (
    id SERIAL PRIMARY KEY,
    working_paper_id INTEGER NOT NULL REFERENCES audit_working_papers(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    signed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    signed_by_name VARCHAR(255),
    comment TEXT,
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wp_signoffs_working_paper_id ON audit_working_paper_signoffs(working_paper_id);

-- ===============================================
-- SECTION 4: CROSS-REFERENCES
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_working_paper_references (
    id SERIAL PRIMARY KEY,
    from_working_paper_id INTEGER NOT NULL REFERENCES audit_working_papers(id) ON DELETE CASCADE,
    to_working_paper_id INTEGER NOT NULL REFERENCES audit_working_papers(id) ON DELETE CASCADE,
    reference_type VARCHAR(100) DEFAULT 'Supporting',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_working_paper_id, to_working_paper_id, reference_type)
);

CREATE INDEX IF NOT EXISTS idx_wp_references_from_id ON audit_working_paper_references(from_working_paper_id);
CREATE INDEX IF NOT EXISTS idx_wp_references_to_id ON audit_working_paper_references(to_working_paper_id);

-- ===============================================
-- SECTION 5: TEMPLATE SEED DATA
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
    is_template
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
    TRUE
FROM (
    VALUES
    (
        'WP-TPL-PLAN-001',
        'Planning memorandum',
        'Document planning decisions, scope, and risk focus for the engagement.',
        'Capture engagement background, scope, timing, team allocation, and key risk areas for planning sign-off.',
        'Approved',
        'Audit Manager',
        'Head of Audit',
        'Planning completed and signed off.',
        'Useful for planning and scoping review.'
    ),
    (
        'WP-TPL-WALK-001',
        'Walkthrough narrative and evidence',
        'Document walkthrough steps, participants, and evidence inspected.',
        'Store process narrative, screenshots, walkthrough notes, and exceptions raised during process understanding.',
        'Approved',
        'Senior Auditor',
        'Audit Manager',
        'Walkthrough completed and evidence retained.',
        'Supports walkthrough and control design work.'
    ),
    (
        'WP-TPL-CTRL-001',
        'Control testing worksheet',
        'Capture the sample, exceptions, and conclusion for control testing.',
        'Document population, sample selection, test attributes, exceptions, root cause, and final conclusion.',
        'Approved',
        'Audit Associate',
        'Senior Auditor',
        'Control test evidence captured and reviewed.',
        'Reusable for recurring control testing.'
    ),
    (
        'WP-TPL-REPORT-001',
        'Findings and reporting summary',
        'Summarize final findings, responses, and reporting considerations.',
        'Track draft report references, unresolved review notes, and final issue summary before report issue.',
        'Approved',
        'Audit Manager',
        'Head of Audit',
        'Report completion file ready for issue.',
        'Useful at completion and reporting stage.'
    )
) AS seed(working_paper_code, title, objective, description, status_name, prepared_by, reviewer_name, conclusion, notes)
INNER JOIN ra_working_paper_status st ON st.name = seed.status_name
WHERE NOT EXISTS (
    SELECT 1
    FROM audit_working_papers existing
    WHERE existing.working_paper_code = seed.working_paper_code
);

-- ===============================================
-- END OF SCRIPT
-- ===============================================
