# Phase 3 Elsa Operational Readiness and Naming Standards

## Purpose

This document records the current Elsa workflow operational posture in the repo and defines workflow naming standards for the auditing platform.

## Current Topology

- Workflow runtime/API server: `Affine.Auditing.Workflows.Server`
- Workflow designer/studio: `Affine.Auditing.Workflows.Studio`
- Auditing application integration point: `Affine.Auditing.API`

## Current Local Configuration

### Workflow Server

- Base URL: `https://localhost:5001`
- Base API path: `/elsa/api`
- Config source: `Affine.Auditing.Workflows.Server/appsettings.json`

### Workflow Studio

- Default local URL: `https://localhost:7001`
- Backend API target: `https://localhost:5001/elsa/api`
- Config sources:
  - `Affine.Auditing.Workflows.Studio/Properties/launchSettings.json`
  - `Affine.Auditing.Workflows.Studio/wwwroot/appsettings.json`

### Auditing API

- Local Elsa dispatch target: `WorkflowServiceUrl`
- Current default: `https://localhost:5001` in `Affine.Auditing.API/appsettings.json`
- This now matches the local Elsa workflow server default

## Current Readiness Assessment

### Working Now

- Elsa server and studio projects exist in the repo
- The auditing API can dispatch workflows through a shared workflow service
- The auditing DB now stores local workflow instances, tasks, notifications, and workflow events
- The frontend now has a workflow inbox and Elsa Studio launchpoint
- The auditing app now exposes launch paths for:
  - annual audit plan approval
  - planning approval
  - scope approval
  - walkthrough review
  - control testing
  - working paper review
  - finding review
  - management response
  - remediation follow-up
  - final report sign-off
- The auditing API now exposes a workflow status sync endpoint for Elsa runtime callbacks:
  - `POST /api/v1/AuditWorkflow/SyncElsaState`
- The Elsa workflow server now registers the audit workflow family in code for:
  - annual audit plan approval
  - planning approval
  - scope approval
  - control testing
  - walkthrough review
  - working paper review
  - finding review
  - management response
  - remediation follow-up
  - final report sign-off
- Each Elsa workflow now suspends on a completion callback route and then synchronizes terminal state back to the auditing API:
  - `POST /elsa/api/audit-callbacks/{workflowInstanceId}/complete`
- Completing a workflow task through the auditing API now calls the Elsa completion callback route automatically
- The auditing API now runs workflow reminder and escalation sweeps:
  - background hosted service
  - manual endpoint: `POST /api/v1/AuditWorkflow/RunReminderSweep`
- The assessment details screen now shows persisted workflow activity in its audit activity feed

### Gaps Before Production

- Hardcoded signing key exists in the workflow server
- Admin API-key based setup is enabled and should be replaced or tightly controlled per environment
- CORS is currently `AllowAnyOrigin`
- Localhost URLs are still embedded in local configuration
- No documented environment-specific secret management strategy is present for Elsa auth/secrets
- No explicit health check/observability layer is in place for workflow runtime failures
- No role-based authorization model is yet documented for who can access Elsa Studio
- No deployment checklist exists yet for workflow promotion across environments
- Elsa workflows currently implement a completion callback path; richer outcome branches such as rejection/rework are not yet modeled

## Required Hardening Actions

1. Move workflow signing keys and admin credentials into secure environment-based configuration.
2. Replace permissive CORS with explicit allowed origins.
3. Align `WorkflowServiceUrl`, workflow server URL, and studio URL per environment.
4. Add health checks and structured logging for workflow dispatch and sync failures.
5. Define a secure Elsa Studio access model for admins only.
6. Define deployment/version promotion rules for workflow definitions.
7. Align the reminder hosted service interval and thresholds per environment.
8. Add environment-specific authorization and secrets management for Elsa Studio and server.

## Workflow Definition Naming Standard

Use this format:

`Audit.<Domain>.<Process>.<Stage>.v<Major>`

Examples:

- `Audit.Planning.AnnualPlanApproval.v1`
- `Audit.Planning.PlanningApproval.v1`
- `Audit.Planning.ScopeApproval.v1`
- `Audit.Execution.WalkthroughReview.v1`
- `Audit.Execution.ControlTesting.v1`
- `Audit.Execution.WorkpaperReview.v1`
- `Audit.Reporting.ManagementResponse.v1`
- `Audit.Reporting.FinalSignOff.v1`
- `Audit.FollowUp.RemediationReview.v1`

## Activity Naming Standard

Use this format:

`<Process><Action>Activity`

Examples:

- `ControlTestingActivity`
- `ScopeApprovalActivity`
- `WorkpaperReviewActivity`
- `FindingApprovalActivity`

## Task Naming Standard

Use this format:

`<Verb> <Object> for <Context>`

Examples:

- `Perform control testing for CTRL-001`
- `Review working paper for Revenue`
- `Approve audit scope for Engagement 2026-01`

## Notification Naming Standard

Use this format:

`<Process> <Event> for <Context>`

Examples:

- `Control testing started for CTRL-001`
- `Working paper review due for Revenue`
- `Final sign-off pending for Engagement 2026-01`

## Local Integration Rule

Every launched audit workflow should persist these minimum fields locally:

- `reference_id`
- `entity_type`
- `entity_id`
- `workflow_definition_id`
- `workflow_instance_id`
- `status`
- `current_activity_name`
- `started_by_user_id`

This local record is the application-facing source for:

- workflow inbox views
- assessment workflow status
- notifications
- task routing
- later audit trail linkage

## Current Phase 3 Recommendation

Short term:

- continue using the shared workflow service plus local workflow tables as the app-facing workflow backbone

Next:

- add admin workflow management and promotion controls
- add rejection, rework, and escalation branches inside Elsa workflow definitions
- harden Elsa auth, secrets, and CORS per environment
