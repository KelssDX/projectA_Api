-- ===============================================
-- AUDIT DOCUMENT ACCESS CONTROL SCHEMA
-- ===============================================
-- This script extends the audit document library with
-- confidentiality-aware visibility and explicit grants.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-10
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS ra_document_visibility_level (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    is_restricted BOOLEAN DEFAULT FALSE,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_document_visibility_level (name, description, color, is_restricted, sort_order) VALUES
('Engagement Team', 'Visible to the broader audit team for the audit file.', '#2563EB', FALSE, 1),
('Managers and Reviewers', 'Visible to managers, partners, directors, reviewers, the uploader, and any explicitly granted users or roles.', '#7C3AED', TRUE, 2),
('Private Draft', 'Visible only to the uploader, managers, and any explicitly granted users or roles.', '#6B7280', TRUE, 3),
('Restricted', 'Visible only to the uploader, managers, and any explicitly granted users or roles.', '#DC2626', TRUE, 4)
ON CONFLICT (name) DO NOTHING;

ALTER TABLE audit_documents
    ADD COLUMN IF NOT EXISTS visibility_level_id INTEGER REFERENCES ra_document_visibility_level(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS confidentiality_label VARCHAR(150),
    ADD COLUMN IF NOT EXISTS confidentiality_reason TEXT;

UPDATE audit_documents
SET visibility_level_id = visibility.id
FROM (
    SELECT id
    FROM ra_document_visibility_level
    WHERE name = 'Engagement Team'
    LIMIT 1
) AS visibility
WHERE audit_documents.visibility_level_id IS NULL;

CREATE TABLE IF NOT EXISTS audit_document_permission_grants (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES audit_documents(id) ON DELETE CASCADE,
    grantee_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    grantee_role_name VARCHAR(100),
    permission_level VARCHAR(50) NOT NULL DEFAULT 'View',
    can_download BOOLEAN NOT NULL DEFAULT TRUE,
    granted_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    granted_by_name VARCHAR(255),
    notes TEXT,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    CONSTRAINT chk_audit_document_permission_grant_target
        CHECK (
            grantee_user_id IS NOT NULL
            OR NULLIF(BTRIM(COALESCE(grantee_role_name, '')), '') IS NOT NULL
        )
);

COMMENT ON TABLE audit_document_permission_grants IS 'Explicit user- or role-based visibility grants for confidential audit documents.';
COMMENT ON COLUMN audit_document_permission_grants.permission_level IS 'Current values include View and Manage.';

CREATE UNIQUE INDEX IF NOT EXISTS uq_audit_document_permission_grants_user
    ON audit_document_permission_grants(document_id, grantee_user_id, permission_level)
    WHERE grantee_user_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_audit_document_permission_grants_role
    ON audit_document_permission_grants(document_id, grantee_role_name, permission_level)
    WHERE grantee_role_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_audit_documents_visibility_level_id
    ON audit_documents(visibility_level_id);

CREATE INDEX IF NOT EXISTS idx_audit_document_permission_grants_document_id
    ON audit_document_permission_grants(document_id);

CREATE INDEX IF NOT EXISTS idx_audit_document_permission_grants_grantee_user_id
    ON audit_document_permission_grants(grantee_user_id);
