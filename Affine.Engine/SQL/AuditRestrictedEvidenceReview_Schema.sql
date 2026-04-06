-- ===============================================
-- RESTRICTED EVIDENCE CATEGORY DEFAULTS & SECURITY REVIEW
-- ===============================================
-- Adds sensitive document-category defaults and a document-level
-- security review state for restricted uploads.
--
-- Schema: Risk_Assess_Framework
-- Date: 2026-03-10
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

ALTER TABLE ra_document_category
    ADD COLUMN IF NOT EXISTS is_sensitive BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS default_visibility_level_id INTEGER REFERENCES ra_document_visibility_level(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS requires_security_approval BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS default_confidentiality_label VARCHAR(150);

ALTER TABLE audit_documents
    ADD COLUMN IF NOT EXISTS security_review_required BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS security_review_status VARCHAR(50) DEFAULT 'Not Required',
    ADD COLUMN IF NOT EXISTS security_review_requested_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS security_review_requested_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS security_review_requested_by_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS security_reviewed_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS security_reviewed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS security_reviewed_by_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS security_review_notes TEXT;

WITH restricted_visibility AS (
    SELECT id
    FROM ra_document_visibility_level
    WHERE LOWER(name) = LOWER('Restricted')
    LIMIT 1
)
UPDATE ra_document_category
SET
    is_sensitive = TRUE,
    default_visibility_level_id = restricted_visibility.id,
    requires_security_approval = TRUE,
    default_confidentiality_label = seeded.default_confidentiality_label
FROM restricted_visibility,
(
    VALUES
        ('Payroll Evidence', 'Payroll'),
        ('HR Records', 'Human Resources'),
        ('Legal & Compliance', 'Legal'),
        ('Executive / Board Material', 'Executive'),
        ('PII / Privacy', 'Personal Information')
) AS seeded(name, default_confidentiality_label)
WHERE LOWER(ra_document_category.name) = LOWER(seeded.name);

WITH restricted_visibility AS (
    SELECT id
    FROM ra_document_visibility_level
    WHERE LOWER(name) = LOWER('Restricted')
    LIMIT 1
)
INSERT INTO ra_document_category
(
    name,
    description,
    color,
    sort_order,
    is_sensitive,
    default_visibility_level_id,
    requires_security_approval,
    default_confidentiality_label
)
SELECT
    seeded.name,
    seeded.description,
    seeded.color,
    seeded.sort_order,
    TRUE,
    restricted_visibility.id,
    TRUE,
    seeded.default_confidentiality_label
FROM restricted_visibility,
(
    VALUES
        ('Payroll Evidence', 'Payroll registers, remuneration schedules, and related payroll support.', '#DC2626', 20, 'Payroll'),
        ('HR Records', 'Personnel files, contracts, disciplinary records, and HR support.', '#B91C1C', 21, 'Human Resources'),
        ('Legal & Compliance', 'Legal opinions, contracts under dispute, and sensitive compliance evidence.', '#7F1D1D', 22, 'Legal'),
        ('Executive / Board Material', 'Board packs, executive compensation, and sensitive leadership material.', '#991B1B', 23, 'Executive'),
        ('PII / Privacy', 'Documents containing personal or privacy-sensitive information.', '#BE123C', 24, 'Personal Information')
) AS seeded(name, description, color, sort_order, default_confidentiality_label)
WHERE NOT EXISTS (
    SELECT 1
    FROM ra_document_category existing
    WHERE LOWER(existing.name) = LOWER(seeded.name)
);

UPDATE audit_documents d
SET
    security_review_required = COALESCE(d.security_review_required, FALSE) OR COALESCE(c.requires_security_approval, FALSE),
    security_review_status = CASE
        WHEN COALESCE(c.requires_security_approval, FALSE) THEN COALESCE(NULLIF(d.security_review_status, ''), 'Approved')
        ELSE COALESCE(NULLIF(d.security_review_status, ''), 'Not Required')
    END
FROM ra_document_category c
WHERE d.category_id = c.id;
