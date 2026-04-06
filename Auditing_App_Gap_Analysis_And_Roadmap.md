# Auditing App Gap Analysis, Elsa Workflow Alignment, and Amendment Roadmap

## Purpose

This document explains how to evolve the current platform into a more complete, holistic auditing application based on:

- the current repository state
- the attached meeting notes
- the existing Elsa workflow projects already in the repo
- the user notes captured during the internal audit discussion

It focuses on:

- missing features
- features that exist but need to be completed or corrected
- workflow opportunities using Elsa
- database additions and schema amendments likely required
- how to distinguish internal audit from external audit requirements

## Important Scope Note

I could not inspect a live database through MCP because no database MCP server is available in this session.

This analysis is therefore based on:

- repository code
- SQL schema files
- API controllers
- frontend views
- Elsa workflow server/studio projects
- the meeting notes you attached

That is still enough to define the implementation roadmap and likely database amendments with good confidence.

---

## Executive Assessment

The product is no longer just a prototype with isolated ideas. It already has meaningful foundations:

- risk assessment
- analytics
- heatmap
- audit universe
- findings and recommendations backend
- an Elsa workflow server and Elsa Studio

The main gap is that the platform still leans more toward risk management and risk visualization than full audit execution.

The largest missing capabilities are:

- formal planning and scoping
- working papers
- procedure library and execution tracking
- walkthroughs and control testing evidence
- document library with proper referencing
- review and sign-off workflow
- notifications and task routing
- better distinction between internal audit and external audit
- richer control model fields
- live workflow usage from the frontend, not just backend wiring

The repo already proves that Elsa can be part of the system. The work now is to convert Elsa from a technical add-on into the operating backbone for audit lifecycle workflows.

---

## What Already Exists

## Backend

- Risk assessment CRUD and reference-based assessments
- Control testing workflow dispatch endpoint in `Affina.Auditing.API`
- audit universe repository and controller support
- findings, recommendations, coverage, and trend APIs
- analytical reporting APIs

## Frontend

- dashboard
- assessments views
- analytical report
- heatmap
- audit universe view
- exports
- partial workflow status UI

## Workflow Foundation

- `Affine.Auditing.Workflows.Server`
- `Affine.Auditing.Workflows.Studio`
- Elsa v3 packages already installed
- workflow persistence configured in PostgreSQL

## Data Foundation

The repo already contains schema support for:

- `audit_universe`
- `audit_findings`
- `audit_recommendations`
- `audit_coverage`
- `risk_trend_history`

This is a strong start, but it is still missing core execution structures such as working papers, procedures, walkthroughs, evidence requests, review notes, and audit program design.

---

## Key Findings from the Meeting Notes

The notes point to a consistent message from different auditors:

1. The current system is good on risk and analytics, but weak on true audit execution.
2. Internal audit and external audit need overlapping but different flows.
3. Auditors need scoping, evidence, review, and working-paper discipline more than just dashboards.
4. Notifications and workflow routing are essential.
5. Control testing needs stronger structure.
6. Risk descriptions, control descriptions, and control classification are missing or incomplete.
7. Audit universe must connect to risks, controls, and audit plans.
8. Procedures need to become first-class objects in the system.
9. Analytical reporting must eventually align with actual audit procedures, not only business-risk graphs.
10. Elsa front-end workflow creation/design should become part of the product operating model.

---

## What "Procedures" Means in Auditing

Karabo’s mention of procedures is important.

In auditing, "procedures" are the specific steps or tests an auditor performs to obtain evidence.

Examples:

- inspect a signed approval
- reperform a depreciation calculation
- trace revenue from invoice to cash receipt
- compare the general ledger to the trial balance
- review weekend journals for management override
- inspect supporting quotations for procurement
- perform a walkthrough of recruitment or payroll termination

In practice, a procedure library is a reusable catalog of standard audit steps that can be selected and attached to:

- a project
- a scope item
- a business process
- a risk
- a control
- a working paper

For this product, `procedures` should become a core module, not just a note field.

---

## Gap Analysis by Functional Area

## 1. Planning and Scoping

### What exists

- departments
- projects
- audit universe
- basic assessment context

### Missing

- annual audit plan
- engagement planning workspace
- scope definition by business process / subprocess / FSLI
- scope letter / engagement letter attachment
- planning sign-off
- materiality setup for external audit
- risk-based audit cycle planning
- scoping by control focus, subprocess, and risk register references

### Why it matters

The notes show auditors begin with planning and scope discipline. Without that, the system remains assessment-centric instead of audit-centric.

---

## 2. Risk and Control Matrix

### What exists

- risk assessments
- controls data in assessment forms
- heatmap and analytics

### Missing or incomplete

- dedicated risk and control matrix module
- explicit risk description and control description fields in all relevant views
- control adequacy vs control effectiveness split
- control classification:
  - preventive
  - detective
  - corrective
- control owner
- control frequency
- control type:
  - manual
  - automated
  - IT dependent
- linkage from audit universe to risks and controls

### Why it matters

This came up directly in the January 30 notes. It is a core internal-audit requirement and also helps external audit planning.

---

## 3. Working Papers

### What exists

- some export capability
- some document attachment concepts in the notes
- findings/recommendations data foundation

### Missing

- working paper entity
- working paper sections and indexing
- reviewer notes on working papers
- preparer / reviewer / approver chain
- sign-off history
- cross-reference linking
- working paper templates
- conclusion field
- status progression:
  - not started
  - in progress
  - prepared
  - reviewed
  - cleared
  - signed off

### Why it matters

This is one of the biggest gaps. A serious auditing app cannot rely on generic notes and attachments only.

---

## 4. Procedure Library and Test Execution

### What exists

- only partial workflow initiation for control testing
- no visible reusable procedure library in the current app

### Missing

- reusable procedure library
- procedure categories:
  - planning
  - walkthrough
  - control testing
  - substantive analytics
  - substantive detail testing
  - reporting
- procedure steps
- expected evidence
- pass/fail/not applicable outcome model
- exceptions captured per procedure step
- linkage to findings generation

### Why it matters

This is the cleanest way to operationalize Karabo’s guidance and make the app truly audit-oriented.

---

## 5. Walkthroughs

### What exists

- conceptually implied in notes
- no formal walkthrough feature identified in the current code review

### Missing

- walkthrough records
- process narrative
- walkthrough participants
- walkthrough date and evidence
- walkthrough exceptions
- walkthrough conclusion
- linkage to business process, risk, and control

### Why it matters

Walkthroughs are standard in both internal and external audit contexts. They also fit naturally into workflow and working papers.

---

## 6. Document Library and Evidence Management

### What exists

- export features
- attachment need acknowledged in notes

### Missing

- central document library
- evidence request tracking
- client document portal
- document metadata:
  - source
  - uploaded by
  - date
  - linked risk/control/procedure
  - confidentiality class
- document referencing from working papers
- version control
- reviewer evidence checklist

### Why it matters

The notes were explicit that the document library must include all referenced support and enable reviewers to verify what was inspected.

---

## 7. Findings, Observations, and Ratings

### What exists

- findings and recommendations backend
- findings aging widget
- recommendation entities

### Missing or incomplete

- dedicated frontend findings management workflow
- observation ratings taxonomy
- criteria / condition / cause / consequence / recommendation structure
- management response workflow
- remediation tracking from issue to closure
- verification workflow
- review note to finding conversion

### Why it matters

The backend is ahead of the frontend here. This is a good place to move quickly because the data model foundation already exists.

---

## 8. Review and Quality Assurance

### What exists

- partial workflow status indicators
- no complete review workflow in the frontend

### Missing

- review points
- review notes
- reviewer clearance
- completeness checks
- missing-signature checks
- missing-document checks
- stage-based quality gates
- final sign-off matrix

### Why it matters

Your own notes captured this clearly: reviewers need to verify completeness, signatures, documents, and readiness before reporting.

---

## 9. Notifications and Tasking

### What exists

- design intent in docs
- some placeholder settings for notifications
- no complete notification engine in reviewed code

### Missing

- in-app notifications
- due-date reminders
- review-ready notifications
- evidence request reminders
- overdue finding reminders
- task ownership
- escalation rules

### Why it matters

This was raised explicitly in the January 30 discussion as a major gap in existing tools and an opportunity for this platform.

---

## 10. Audit Trail and Change History

### What exists

- `created_at` and `updated_at` fields on a number of tables
- workflow infrastructure that can later contribute state transitions

### Missing

- append-only audit trail event storage
- entity-level field change history
- document access history
- workflow transition logging at business level
- sign-off and review action trail
- audit trail reporting UI

### Why it matters

For an auditing application, `created_at` and `updated_at` are not enough.

The system needs to record:

- who changed what
- when they changed it
- what the old value was
- what the new value is
- which workflow or action triggered the change

Recommended audit trail categories:

- business audit trail
- system change trail
- document access trail
- workflow transition trail

---

## 11. Analytical Report Alignment

### What exists

- native analytical dashboard
- Power BI mode preparation
- findings and coverage analytics
- drill-down support

### Missing

- analytics aligned to actual audit procedures
- materiality-driven analytics
- FSLI-driven analytics
- management override analytics
- trial balance vs general ledger checks
- year-on-year movement analysis
- exception analytics for journals, approvals, weekends, holidays
- reasonability and forecast analytics

### Why it matters

The current analytical suite is useful, but the notes repeatedly show that audit buyers will expect analytics tied to procedure objectives and assertions.

---

## 12. Internal Audit vs External Audit Mode

### What exists

- one general system model

### Missing

- configurable engagement type
- mode-specific forms and workflows
- different terminology and defaults for internal vs external audit

### Why it matters

The notes make it clear:

- internal audit is more control, process, scoping, coverage, and findings driven
- external audit is more FSLI, assertions, materiality, and substantive procedure driven

One product can support both, but it should do so through configuration rather than pretending both workflows are identical.

---

## Elsa Workflow Analysis

## Current Elsa Position

The repo already has:

- Elsa server
- Elsa Studio
- PostgreSQL persistence for workflows
- API dispatch integration for control testing

This means the platform already has the technical base to create workflows.

## Current Limitation

Elsa is not yet the central orchestration model for the auditing lifecycle.

Right now it appears closer to:

- workflow infrastructure
- one-off control testing trigger
- separate studio environment for workflow design

It should evolve into:

- workflow orchestration for planning
- evidence request routing
- review routing
- sign-off routing
- finding remediation lifecycle
- client response workflow

## Recommended Elsa Workflow Families

1. Planning Workflow
2. Scope Approval Workflow
3. Walkthrough Workflow
4. Control Testing Workflow
5. Working Paper Review Workflow
6. Findings Review and Sign-off Workflow
7. Management Response Workflow
8. Remediation Follow-up Workflow
9. Final Report Sign-off Workflow

## Recommended Elsa Design Principle

Use Elsa for process state and orchestration, not as a substitute for core audit data tables.

That means:

- audit entities live in the audit application database
- Elsa stores process state, transitions, timers, approvals, assignments, and triggers
- the application UI remains the source of truth for audit content and evidence

This is the right separation of concerns.

---

## Database Amendment Analysis

## What the Repository Already Covers

The SQL reviewed already includes good support for:

- audit universe
- findings
- recommendations
- coverage
- trend snapshots

## What Still Needs New Tables

The following appear to be missing from the reviewed schema and should likely be added.

### 1. Audit Engagement / Audit Plan

Suggested tables:

- `audit_engagements`
- `audit_plan_cycles`
- `audit_scope_items`

Purpose:

- define audit type
- define period
- define entity or business unit
- define scoped processes / subprocesses / FSLIs
- track engagement status

### 2. Procedure Library

Suggested tables:

- `audit_procedure_library`
- `audit_procedure_steps`
- `audit_procedure_assignments`

Purpose:

- reusable procedures
- reusable step templates
- assignment of procedures to engagements, scope items, controls, or working papers

### 3. Working Papers

Suggested tables:

- `audit_working_papers`
- `audit_working_paper_sections`
- `audit_working_paper_references`
- `audit_working_paper_reviews`

Purpose:

- preparation and review of audit evidence files
- structured indexing and sign-off

### 4. Evidence and Document Management

Suggested tables:

- `audit_documents`
- `audit_document_links`
- `audit_evidence_requests`
- `audit_evidence_request_items`

Purpose:

- upload, classify, link, and review evidence
- route evidence requests to client-side owners

### 5. Walkthroughs

Suggested tables:

- `audit_walkthroughs`
- `audit_walkthrough_steps`
- `audit_walkthrough_exceptions`

Purpose:

- capture process walkthroughs and exceptions

### 6. Control Testing Expansion

Suggested tables:

- `audit_control_tests`
- `audit_control_test_steps`
- `audit_control_test_results`
- `audit_control_exceptions`

Purpose:

- formalize testing results instead of only starting workflow instances

### 7. Reviews and Sign-offs

Suggested tables:

- `audit_reviews`
- `audit_review_notes`
- `audit_signoffs`

Purpose:

- reviewer comments
- clearance cycle
- final approvals

### 8. Notifications

Suggested tables:

- `audit_notifications`
- `audit_notification_preferences`
- `audit_tasks`

Purpose:

- route actions and reminders through the platform

### 9. Audit Trail

Suggested tables:

- `audit_trail_events`
- `audit_entity_changes`
- `audit_document_access_logs`
- `audit_login_events`

Purpose:

- immutable history of important business and system actions
- field-level change logging for sensitive entities
- evidence access traceability
- stronger compliance and defensibility

### 9. Rating Models and Control Attributes

Suggested lookup tables:

- `ra_control_classification`
- `ra_control_type`
- `ra_observation_rating`
- `ra_engagement_type`
- `ra_working_paper_status`
- `ra_review_note_status`

Purpose:

- normalize the extra classification auditors expect

---

## Immediate Data Model Corrections to Existing Structures

These should be reviewed even before adding new modules.

### Risk and Control Data

Ensure the underlying model supports:

- risk description
- control description
- control objective
- control owner
- control frequency
- control classification
- adequacy rating
- effectiveness rating

### Audit Universe Linkage

Ensure audit universe can link to:

- risks
- controls
- projects
- findings
- audit plans

### Findings Model

Extend findings if needed to support:

- observation rating
- criteria
- condition
- cause
- consequence
- recommendation
- management action plan
- agreed action date
- verified closure

### Audit Trail Coverage

Ensure audit trail design covers:

- risk assessments
- controls
- audit universe
- scope changes
- procedures
- working papers
- findings and recommendations
- management responses
- document uploads and downloads
- review notes
- sign-offs
- workflow state transitions

---

## Feature Completion Gaps in Current Frontend

From the code review, several audit features are visibly stubbed or incomplete.

Examples:

- add finding action is still placeholder logic
- comment flow is still placeholder logic
- management response request is still placeholder logic
- report generation is still placeholder logic
- notifications appear planned but not fully implemented
- workflow status is mostly illustrative in some assessment views

This matters because some capabilities are already "announced" in the UI but not yet operational.

Those should be treated as completion work, not net-new invention.

---

## Recommended Product Structure

To make the platform holistic, the app should be organized around the audit lifecycle, not only around risk records.

Recommended major modules:

1. Dashboard
2. Audit Universe
3. Annual Plan / Engagement Planning
4. Scoping
5. Risk and Control Matrix
6. Procedure Library
7. Working Papers
8. Control Testing
9. Findings and Recommendations
10. Review and Sign-off
11. Reporting
12. Analytics
13. Workflow Designer / Workflow Admin
14. Client Portal / Document Requests

This structure is closer to how auditors think and work.

---

## Internal Audit and External Audit Planning

## Internal Audit Priority Features

- annual audit plan
- audit universe coverage
- process and subprocess scoping
- control testing
- walkthroughs
- findings and remediation
- management action tracking
- review notes and quality gates

## External Audit Priority Features

- FSLI scoping
- assertions
- materiality
- procedure library by assertion
- substantive testing
- journal testing / management override
- recalculation and reperformance procedures
- working papers and sign-off discipline

## Product Strategy Recommendation

Do not try to fully solve both immediately.

Recommended order:

1. strengthen internal audit flow first
2. add external-audit-specific planning, materiality, assertions, and FSLI procedures next

Reason:

- the current repo is already closer to internal audit and enterprise risk
- the January 30 notes map more naturally to internal audit execution
- external audit adds more specialized methodology and accounting depth

---

## Recommended Phased Delivery Plan

## Phase 1: Stabilize and Complete What Already Exists

- complete findings frontend
- complete recommendation and management response UI
- complete control testing UI
- wire notifications
- improve workflow status visibility
- link audit universe to risks and controls consistently

## Phase 2: Add Core Audit Execution Modules

- procedure library
- working papers
- document library
- walkthroughs
- review notes
- sign-off

## Phase 3: Make Elsa the Audit Process Backbone

- create planning workflow
- create review workflow
- create sign-off workflow
- create management response workflow
- surface workflow tasks in the frontend
- add workflow admin view or launchpad into Elsa Studio

## Phase 4: Differentiate Internal vs External Audit

- engagement type selector
- internal-audit templates
- external-audit templates
- materiality and assertion support
- FSLI-based planning and procedure packs

## Phase 5: Advanced Analytics and Data Integration

- management override analytics
- journal exception analytics
- ERP connectors
- trial balance and ledger reconciliation analytics
- richer Power BI integration

---

## Practical Elsa Implementation Plan

## Short-Term

- keep Elsa Studio as the designer/admin surface
- expose clear workflow launch points inside the app
- store workflow instance IDs against domain entities

Example links:

- engagement -> planning workflow instance
- control test -> control testing workflow instance
- working paper -> review workflow instance
- finding -> remediation workflow instance

## Medium-Term

- create a workflow inbox inside the frontend
- show:
  - assigned tasks
  - pending approvals
  - overdue actions
  - review-ready workpapers

## Long-Term

- provide template workflow packs:
  - internal audit basic pack
  - external audit planning pack
  - findings remediation pack

This lets Elsa become a configurable capability instead of a hidden technical subsystem.

---

## High-Priority Backlog

These are the highest-value changes to do next.

1. Complete notifications and task routing.
2. Add dedicated findings and recommendations UI using the existing backend.
3. Add a proper risk and control matrix with richer control fields.
4. Add procedure library.
5. Add working papers.
6. Add document library and evidence request workflow.
7. Add walkthrough module.
8. Add review notes and sign-off workflow.
9. Add internal-audit planning and scoping workspace.
10. Link frontend actions directly to Elsa workflow instances and task states.

---

## Recommended Output Document Strategy

This analysis should lead to a set of follow-up implementation documents:

1. `Internal_Audit_Workflow_Implementation_Plan.md`
2. `Procedure_Library_Design.md`
3. `Working_Papers_Module_Design.md`
4. `Document_Library_And_Evidence_Flow.md`
5. `Elsa_Workflow_Integration_Plan.md`
6. `Database_Migration_Plan_For_Audit_Execution.md`

That will let the work be delivered in controlled chunks instead of one giant rewrite.

---

## Conclusion

The platform is not starting from zero. It already has meaningful audit-oriented foundations and a real Elsa workflow base.

The main problem is not the absence of technology. The main problem is that the product still needs to be reorganized around real audit execution:

- planning
- scoping
- procedures
- working papers
- evidence
- review
- sign-off
- findings follow-up

The repo already proves:

- Elsa can be used here
- workflow persistence already exists
- findings and recommendations already have a backend base
- audit universe already exists
- analytics already exist

The next stage should therefore be a structured expansion of the audit operating model, not a rebuild.

If done in the phased way above, the system can evolve from a risk-and-analytics-heavy prototype into a genuinely holistic auditing application.

---

## Audit Core Demo Follow-Up Backlog (2026-03-10)

This section is based on the attached transcript file:

- `c:\Users\keletso\Pictures\New folder\land\Audit Meeting Notes\Affine Products Demo QnA  - 2026_03_10 10_58 SAST - Notes by Gemini.md`

Scope is limited to the Audit Core discussion only. The separate business-networking product discussion is intentionally excluded.

## What The Demo Confirmed Already Exists Directionally

The meeting largely confirmed that these product areas are already in the right direction:

- dashboard, notifications, and workflow inbox
- audit universe hierarchy for franchise, department, and entity reporting
- planning, controls, procedures, and walkthrough-oriented structure
- findings, evidence capture, and review/sign-off intent
- analytical reporting with optional Microsoft Power BI integration
- materiality as an explicit finance-audit concept in the product

That means the next stage is not broad discovery anymore. It is transcript-driven gap closure around security, finance-audit finalization, and product consolidation.

## Missing Or Incomplete Items Raised In The Demo

### 1. Confidential Access Model For Audit Files And Evidence

The clearest missing requirement from the meeting is granular confidentiality handling. The example given was payroll evidence that should only be visible to a restricted subset of users even when other people are part of the same broader audit engagement. That implementation slice is now materially in place: collaborator roles, document-level visibility, scoped client evidence submission, document security updates, document access logging, seeded sensitive evidence categories, default confidentiality labels, and pending or approved or rejected security review states for restricted uploads are all wired into the live app. The remaining work in this area is no longer core workflow design. It is mainly whether this should later move from the current app-level permission model into richer claims-based auth and more formal reviewer routing.

Implementation direction:

- add project-level collaborator access rules
- add audit-file and document-level visibility rules
- add restricted evidence categories for confidential content such as payroll, HR, legal, and executive material
- add approval or rejection workflow for uploads that fall into restricted evidence categories
- add client-side contributor access that can submit or review only assigned requests
- log all access grants, access reads, and permission changes in the audit trail

### 2. Collaboration Rights Matrix And Project Scoping

The meeting reinforced that multiple users must collaborate on the same engagement, but not with identical rights. The current product direction needs a more formal matrix for managers, seniors, juniors, reviewers, client contacts, and limited contributors. The core project-to-audit-file linkage gap is now materially closed in the app: audit files can now persist department and project assignment directly from the main form, and the audit project view now drills into linked audit files and routes into the filtered audit-file workspace. Remaining work in this area is more about deeper workflow grouping than about basic linkage.

Implementation direction:

- formalize role templates per engagement
- allow project-specific overrides instead of only broad user roles
- support one project containing multiple audit files with clear linkage to tasks, evidence, and review state
- separate internal audit team access from client access and from restricted subject-matter contributors

### 3. Risk Assessment Form Completion

The live demo exposed that the risk assessment form needed description columns and a more production-ready approval path. The first implementation slice for this is now in place: richer narrative columns are persisted, draft/in review/approved/archived audit-file statuses now exist, and approved or archived audit files are locked against further edits in both the API and frontend. Remaining enhancement work should focus on richer rework or rejection paths if auditors need them beyond the current lock-based lifecycle.

Implementation direction:

- add missing description and narrative fields requested during the meeting
- harden approval state transitions for draft, submitted, approved, and returned-for-rework states
- ensure the editable table and approval workflow stay in sync

### 4. Auditor-Validated Materiality Rules

The meeting confirmed that the chosen benchmarks are broadly correct for finance audit, but the benchmark percentages still need validation. This is important because materiality and clearly trivial thresholds drive the rest of the audit approach. The implementation gap is now partly closed in the live app: benchmark profiles are persisted in the database, each profile now carries an explicit validation status and note, the materiality workflow captures entity and industry context plus benchmark-selection rationale, and every activation or override now writes a materiality approval-history entry. The remaining open item is still the same one raised in the meeting notes: the actual percentage defaults must be confirmed by an auditor before any profile is treated as validated rather than pending confirmation.

Implementation direction:

- validate default percentages for profit before tax, revenue, and total assets with auditor-reviewed guidance
- store the rationale for chosen benchmark and percentage
- support entity-type or industry guidance where the benchmark basis changes
- preserve clearly trivial and performance materiality as first-class thresholds
- add reviewer approval history for overrides to the recommended thresholds

### 5. Trial Balance Mapping To Financial Statement Structure

One of the most important missing capabilities is the move from a raw trial balance to a usable financial statement view. The meeting was explicit that a meaningful end-state is when the system can take a trial balance and map it into draft financial statements.

This slice is now implemented in the live product. A finance reporting workspace sits inside the audit-file details view, consumes the imported trial balance data already stored in the analytics layer, generates initial income statement and balance sheet classifications with heuristics or reusable profile rules, supports reviewer edits on individual account mappings, and persists reusable mapping profiles for recurring clients or engagement approaches.

Implementation direction:

- add trial balance mapping into income statement and balance sheet groupings
- support mapping rules for income, expenses, assets, liabilities, and equity
- allow user review and correction of mapping before generation
- persist mapping profiles by client or engagement where useful

### 6. Finalization-Stage Draft Financial Statements

The meeting repeatedly framed signed financial statements as a core objective of the audit process. Audit Core currently needs an explicit finalization-stage capability that produces a draft or dummy financial statement package from mapped trial-balance data.

This is now implemented as part of the finance reporting workspace. Users can generate draft income statement and balance sheet outputs directly from the mapped trial balance, and the resulting draft-generation state is persisted into a dedicated finance finalization record for the audit file.

Implementation direction:

- add a finalization workspace after findings and review stages
- generate draft income statement and balance sheet outputs
- link generated outputs back to the evidence, planning, and findings trail
- prepare for later signed-financial-statement workflows even if signature and publishing stay in a later phase

### 7. General Ledger Transaction Triage And Support Requests

Another major gap is the ability to ingest a general ledger extract and identify which transactions require supporting documentation. The meeting made this the practical definition of being close to a finished finance-audit workflow.

This is now materially in place. The product already had journal-entry import in the analytics and materiality flow, and the finance reporting workspace now operationalizes that dataset for substantive review by generating support-request queues from imported general-ledger rows using materiality, journal-risk, and revenue-risk selections.

Implementation direction:

- ingest general-ledger extracts alongside trial balance uploads
- identify transactions above materiality or other risk thresholds
- create support-request queues for transactions requiring evidence
- show why a transaction was selected, for example materiality, journal-risk, or revenue-risk logic
- let reviewers mark requests as received, cleared, escalated, or unresolved

### 8. Revenue And Journal High-Risk Assumption Coverage

The meeting highlighted two standard high-risk areas in financial audit:

- revenue understatement
- journal controls / journal manipulation risk

Some of this exists directionally in the analytics layer, but it needs to be made more explicit in the finance-audit operating flow.

That explicit operating link is now in place. Finance support requests generated from imported journals now preserve the selection reason, expose the related risk flags in the audit-file workspace, and let reviewers link each selected item back to procedures, walkthroughs, controls, and findings from the same engagement.

Implementation direction:

- connect revenue and journal-risk analytics directly to planned procedures and support requests
- surface invoice sequence gaps, large credit notes, unusual journals, posting rights, and approval rights in one reviewable workflow
- tie those selections back to walkthroughs, controls, findings, and finalization notes

### 9. Recommendation And Finalization Workflow Completion

The meeting also pointed out that the product needs a clearer recommendation and finalization stage after evidence and findings work is done.

This is now implemented in a dedicated finance finalization record and workspace section. The workflow now captures overall conclusion, recommendation summary, outstanding matters, reviewer notes, draft-statement status, release-readiness state, and an explicit ready-for-release flag.

Implementation direction:

- add a dedicated finalization stage in the lifecycle
- capture recommendations, conclusion notes, outstanding matters, and release readiness
- connect finalization to review/sign-off rather than leaving it as an implied end state

### 10. Product Consolidation: Heatmap And Departments

The transcript confirmed two simplifications that should happen to reduce product sprawl:

- the standalone heatmap view should be absorbed into the analytical suite
- duplicate department management should be retired where Audit Universe already covers the same hierarchy need

This consolidation is now reflected in the live shell navigation. The standalone heatmap and departments entries have been removed from the primary sidebar, old heatmap routes now normalize back into the Analytical Suite, and old departments routes now normalize back into Audit Universe so the product stops presenting duplicate top-level modules for the same hierarchy and reporting concepts.

Implementation direction:

- remove or de-emphasize duplicate navigation entry points
- keep one reporting path for risk visualization
- keep one hierarchy model centered on Audit Universe

### 11. Configurable Domain Packs Beyond Finance Audit

The meeting also clarified an important boundary: finance audit has a strong baseline, but IT audit and other audit types will need different procedures and workflows. That should be handled as configurable domain packs, not by forcing one rigid process on every audit type.

The first part of that boundary is now implemented in persistence. Finance reporting now runs through a dedicated rule-package table with seeded `finance_audit_core` and a separate future-domain-extension placeholder package so finance defaults stay explicit instead of being hardcoded as the only future operating model.

Implementation direction:

- keep finance-audit defaults as the core product baseline
- layer IT-audit and other domain-specific templates on top
- drive those packs through templates, workflow definitions, and permissions rather than one-off hardcoding

## Recommended Delivery Sequence For The Demo Backlog

1. Auditor validation of the default materiality percentage set for profit before tax, revenue, and total assets
2. Claims-based authorization hardening to replace the current trusted-header user context model
3. Richer rejection, rework, and escalation branches for the newer approval workflows where required

## Database Implementation Rule For This Backlog

This demo backlog should not be treated as frontend-only work. Several items will require database amendments, likely including new tables, new columns, new lookup data, and audit-history extensions.

Default rule for implementation:

- design the schema changes with the specific feature, not as one speculative bulk migration
- add or amend SQL schema files when the feature is implemented
- add seed or reference data where the feature needs statuses, categories, templates, or default mappings
- update repository, API, workflow, and frontend layers together so the database shape matches actual behavior
- avoid creating placeholder tables too early where the final workflow is still unsettled

The most likely database-impact areas from this meeting are:

- confidential access control and restricted evidence visibility
- collaborator rights and project/file assignment matrices
- materiality benchmark validation and override history
- trial balance mapping profiles and financial-statement groupings
- general ledger import batches and selected-transaction support queues
- finalization-stage conclusions, recommendations, and release status

## Practical Interpretation Of The Meeting

The demo feedback did not say the product lacks value. It said the product is already strong enough that the missing pieces are now more specific and more demanding:

- secure collaboration instead of broad access
- auditor-calibrated finance logic instead of generic thresholds
- end-to-end finalization instead of only planning and execution
- one coherent Audit Core workflow instead of duplicate legacy navigation paths

That is the correct point in the product lifecycle to be at. The roadmap should now prioritize closing those operational audit gaps rather than adding more disconnected screens.
