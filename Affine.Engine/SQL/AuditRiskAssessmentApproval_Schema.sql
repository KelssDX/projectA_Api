-- ===============================================
-- AUDIT RISK ASSESSMENT APPROVAL & DESCRIPTION ENHANCEMENTS
-- ===============================================
-- Adds richer description fields to riskassessment rows and
-- extends reference status options for audit-file lifecycle control.
--
-- Schema: Risk_Assess_Framework
-- Date: 2026-03-10
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

ALTER TABLE riskassessment
    ADD COLUMN IF NOT EXISTS businessobjectivedescription TEXT,
    ADD COLUMN IF NOT EXISTS riskdescription TEXT,
    ADD COLUMN IF NOT EXISTS controldescription TEXT,
    ADD COLUMN IF NOT EXISTS outcomedescription TEXT;

UPDATE riskassessment
SET businessobjectivedescription = COALESCE(businessobjectivedescription, businessobjectives)
WHERE businessobjectivedescription IS NULL;

UPDATE riskassessment
SET riskdescription = COALESCE(riskdescription, keyriskandfactors)
WHERE riskdescription IS NULL;

UPDATE riskassessment
SET controldescription = COALESCE(controldescription, mitigatingcontrols)
WHERE controldescription IS NULL;

UPDATE riskassessment
SET outcomedescription = COALESCE(outcomedescription, auditorsrecommendedactionplan)
WHERE outcomedescription IS NULL;

INSERT INTO ra_referencestatus (name, description, sort_order, is_active)
SELECT seed.name, seed.description, seed.sort_order, TRUE
FROM (
    VALUES
        ('Draft', 'Audit file is being prepared and remains editable.', 5),
        ('In Review', 'Audit file content is frozen for reviewer attention but not yet approved.', 10),
        ('Approved', 'Audit file has been approved and is locked against normal edits.', 20),
        ('Archived', 'Audit file has been archived and is locked for historical retention.', 30)
) AS seed(name, description, sort_order)
WHERE NOT EXISTS (
    SELECT 1
    FROM ra_referencestatus existing
    WHERE LOWER(existing.name) = LOWER(seed.name)
);
