-- =====================================================
-- Phase 5: Audit Trail Schema
-- Purpose:
--   Add append-only audit trail storage for business events,
--   workflow transitions, document activity, and field changes.
-- =====================================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS audit_trail_events (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255) NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'Business',
    action VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    performed_by_user_id INTEGER NULL,
    performed_by_name VARCHAR(255) NULL,
    icon VARCHAR(50) NULL,
    color VARCHAR(20) NULL,
    workflow_instance_id VARCHAR(255) NULL,
    correlation_id VARCHAR(255) NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'Application',
    details_json JSONB NULL,
    event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_trail_events_reference_time
    ON audit_trail_events(reference_id, event_time DESC);

CREATE INDEX IF NOT EXISTS idx_audit_trail_events_entity
    ON audit_trail_events(entity_type, entity_id, event_time DESC);

CREATE INDEX IF NOT EXISTS idx_audit_trail_events_workflow
    ON audit_trail_events(workflow_instance_id, event_time DESC);

CREATE TABLE IF NOT EXISTS audit_trail_entity_changes (
    id BIGSERIAL PRIMARY KEY,
    audit_trail_event_id BIGINT NOT NULL REFERENCES audit_trail_events(id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    old_value TEXT NULL,
    new_value TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_trail_entity_changes_event
    ON audit_trail_entity_changes(audit_trail_event_id);
