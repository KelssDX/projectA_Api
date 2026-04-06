-- Phase 5: Enterprise Readiness
-- Retention policies, archival events, usage telemetry, and assessment archive metadata

SET search_path TO "Risk_Assess_Framework";

ALTER TABLE riskassessmentreference
    ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP NULL,
    ADD COLUMN IF NOT EXISTS archived_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS archived_by_name VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS archive_reason TEXT NULL;

CREATE INDEX IF NOT EXISTS idx_riskassessmentreference_is_archived
    ON riskassessmentreference(is_archived);

CREATE TABLE IF NOT EXISTS audit_retention_policies (
    id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL UNIQUE,
    entity_type VARCHAR(100) NOT NULL,
    retention_days INTEGER NOT NULL,
    archive_action VARCHAR(100) NOT NULL DEFAULT 'Archive',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_archival_events (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NULL REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    archive_action VARCHAR(100) NOT NULL,
    reason TEXT NULL,
    retention_policy_id INTEGER NULL REFERENCES audit_retention_policies(id) ON DELETE SET NULL,
    archived_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    archived_by_name VARCHAR(255) NULL,
    archived_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details_json TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_archival_events_reference_id
    ON audit_archival_events(reference_id);

CREATE INDEX IF NOT EXISTS idx_audit_archival_events_archived_at
    ON audit_archival_events(archived_at DESC);

CREATE TABLE IF NOT EXISTS audit_usage_events (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    reference_id INTEGER NULL REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    performed_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    performed_by_name VARCHAR(255) NULL,
    role_name VARCHAR(100) NULL,
    session_id VARCHAR(100) NULL,
    source VARCHAR(100) NULL,
    metadata_json TEXT NULL,
    event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_usage_events_module_time
    ON audit_usage_events(module_name, event_time DESC);

CREATE INDEX IF NOT EXISTS idx_audit_usage_events_reference_id
    ON audit_usage_events(reference_id);

INSERT INTO audit_retention_policies (policy_name, entity_type, retention_days, archive_action, notes)
VALUES
    ('Assessment Archive Policy', 'Assessment', 1095, 'Archive', 'Archive assessment references and packs three years after completion or closure.'),
    ('Workflow Notification Retention', 'WorkflowNotification', 365, 'Retain', 'Retain workflow notifications for one year for operational traceability.'),
    ('Analytics Import Batch Retention', 'AnalyticsImportBatch', 730, 'Retain', 'Retain analytics import batch records for two years for reconciliation and audit support.'),
    ('Audit Trail Retention', 'AuditTrail', 2555, 'Retain', 'Retain audit trail records for seven years unless stricter client policy applies.'),
    ('Document Evidence Retention', 'Document', 2555, 'Archive', 'Archive audit evidence and working documents for seven years unless client policy is longer.')
ON CONFLICT (policy_name) DO NOTHING;
