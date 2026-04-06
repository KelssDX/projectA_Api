-- ===============================================
-- AUDIT WORKFLOW PHASE 3 RUNTASK CLOSEOUT
-- ===============================================
-- This patch stores Elsa RunTask identifiers on
-- audit workflow tasks so the audit application
-- can resume Elsa workflows through the native
-- Elsa tasks completion endpoint.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-03-08
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

ALTER TABLE IF EXISTS audit_workflow_tasks
    ADD COLUMN IF NOT EXISTS external_task_id VARCHAR(255);

ALTER TABLE IF EXISTS audit_workflow_tasks
    ADD COLUMN IF NOT EXISTS external_task_source VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_audit_workflow_tasks_external_task_id
    ON audit_workflow_tasks(external_task_id);
