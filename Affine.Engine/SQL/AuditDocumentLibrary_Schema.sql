-- ===============================================
-- AUDIT DOCUMENT LIBRARY & EVIDENCE REQUESTS SCHEMA
-- ===============================================
-- This script creates a document library for audit evidence,
-- plus evidence request tracking for engagement support.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-07
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

-- ===============================================
-- SECTION 1: DOCUMENT LOOKUPS
-- ===============================================

CREATE TABLE IF NOT EXISTS ra_document_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_document_category (name, description, color, sort_order) VALUES
('Scope Letter', 'Formal engagement or scope letter for the audit', '#1D4ED8', 1),
('Planning Support', 'Planning schedules, scoping notes, and planning evidence', '#0F766E', 2),
('Walkthrough Evidence', 'Evidence collected during walkthroughs', '#7C3AED', 3),
('Control Testing Evidence', 'Evidence supporting control testing execution', '#EA580C', 4),
('Substantive Testing Evidence', 'Evidence supporting substantive procedures', '#DC2626', 5),
('Analytics Output', 'Analytics extracts, data files, and report outputs', '#2563EB', 6),
('Working Paper Support', 'Documents referenced by working papers', '#16A34A', 7),
('Finding Support', 'Evidence supporting a finding or recommendation', '#B45309', 8),
('Management Response', 'Responses, action plans, and remediation support', '#9333EA', 9),
('Final Reporting', 'Draft and final report packs', '#334155', 10)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS ra_evidence_request_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    is_closed BOOLEAN DEFAULT FALSE,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_evidence_request_status (name, description, color, is_closed, sort_order) VALUES
('Draft', 'Request has been drafted but not yet sent', '#6B7280', FALSE, 1),
('Sent', 'Request has been issued to the information owner', '#2563EB', FALSE, 2),
('In Progress', 'The request is being worked on by the information owner', '#F59E0B', FALSE, 3),
('Partially Fulfilled', 'Some requested evidence has been received', '#7C3AED', FALSE, 4),
('Fulfilled', 'All requested evidence has been received', '#16A34A', FALSE, 5),
('Closed', 'The request has been reviewed and closed', '#0F766E', TRUE, 6),
('Cancelled', 'The request has been cancelled', '#DC2626', TRUE, 7)
ON CONFLICT (name) DO NOTHING;

-- ===============================================
-- SECTION 2: DOCUMENT LIBRARY
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_documents (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    audit_universe_id INTEGER REFERENCES audit_universe(id) ON DELETE SET NULL,
    procedure_id INTEGER REFERENCES audit_procedures(id) ON DELETE SET NULL,
    working_paper_id INTEGER REFERENCES audit_working_papers(id) ON DELETE SET NULL,
    finding_id INTEGER REFERENCES audit_findings(id) ON DELETE SET NULL,
    recommendation_id INTEGER REFERENCES audit_recommendations(id) ON DELETE SET NULL,
    document_code VARCHAR(50) UNIQUE,
    title VARCHAR(500) NOT NULL,
    original_file_name VARCHAR(500) NOT NULL,
    stored_file_name VARCHAR(500) NOT NULL,
    stored_relative_path VARCHAR(1000) NOT NULL,
    content_type VARCHAR(255),
    file_extension VARCHAR(50),
    file_size BIGINT,
    category_id INTEGER REFERENCES ra_document_category(id) ON DELETE SET NULL,
    source_type VARCHAR(100) DEFAULT 'Audit Team',
    tags TEXT,
    notes TEXT,
    uploaded_by_name VARCHAR(255),
    uploaded_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE audit_documents IS 'Central engagement document and evidence library';
COMMENT ON COLUMN audit_documents.source_type IS 'Typical values: Audit Team, Client, Management, System, Third Party';

CREATE OR REPLACE FUNCTION generate_document_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.document_code IS NULL THEN
        NEW.document_code := 'DOC-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                             LPAD(nextval('audit_documents_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_generate_document_code ON audit_documents;
CREATE TRIGGER trigger_generate_document_code
    BEFORE INSERT ON audit_documents
    FOR EACH ROW
    EXECUTE FUNCTION generate_document_code();

CREATE INDEX IF NOT EXISTS idx_audit_documents_reference_id ON audit_documents(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_documents_category_id ON audit_documents(category_id);
CREATE INDEX IF NOT EXISTS idx_audit_documents_procedure_id ON audit_documents(procedure_id);
CREATE INDEX IF NOT EXISTS idx_audit_documents_working_paper_id ON audit_documents(working_paper_id);
CREATE INDEX IF NOT EXISTS idx_audit_documents_finding_id ON audit_documents(finding_id);
CREATE INDEX IF NOT EXISTS idx_audit_documents_recommendation_id ON audit_documents(recommendation_id);

-- ===============================================
-- SECTION 3: EVIDENCE REQUESTS
-- ===============================================

CREATE TABLE IF NOT EXISTS audit_evidence_requests (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    audit_universe_id INTEGER REFERENCES audit_universe(id) ON DELETE SET NULL,
    request_number VARCHAR(50) UNIQUE,
    title VARCHAR(500) NOT NULL,
    request_description TEXT,
    requested_from VARCHAR(255),
    requested_to_email VARCHAR(255),
    priority INTEGER DEFAULT 2,
    due_date DATE,
    status_id INTEGER REFERENCES ra_evidence_request_status(id) DEFAULT 2,
    requested_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    requested_by_name VARCHAR(255),
    workflow_instance_id VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_evidence_requests IS 'Evidence or document requests issued during audit execution';
COMMENT ON COLUMN audit_evidence_requests.priority IS '1=High, 2=Medium, 3=Low';

CREATE OR REPLACE FUNCTION generate_evidence_request_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.request_number IS NULL THEN
        NEW.request_number := 'EDR-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                              LPAD(nextval('audit_evidence_requests_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_generate_evidence_request_number ON audit_evidence_requests;
CREATE TRIGGER trigger_generate_evidence_request_number
    BEFORE INSERT ON audit_evidence_requests
    FOR EACH ROW
    EXECUTE FUNCTION generate_evidence_request_number();

CREATE OR REPLACE FUNCTION update_evidence_request_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_evidence_request_updated_at ON audit_evidence_requests;
CREATE TRIGGER trigger_update_evidence_request_updated_at
    BEFORE UPDATE ON audit_evidence_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_evidence_request_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_evidence_requests_reference_id ON audit_evidence_requests(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_evidence_requests_status_id ON audit_evidence_requests(status_id);
CREATE INDEX IF NOT EXISTS idx_audit_evidence_requests_due_date ON audit_evidence_requests(due_date);

CREATE TABLE IF NOT EXISTS audit_evidence_request_items (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES audit_evidence_requests(id) ON DELETE CASCADE,
    item_description TEXT NOT NULL,
    expected_document_type VARCHAR(255),
    is_required BOOLEAN DEFAULT TRUE,
    fulfilled_document_id INTEGER REFERENCES audit_documents(id) ON DELETE SET NULL,
    submitted_at TIMESTAMP,
    reviewer_notes TEXT,
    reviewed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    is_accepted BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_evidence_request_items IS 'Individual evidence items requested under a single request';
COMMENT ON COLUMN audit_evidence_request_items.fulfilled_document_id IS 'Document uploaded to fulfill this request item';

CREATE INDEX IF NOT EXISTS idx_audit_evidence_request_items_request_id ON audit_evidence_request_items(request_id);
CREATE INDEX IF NOT EXISTS idx_audit_evidence_request_items_fulfilled_document_id ON audit_evidence_request_items(fulfilled_document_id);

