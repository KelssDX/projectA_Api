-- ===============================================
-- AUDIT PROJECT & FILE COLLABORATION SCHEMA
-- ===============================================
-- This script introduces collaborator role lookups and
-- assignment tables for audit projects and audit files.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-10
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS ra_audit_collaborator_role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    is_client_role BOOLEAN DEFAULT FALSE,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_audit_collaborator_role (name, description, color, is_client_role, sort_order) VALUES
('Audit Manager', 'Owns the project, can manage access, and can review or edit work.', '#1D4ED8', FALSE, 1),
('Senior Auditor', 'Leads fieldwork and coordinates day-to-day execution.', '#2563EB', FALSE, 2),
('Auditor', 'Performs standard audit work and uploads evidence.', '#0F766E', FALSE, 3),
('Reviewer', 'Reviews workpapers and evidence without being the project owner.', '#7C3AED', FALSE, 4),
('Client Owner', 'Client-side contact who can provide requested evidence and collaborate on requests.', '#B45309', TRUE, 5),
('Restricted Contributor', 'Limited-access contributor used for sensitive evidence areas such as payroll or HR.', '#DC2626', TRUE, 6)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS audit_project_collaborators (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    collaborator_role_id INTEGER REFERENCES ra_audit_collaborator_role(id) ON DELETE SET NULL,
    can_edit BOOLEAN NOT NULL DEFAULT TRUE,
    can_review BOOLEAN NOT NULL DEFAULT FALSE,
    can_upload_evidence BOOLEAN NOT NULL DEFAULT TRUE,
    can_manage_access BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    assigned_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_by_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

CREATE TABLE IF NOT EXISTS audit_reference_collaborators (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    collaborator_role_id INTEGER REFERENCES ra_audit_collaborator_role(id) ON DELETE SET NULL,
    can_edit BOOLEAN NOT NULL DEFAULT TRUE,
    can_review BOOLEAN NOT NULL DEFAULT FALSE,
    can_upload_evidence BOOLEAN NOT NULL DEFAULT TRUE,
    can_manage_access BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    assigned_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_by_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(reference_id, user_id)
);

CREATE OR REPLACE FUNCTION update_audit_collaborator_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_project_collaborators_updated_at ON audit_project_collaborators;
CREATE TRIGGER trigger_update_audit_project_collaborators_updated_at
    BEFORE UPDATE ON audit_project_collaborators
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_collaborator_updated_at();

DROP TRIGGER IF EXISTS trigger_update_audit_reference_collaborators_updated_at ON audit_reference_collaborators;
CREATE TRIGGER trigger_update_audit_reference_collaborators_updated_at
    BEFORE UPDATE ON audit_reference_collaborators
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_collaborator_updated_at();

CREATE INDEX IF NOT EXISTS idx_audit_project_collaborators_project_id
    ON audit_project_collaborators(project_id);

CREATE INDEX IF NOT EXISTS idx_audit_project_collaborators_user_id
    ON audit_project_collaborators(user_id);

CREATE INDEX IF NOT EXISTS idx_audit_reference_collaborators_reference_id
    ON audit_reference_collaborators(reference_id);

CREATE INDEX IF NOT EXISTS idx_audit_reference_collaborators_user_id
    ON audit_reference_collaborators(user_id);
