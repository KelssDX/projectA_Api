-- ===============================================
-- AUDIT WORKFLOW PHASE 3 FOUNDATION SCHEMA
-- ===============================================
-- This script adds workflow linkage, inbox tasking,
-- and notifications to support Elsa-backed audit flows.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-07
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS audit_workflow_instances (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    workflow_definition_id VARCHAR(255) NOT NULL,
    workflow_display_name VARCHAR(255),
    workflow_instance_id VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(100) NOT NULL DEFAULT 'Running',
    current_activity_id VARCHAR(255),
    current_activity_name VARCHAR(255),
    started_by_user_id INTEGER,
    started_by_name VARCHAR(255),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP,
    completed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_workflow_instances_reference_id
    ON audit_workflow_instances(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_workflow_instances_entity
    ON audit_workflow_instances(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_workflow_instances_status
    ON audit_workflow_instances(status, is_active);

CREATE TABLE IF NOT EXISTS audit_workflow_tasks (
    id SERIAL PRIMARY KEY,
    workflow_instance_id VARCHAR(255) NOT NULL REFERENCES audit_workflow_instances(workflow_instance_id) ON DELETE CASCADE,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    task_title VARCHAR(255) NOT NULL,
    task_description TEXT,
    assignee_user_id INTEGER,
    assignee_name VARCHAR(255),
    status VARCHAR(100) NOT NULL DEFAULT 'Pending',
    priority VARCHAR(50) DEFAULT 'Medium',
    due_date TIMESTAMP,
    action_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    completed_by_user_id INTEGER,
    completion_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_workflow_tasks_assignee
    ON audit_workflow_tasks(assignee_user_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_workflow_tasks_reference_id
    ON audit_workflow_tasks(reference_id);

CREATE TABLE IF NOT EXISTS audit_notifications (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    workflow_instance_id VARCHAR(255) REFERENCES audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL,
    notification_type VARCHAR(100) DEFAULT 'Workflow',
    severity VARCHAR(50) DEFAULT 'Info',
    title VARCHAR(255) NOT NULL,
    message TEXT,
    recipient_user_id INTEGER,
    recipient_name VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    action_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_notifications_recipient
    ON audit_notifications(recipient_user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_audit_notifications_reference_id
    ON audit_notifications(reference_id);

CREATE TABLE IF NOT EXISTS audit_workflow_events (
    id SERIAL PRIMARY KEY,
    workflow_instance_id VARCHAR(255) NOT NULL REFERENCES audit_workflow_instances(workflow_instance_id) ON DELETE CASCADE,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    event_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    actor_user_id INTEGER,
    actor_name VARCHAR(255),
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_workflow_events_reference_id
    ON audit_workflow_events(reference_id, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_audit_workflow_events_workflow_instance_id
    ON audit_workflow_events(workflow_instance_id, event_time DESC);
