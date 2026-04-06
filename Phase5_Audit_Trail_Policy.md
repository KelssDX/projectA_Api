# Phase 5 Audit Trail Policy

## Purpose

Define what the platform must record in the audit trail and how those records should be retained, reviewed, and correlated to workflow activity.

## Business Event Policy

The system should record append-only business events for:

- planning updates and sign-off actions
- scope item create, update, and delete actions
- risk and control matrix changes
- procedure create, clone, update, and delete actions
- walkthrough create, update, exception, and delete actions
- working paper create, review, sign-off, cross-reference, and delete actions
- document upload, delete, request, review, and fulfilment actions
- finding and recommendation lifecycle actions
- management action lifecycle actions
- workflow launch and task-completion actions

## Field-Level Change Policy

Field-level changes should be captured when:

- a sensitive business value is updated
- a sign-off or approval attribute changes
- a due date, status, severity, or owner changes
- a management response or conclusion changes

The platform should store field-level changes in `audit_trail_entity_changes` with:

- field name
- old value
- new value
- parent audit trail event ID

## Document Access Policy

Document access should be captured as audit-trail events with category `Document` for:

- upload
- delete
- open / view
- download
- evidence-request review actions

## Workflow Transition Policy

Workflow transition events should be recorded for:

- workflow launch
- task assignment
- task completion
- Elsa status synchronization
- overdue reminder / escalation events where relevant

Workflow events must carry:

- `workflow_instance_id`
- domain `reference_id`
- `entity_type`
- `entity_id`
- optional `correlation_id` for source object IDs

## Immutable History Policy

The following entities require immutable history:

- engagement planning records
- scope items
- procedures
- walkthroughs
- working papers
- findings
- recommendations
- management actions
- documents and evidence requests
- workflow tasks and approvals

Audit trail records themselves must never be updated in place other than archival movement.

## Correlation Strategy

Use these keys to correlate platform events:

- `reference_id` for engagement-level review
- `entity_type` + `entity_id` for domain drill-down
- `workflow_instance_id` for Elsa-linked actions
- `correlation_id` for source-object or external-system correlation

## Viewer Requirements

The frontend viewer should provide:

- recent-event timeline
- category totals
- filtering by category, entity type, and date range later
- drill-down to field-level changes
- workflow-linked event visibility
- export-ready chronological ordering

## Export and Review Requirements

Audit trail review exports should support:

- PDF summary for review packs
- Excel / CSV export for detailed inspection
- reference-level filtering
- inclusion of field-level change rows
- inclusion of workflow instance references

## Retention and Archival Rules

- retain active audit trail records with live engagements
- move closed engagements to archive storage based on retention policy
- retain workflow-linked approvals and sign-off history for the full audit retention term
- do not purge records needed for legal, regulatory, or quality-review purposes
- archival jobs should preserve referential integrity between events and change rows

## Current Implementation Note

This phase implements:

- `audit_trail_events`
- `audit_trail_entity_changes`
- backend audit-trail write service
- assessment-level audit-trail viewer
- workflow-start and workflow-complete audit trail writes

Further enhancement later should add:

- server-side recording for document open/download events
- broader controller-level field-diff capture
- export UI from the audit-trail tab
- retention automation
