# Auditing App Implementation Task Tracker

## Purpose

This document turns the gap analysis into an implementation tracker with:

- phases
- tasks
- progress status
- completion tracking

Status key:

- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed
- `[-]` Deferred / later phase

Overall progress should be updated as implementation moves forward.

---

## Overall Progress

- Phase 1: 100%
- Phase 2: 100%
- Phase 3: 100%
- Phase 4: 100%
- Phase 5: 100%
- Materiality Calculation Expansion: 100%
- Post-Demo Audit Core Backlog: 96%

---

## Phase 1: Stabilize and Complete Existing Foundations

### Goal

Complete and harden the features that already exist partially in the repo so the system becomes reliable before major expansion.

### Progress

- Status: `[x] Completed`
- Completion: `100%`

### Tasks

- `[x]` Add Microsoft Power BI as an optional mode entry point in the Analytical Report view
- `[x]` Confirm and document all current auditing-related modules that already exist in backend and frontend
- `[x]` Complete findings frontend using existing findings API
- `[x]` Complete recommendations frontend using existing recommendations API
- `[x]` Add management response capture and display flow in the frontend
- `[x]` Replace placeholder `Add Finding` logic in assessment details with real CRUD
- `[x]` Replace placeholder comment and collaboration actions with real persistence
- `[x]` Replace placeholder report generation actions with real report workflows
- `[x]` Make workflow status in assessment views reflect actual Elsa or domain state
- `[x]` Surface findings aging drill-down into a working findings screen
- `[x]` Review and fix broken or misleading labels that still reflect risk-only wording instead of audit wording
- `[x]` Validate audit universe linkage to departments, projects, risks, and findings
- `[x]` Validate existing findings/recommendations analytics against frontend consumption
- `[x]` Add implementation notes for all stubs currently present in `modern_details.py`
- `[x]` Define audit trail scope for Phase 1 entities and actions

### Deliverables

- functioning findings UI
- functioning recommendations UI
- real management response flow
- clearer workflow state display
- reduced placeholder UX
- audit trail scope defined for current modules
- Phase 1 validation and closeout notes documented

---

## Phase 2: Add Core Audit Execution Modules

### Goal

Shift the product from risk-and-analytics heavy toward actual audit execution.

### Progress

- Status: `[x] Completed`
- Completion: `100%`

### Tasks

#### 2.1 Planning and Scoping

- `[x]` Create audit engagement module
- `[x]` Create annual audit plan model
- `[x]` Add scope definition by business unit, process, subprocess, and FSLI where applicable
- `[x]` Add planning workspace UI
- `[x]` Add scope letter / engagement letter attachment support
- `[x]` Add planning sign-off state
- `[x]` Add internal audit vs external audit engagement type selector

#### 2.2 Risk and Control Matrix

- `[x]` Create dedicated risk and control matrix UI
- `[x]` Add risk description fields consistently across relevant views
- `[x]` Add control description fields consistently across relevant views
- `[x]` Add control adequacy field
- `[x]` Add control effectiveness field
- `[x]` Add control classification lookup:
- `[x]` Add `Preventive`
- `[x]` Add `Detective`
- `[x]` Add `Corrective`
- `[x]` Add control frequency
- `[x]` Add control owner
- `[x]` Add control type:
- `[x]` Add `Manual`
- `[x]` Add `Automated`
- `[x]` Add `IT Dependent`

#### 2.3 Procedure Library

- `[x]` Create procedure library data model
- `[x]` Create procedure categories:
- `[x]` Add `Planning`
- `[x]` Add `Walkthrough`
- `[x]` Add `Control Testing`
- `[x]` Add `Substantive Analytics`
- `[x]` Add `Substantive Testing`
- `[x]` Add `Reporting`
- `[x]` Create procedure library management UI
- `[x]` Allow procedures to be assigned to engagements
- `[x]` Allow procedures to be assigned to scope items
- `[x]` Allow procedures to be assigned to risks and controls
- `[x]` Allow procedures to be assigned to working papers

#### 2.4 Working Papers

- `[x]` Create working paper data model
- `[x]` Create working paper list and detail views
- `[x]` Add working paper status lifecycle
- `[x]` Add preparer and reviewer assignment
- `[x]` Add conclusion field
- `[x]` Add cross-reference links
- `[x]` Add sign-off history
- `[x]` Add working paper templates

#### 2.5 Walkthroughs

- `[x]` Create walkthrough data model
- `[x]` Create walkthrough UI
- `[x]` Add participants, dates, and process narrative
- `[x]` Add walkthrough exceptions capture
- `[x]` Link walkthroughs to process, risk, and control

#### 2.6 Document Library and Evidence

- `[x]` Create document library data model
- `[x]` Create evidence upload UI
- `[x]` Add document metadata tagging
- `[x]` Add document linking to risks, controls, procedures, findings, and working papers
- `[x]` Add evidence request workflow model
- `[x]` Add client-facing evidence request submission flow
- `[x]` Add reviewer evidence checklist

### Deliverables

- planning and scoping module
- risk and control matrix
- procedure library
- working papers module
- walkthrough module
- document library

---

## Phase 3: Make Elsa the Audit Process Backbone

### Goal

Move Elsa from side infrastructure to the central orchestration layer for audit process flows.

### Progress

- Status: `[x] Complete`
- Completion: `100%`

### Tasks

#### 3.1 Workflow Integration Foundation

- `[x]` Audit current Elsa server and studio configuration for production readiness
- `[x]` Document workflow definition naming standards
- `[x]` Link domain entities to Elsa workflow instance IDs
- `[x]` Add workflow status mapping between Elsa and application UI
- `[x]` Add workflow launch service abstraction in the backend
- `[x]` Register deployed Elsa definitions and sync callbacks against the local auditing workflow API

#### 3.2 Workflow Families

- `[x]` Implement planning workflow
- `[x]` Implement scope approval workflow
- `[x]` Implement walkthrough workflow
- `[x]` Implement control testing workflow improvements
- `[x]` Implement working paper review workflow
- `[x]` Implement finding review and approval workflow
- `[x]` Implement management response workflow
- `[x]` Implement remediation follow-up workflow
- `[x]` Implement final report sign-off workflow

#### 3.3 Frontend Workflow Experience

- `[x]` Add workflow inbox to the frontend
- `[x]` Add pending tasks view
- `[x]` Add pending approvals view
- `[x]` Add overdue actions view
- `[x]` Add review-ready workpaper queue
- `[x]` Add workflow activity timeline on engagement detail screens
- `[x]` Add admin navigation or launchpoint to Elsa Studio

#### 3.4 Notifications and Task Routing

- `[x]` Create notification model and storage
- `[x]` Create task routing model
- `[x]` Add in-app notifications
- `[x]` Add due-date reminders
- `[x]` Add review-ready notifications
- `[x]` Add overdue finding reminders
- `[x]` Add escalation rules

### Deliverables

- Elsa-centered workflow orchestration
- workflow inbox
- notifications and task routing
- stronger audit lifecycle visibility

---

## Phase 4: Differentiate Internal Audit and External Audit

### Goal

Support both audit types without forcing a single process model onto both.

### Progress

- Status: `[x] Complete`
- Completion: `100%`

### Tasks

#### 4.1 Internal Audit Mode

- `[x]` Add internal audit engagement templates
- `[x]` Add annual audit plan workflow
- `[x]` Add control-focused scoping defaults
- `[x]` Add audit coverage reporting improvements
- `[x]` Add management action tracking

#### 4.2 External Audit Mode

- `[x]` Add external audit engagement templates
- `[x]` Add materiality setup module
- `[x]` Add FSLI scoping support
- `[x]` Add assertions support
- `[x]` Add substantive procedure packs
- `[x]` Add journal testing and management override procedure templates
- `[x]` Add recalculation and reperformance templates

#### 4.3 Shared Configuration Layer

- `[x]` Add engagement type configuration to drive forms and workflows
- `[x]` Add template selection by audit type
- `[x]` Add terminology mapping where internal and external audit use different wording
- `[x]` Add role-specific dashboards by engagement type

### Deliverables

- internal audit operating mode
- external audit operating mode
- configurable templates and forms

---

## Phase 5: Advanced Analytics, Data Integration, and Enterprise Readiness

### Goal

Expand the platform’s analytical and integration capability after the core audit execution model is stable.

### Progress

- Status: `[x] Completed`
- Completion: `100%`

### Tasks

#### 5.1 Audit Analytics

- `[x]` Add management override of controls analytics
- `[x]` Add general journal exception analytics
- `[x]` Add weekend and holiday posting analytics
- `[x]` Add unusual user posting concentration analytics
- `[x]` Add prior year vs current year TB movement analytics
- `[x]` Add materiality-threshold analytics
- `[x]` Add industry benchmark analytics where relevant
- `[x]` Add reasonability and forecast analysis support

#### 5.2 Data Integration

- `[x]` Define ERP integration architecture
- `[x]` Add import connectors roadmap for SAP, Oracle, Dynamics, Sage, Xero
- `[x]` Add high-volume data ingestion approach
- `[x]` Define staging tables for imported audit analytics data
- `[x]` Define client-environment deployment option for sensitive data
- `[x]` Add analytics import UI and CSV batch validation for staging datasets

#### 5.3 Power BI and Reporting Maturity

- `[x]` Prepare Power BI as optional Analytical Report mode
- `[x]` Configure environment-driven Power BI reporting settings
- `[x]` Add reporting data mart / views for Power BI
- `[x]` Reconcile Power BI metrics with native analytics
- `[x]` Add server-driven config for Power BI reporting

#### 5.4 Enterprise Readiness

- `[x]` Add audit trail review dashboard
- `[x]` Add stronger role-based permissions for client-side owners and reviewers
- `[x]` Add document retention and archival rules
- `[x]` Add environment-level feature flags for modules
- `[x]` Add implementation telemetry for workflow and module usage

### Deliverables

- richer audit analytics
- stronger integration strategy
- enterprise reporting maturity
- operational hardening

---

## Materiality Calculation Expansion

### Goal

Move external-audit materiality from manual planning capture to a financial-data-driven calculation workflow sourced from imported trial balance data.

### Progress

- Status: `[x] Completed`
- Completion: `100%`

### Tasks

- `[x]` Document the target materiality workflow and implementation approach in `Materiality_Calculation_Implementation_Plan.md`
- `[x]` Define schema amendments for materiality candidates, calculation history, active-selection metadata, misstatements, and scope links
- `[x]` Create initial materiality backend domain models and request contracts
- `[x]` Create materiality repository and API endpoints for workspace, candidate generation, calculation history, and active selection
- `[x]` Make analytics threshold queries prefer active materiality calculations before falling back to manual planning fields
- `[x]` Apply `AuditMateriality_Calculation_Schema.sql` to the live database
- `[x]` Add frontend planning workspace for benchmark selection and auto-calculation
- `[x]` Add materiality candidate regeneration from imported financials in the audit-file Planning tab
- `[x]` Add manual override flow with rationale and audit trail capture
- `[x]` Add PM-based population stratification against imported journals or trial balance in the Planning tab
- `[x]` Add read-only materiality application summary showing key items, sample pool, and scope candidates
- `[x]` Add SAD-style misstatement summary against clearly trivial, performance materiality, and overall materiality
- `[x]` Add persisted scope/FSLI decision capture backed by `audit_materiality_scope_links`
- `[x]` Add persisted misstatement capture backed by `audit_misstatements`
- `[x]` Add fuller misstatement evaluation workspace against clearly trivial, performance materiality, and overall materiality
- `[x]` Update analytics widgets and findings views to show the active benchmark and threshold source

### Deliverables

- materiality workspace API
- benchmark candidate generation from imported financials
- calculation history and active materiality selection
- PM-based stratification and scope-candidate guidance
- persisted scope-link decisions in the audit file
- persisted misstatement capture with SAD summary refresh
- fuller misstatement evaluation workspace with escalation into findings
- active benchmark / threshold source surfaced in analytics and findings views

---

## Database Workstream

### Goal

Track the schema work required to support the roadmap.

### Progress

- Status: `[x] Completed`
- Completion: `100%`

### Tasks

- `[x]` Review current audit schema against roadmap modules
- `[x]` Design `audit_engagement_plans`
- `[x]` Design annual planning fields within the engagement plan schema
- `[x]` Design `audit_scope_items`
- `[x]` Design `audit_procedure_library`
- `[x]` Design `audit_procedure_steps`
- `[x]` Design `audit_procedure_assignments`
- `[x]` Design `audit_working_papers`
- `[x]` Design `audit_working_paper_sections`
- `[x]` Design `audit_working_paper_reviews`
- `[x]` Design `audit_documents`
- `[x]` Design `audit_document_links`
- `[x]` Design `audit_evidence_requests`
- `[x]` Design `audit_walkthroughs`
- `[x]` Design `audit_walkthrough_exceptions`
- `[x]` Design `audit_control_tests`
- `[x]` Design `audit_control_test_results`
- `[x]` Design `audit_reviews`
- `[x]` Design `audit_review_notes`
- `[x]` Design `audit_signoffs`
- `[x]` Design `audit_notifications`
- `[x]` Design `audit_tasks`
- `[x]` Design `audit_trail_events`
- `[x]` Design `audit_entity_changes`
- `[x]` Design `audit_document_access_logs`
- `[x]` Design `audit_login_events`
- `[x]` Design lookup tables for control classification, engagement type, observation rating, and working paper status
- `[x]` Write migration scripts
- `[x]` Write seed scripts for lookup data
- `[x]` Map each new table to API and frontend needs

---

## Audit Trail Workstream

### Goal

Make audit trail a first-class platform capability instead of relying only on `created_at` and `updated_at`.

### Progress

- Status: `[x] Completed`
- Completion: `100%`

### Tasks

- `[x]` Define audit trail policy for business events
- `[x]` Define audit trail policy for field-level changes
- `[x]` Define audit trail policy for document access
- `[x]` Define audit trail policy for workflow transitions
- `[x]` Define which entities require immutable history
- `[x]` Design backend service for audit trail writes
- `[x]` Define correlation strategy between domain events and Elsa workflow instances
- `[x]` Add audit trail viewer requirements for frontend
- `[x]` Add export/report requirements for audit trail review
- `[x]` Add retention and archival rules for audit trail records

---

## UI/UX Workstream

### Goal

Track user-facing changes across modules.

### Progress

- Status: `[x] Completed`
- Completion: `100%`

### Tasks

- `[x]` Redesign navigation to match audit lifecycle
- `[x]` Add planning workspace screens
- `[x]` Add scoping workspace screens
- `[x]` Add procedure library screens
- `[x]` Add working paper screens
- `[x]` Add evidence request screens
- `[x]` Add review and sign-off screens
- `[x]` Add workflow inbox screens
- `[x]` Add notifications center
- `[x]` Add client owner access flows
- `[x]` Review all audit terminology for consistency

---

## Suggested Implementation Order

1. Phase 1
2. Database workstream for Phase 2 modules
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5

---

## Current Summary

- Completed:
  - Power BI optional mode entry point prepared in Analytical Report view
  - audit trail explicitly added to roadmap and task tracker
  - findings and recommendations tab now loads live API-backed data
  - findings now support create, edit, and delete in assessment details
  - recommendations now support create and delete in assessment details
  - management response update dialog wired into recommendation actions
  - collaboration comments persist in client storage per assessment
  - activity feed persists in client storage per assessment
  - assessment workflow status is derived from workflow/domain state
  - assessment export/report generation is functional
  - findings drill-down now navigates into the assessment details findings tab
  - Phase 1 closeout validation documented in `Phase1_Closeout_Validation.md`
  - first procedure library slice implemented across SQL, backend API, and frontend assessment details
  - reusable procedure templates can now be cloned into an assessment
  - assessment details now includes a Procedures tab with create, edit, and delete actions
  - first working papers slice implemented across SQL, backend API, and frontend assessment details
  - working papers now support template cloning, sign-off capture, and cross-reference linking
  - assessment details now includes a Working Papers tab with create, edit, and delete actions
  - first document library slice implemented across SQL, backend API, and frontend assessment details
  - audit documents now support upload, categorization, linking, download, and deletion
  - evidence requests now persist requested items and auto-update fulfillment state when linked evidence is uploaded
  - assessment details now includes a Documents tab with upload and evidence-request actions
  - planning and scoping are now implemented across SQL, backend API, and frontend assessment details
  - planning workspace now supports engagement type, annual plan fields, scope-letter linkage, and sign-off state
  - scope items now support business unit, process, subprocess, FSLI, owner, and linked procedure capture
  - risk and control matrix is now implemented with adequacy, effectiveness, classification, type, frequency, and owner fields
  - walkthroughs now support participants, narrative, evidence summary, control design conclusion, and linked exceptions
  - walkthrough exceptions can now be linked to findings from the assessment details screen
  - evidence requests now support submission of requested evidence directly from each request item
  - uploaded evidence request items now support reviewer accept or reject decisions with notes
  - procedure dialogs now assign working paper references from live working paper options
  - analytical dashboard drill-down routing now targets the shifted planning, risk/control, controls, and findings tabs correctly
  - Phase 3 workflow foundation now persists local workflow instances, tasks, and notifications in dedicated workflow tables
  - `StartControlTesting` now launches through a shared workflow service instead of a raw controller-level Elsa dispatch call
  - a new workflow inbox view now surfaces active workflows, pending tasks, and notifications in the frontend
  - workflow inbox actions now support opening linked assessments, completing tasks, and marking notifications as read
  - assessment details now pull workflow instances by reference and use backend workflow records when deriving workflow status
  - assessment timeline control-testing status now reflects backend workflow instances before falling back to local client storage
  - workflow inbox now includes approval, overdue, and review-ready workpaper queues derived from persisted workflow tasks
  - workflow inbox now includes a configurable Elsa Studio launchpoint for workflow administration
  - control-testing workflow tasks now receive a due date so overdue workflow queues can operate
  - Phase 3 operational readiness and workflow naming standards are now documented in `Phase3_Elsa_Operational_Readiness.md`
  - planning approval, scope approval, walkthrough review, working paper review, finding review, management response, remediation follow-up, and final sign-off workflow launch paths are now exposed through the auditing API
  - assessment details now includes launch actions for planning approval, scope approval, walkthrough review, working paper review, findings review, management response, remediation follow-up, and final sign-off workflows
  - workflow events are now persisted and exposed as a workflow activity timeline on engagement detail screens
  - Elsa status sync, manual reminder sweep, and a background reminder service are now implemented in the auditing API
  - workflow inbox now exposes a `Run Reminders` action to generate due-soon, review-ready, overdue, and escalation notifications on demand
  - the Elsa workflow server now registers the full audit workflow family directly in code for planning approval, scope approval, control testing, walkthrough review, working paper review, finding review, management response, remediation follow-up, and final report sign-off
  - the Elsa workflow server now exposes a completion callback route at `/elsa/api/audit-callbacks/{workflowInstanceId}/complete` for each running workflow instance
  - completing a workflow task in the auditing API now calls the Elsa completion callback so Elsa can resume the suspended workflow and push a terminal sync back into the audit application
  - shell navigation is now grouped by audit lifecycle with portfolio, planning, execution, reporting, and administration sections
  - the frontend now includes a dedicated notifications center for workflow alerts, escalations, and client-owner action items
  - the frontend now includes a dedicated review-and-sign-off workspace for approval, review, and final sign-off queues
  - workflow inbox now cross-links directly into notifications and review/sign-off workspaces
  - audit terminology in the shell has been aligned around Audit Dashboard, Audit Files, Analytical Suite, and Audit Core
  - database workstream closeout schema added in `Affine.Engine/SQL/AuditDatabaseWorkstream_Closeout.sql`
  - generic audit task, review, sign-off, control-test, procedure-step, and access-log tables now exist in the `Risk_Assess_Framework` schema
  - template-level procedure steps and working paper sections were seeded into the live database for reusable audit templates
  - the auditing API and workflow server local URLs are now aligned to `https://localhost:5001` for Elsa runtime dispatch
  - Phase 4 engagement-mode support now differentiates internal and external audits through a shared engagement profile layer in the assessment details view
  - planning now supports structured external-audit materiality fields for basis, overall materiality, performance materiality, and clearly trivial thresholds
  - scope items now support assertion mapping and scoping rationale capture for external-audit engagements
  - procedure and working paper template libraries now support engagement-type applicability and audit-type-based template filtering
  - new internal-audit and external-audit template packs are scripted in `AuditModesPhase4_Schema.sql`
  - internal-audit management action tracking is now implemented end to end across SQL, backend API, frontend client, and a dedicated assessment tab
  - findings and recommendations screens now use audit-type-aware terminology and expose management-action creation for internal-audit follow-up
  - overview and planning screens now show engagement-type-aware dashboard metrics and guidance panels
  - internal-audit planning now includes an annual audit plan approval workflow launch path backed by the auditing API and Elsa workflow server
  - internal-audit overview and planning screens now surface annual coverage summary metrics and priority coverage gaps using the audit coverage map API
- Phase 5 audit analytics now includes journal-exception, management-override, user-posting-concentration, and trial-balance-movement APIs plus Analytical Dashboard widgets
- Phase 5 analytics staging tables are now scripted in `AuditAnalyticsPhase5_Schema.sql` for journal entries, holiday calendars, trial balance snapshots, and import batches
- Phase 5 analytics now also includes industry-benchmark and reasonability/forecast APIs plus new Analytical Dashboard widgets for benchmark variance and expected-versus-actual analysis
- Phase 5 ERP integration architecture is now documented for SAP, Oracle, Dynamics, Sage, and Xero, including staging-first ingestion, high-volume loading, and client-environment deployment options
- Phase 5 audit trail now has append-only schema, backend write/read service, workflow-linked persistence, an assessment-level review tab, and a formal policy document covering retention, correlation, and export requirements
- Phase 5 reporting maturity now includes Power BI-facing reporting data mart views for findings, execution, and analytics summaries
- Analytical Report mode now surfaces Power BI reconciliation in both Microsoft Power BI mode and an optional dashboard widget so users can compare native versus reporting counts before relying on Power BI
- Analytical Suite now includes a CSV analytics import workflow with dataset-type validation, preview, recent batch history, and API-backed staging imports for journal, trial balance, benchmark, and forecast datasets
- High-risk import and workflow actions now have both client-side gating and API-layer role enforcement using shared user-context headers for analytics import, workflow starts, workflow task completion, scoped inbox access, and reminder administration
- Phase 5 enterprise closeout now includes server-driven Power BI configuration delivery, archive and retention policy tables, assessment archive actions, API-driven feature flags, and usage telemetry for module opens, analytics imports, workflow actions, reminder sweeps, and archive events
- Post-implementation service-level smoke testing now passes for procedures, working papers, evidence requests, document upload, audit trail, analytics import, workflow inbox launch, archive actions, and Power BI reconciliation endpoints
- Materiality calculation expansion is now in progress with a dedicated schema file, repository/API surface, analytics-threshold fallback to active calculated materiality, persisted scope-link capture, and persisted misstatement capture
- Post-demo document confidentiality foundation is now implemented with a dedicated schema file, live database lookup and grant tables, API-side access enforcement, redaction of restricted evidence links, and frontend upload metadata for restricted evidence handling
- Post-demo collaborator access control is now implemented with seeded audit-team role definitions, live project and audit-file collaborator tables, protected API endpoints, project-team management UI, and audit-file access inheritance from project assignments
- Post-demo risk assessment hardening is now implemented with live database description columns, seeded audit-file lifecycle statuses for draft, in review, approved, and archived states, API-side edit locking for approved or archived audit files, and frontend read-only handling that saves row updates before applying the final header status lock
- Post-demo evidence workflow hardening now scopes client contributors to assigned evidence requests, blocks unassigned client uploads at the API, adds document security update APIs and UI for permission changes, and surfaces document access activity for confidential-content review
- Post-demo restricted evidence approval workflow is now implemented with seeded sensitive document categories, category-level confidentiality defaults, persisted pending or approved or rejected security review state, API-side approval enforcement, and frontend upload and approve or reject flows for restricted evidence
- Post-demo project-to-audit-file linkage is now surfaced in the live frontend with persisted department and project assignment on the audit-file form, project-level drill-down into linked audit files, and routed navigation from audit projects into the filtered audit-file workspace
- Post-demo materiality governance is now implemented with a live benchmark-profile table, explicit validation-status notes on defaults, entity and industry context capture, benchmark-selection rationale capture, and persisted approval history for calculated and manual materiality activation; final auditor confirmation of the default percentage set still remains open
- Post-demo finance reporting closure is now implemented with a dedicated finance workspace inside the audit-file view, persisted trial-balance mappings, reusable mapping profiles, draft financial statement generation, support-queue generation from imported general-ledger data, link-back to procedures or walkthroughs or controls or findings, persisted finalization capture, finance rule-package separation, and shell-navigation cleanup for duplicate heatmap and departments modules

- Deployment note:
  - the real `PowerBI:ReportUrl` value still needs to be populated per environment in API configuration; the configuration path is now implemented in code

- Next recommended build targets:
  1. replace trusted user-context headers with claims-based authentication and authorization on the auditing API
  2. add richer approval outcomes such as rejection, rework, and escalation branches inside Elsa workflow definitions
  3. add scheduled retention execution and archival administration screens on top of the new retention-policy schema
  4. populate the real Power BI environment values and add embed support if browser launch is no longer sufficient

---

## Post-Demo Audit Core Backlog (2026-03-10 Meeting Follow-Up)

### Goal

Turn the March 10, 2026 Audit Core demo feedback into a focused implementation backlog for the finance-audit gaps that still remain after the earlier phase work.

### Progress

- Status: `[~] In progress`
- Completion: `96%`

### Tasks

- `[x]` Add project-level collaborator access rules for managers, seniors, juniors, reviewers, clients, and restricted contributors
- `[x]` Add audit-file and document-level confidentiality controls for sensitive evidence such as payroll and HR records
- `[x]` Add restricted evidence categories and access approval rules for confidential uploads
- `[x]` Add client-side evidence submission lanes that expose only assigned requests and allowed documents
- `[x]` Extend the audit trail to capture access reads, permission grants, and permission changes on confidential content
- `[x]` Add the missing risk assessment description columns raised during the demo review
- `[x]` Harden risk assessment approval states so editable table data and approval workflow remain consistent
- `[x]` Refine project-to-audit-file linkage so one audit project can contain multiple audit files with clean workflow routing
- `[ ]` Validate materiality benchmark percentages for profit before tax, revenue, and total assets against auditor-reviewed defaults, then promote only those approved profiles to validated defaults
- `[x]` Add entity-type or industry rationale capture for selected materiality benchmark and percentage
- `[x]` Add approval history for materiality overrides, clearly trivial thresholds, and performance materiality changes
- `[x]` Add a trial balance mapping workspace that classifies accounts into income statement and balance sheet structures
- `[x]` Persist reusable mapping profiles for recurring clients or engagement types where appropriate
- `[x]` Generate draft or dummy financial statements from mapped trial balance data
- `[x]` Add a finance-audit finalization workspace after findings, evidence, and review stages
- `[x]` Add general ledger extract ingestion for substantive transaction review
- `[x]` Add transaction triage rules that identify items requiring support based on materiality, journal-risk, and revenue-risk logic
- `[x]` Create support-request queues for selected transactions and track received, cleared, escalated, and unresolved states
- `[x]` Link revenue and journal-risk selections back to procedures, walkthroughs, controls, and findings
- `[x]` Add recommendation, conclusion, and release-readiness capture in the finalization stage
- `[x]` Fold duplicate standalone heatmap navigation into the Analytical Suite where the same capability already exists
- `[x]` Remove or merge duplicate departments administration where Audit Universe already covers the hierarchy need
- `[x]` Package finance-audit defaults separately from future IT-audit or domain-specific extensions

### Deliverables

- secure collaboration and confidentiality controls for audit evidence
- finance-audit-calibrated materiality workflow
- trial-balance-to-financial-statement mapping flow
- general-ledger-based substantive testing queues
- explicit finalization-stage workflow and draft financial statement output
- cleaner Audit Core navigation with fewer duplicate modules

### Implementation Rule

- Any backlog item that introduces new persistence requirements must ship with the corresponding SQL schema or migration changes, repository/API updates, and any required seed or reference data.
- Database changes will be implemented with the specific feature work rather than as one large speculative migration, unless a shared foundation table is clearly needed first.

### Source

- Attached transcript: `c:\Users\keletso\Pictures\New folder\land\Audit Meeting Notes\Affine Products Demo QnA  - 2026_03_10 10_58 SAST - Notes by Gemini.md`
- Scope limited to Audit Core discussion only
