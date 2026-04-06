# Materiality Calculation Implementation Plan

## Purpose

This plan closes the current gap between:

- `materiality capture`
- and the fuller workflow discussed in the meeting notes:
  - import financial data
  - calculate materiality from that data
  - use the result in scoping, analytics, procedures, working papers, and findings evaluation

The current app already supports:

- external vs internal audit distinction
- planning fields for materiality
- trial balance and journal import
- analytics widgets using imported finance data

What is still missing is the real materiality operating flow.

---

## What The Meeting Notes Implied

The meeting notes point to this model:

1. Materiality is mainly an `external audit` concept.
2. Auditors should use imported financial information to determine materiality.
3. Materiality should drive:
   - planning
   - FSLI scoping
   - analytics thresholds
   - working papers
   - misstatement evaluation
4. The app should not rely mainly on auditors typing values manually.

So the target workflow is:

`Imported financials -> benchmark selection -> materiality calculation -> approval -> downstream audit use`

---

## Current Gap

The app currently stores and displays:

- `materiality`
- `materiality_basis`
- `overall_materiality`
- `performance_materiality`
- `clearly_trivial_threshold`

Those fields live on `audit_engagement_plans`.

That is useful, but incomplete, because:

- there is no materiality calculation engine
- there is no benchmark selection workflow
- there is no link back to imported trial balance batches
- there is no record of how the threshold was derived
- there is no propagation into scoping or findings evaluation

---

## Comparison Against The External-Audit Reference Workflow

The materiality guide and the two HTML references describe a stronger operating model than the app had before this expansion.

### What the reference workflow requires

- imported financial data should be the starting point
- auditors should calculate:
  - overall materiality
  - performance materiality
  - clearly trivial
- performance materiality should drive:
  - `key item / 100% testing`
  - `sample pool`
- overall materiality should help drive:
  - balance/FSLI scoping
- misstatements should accumulate into a `Summary of Audit Differences`
- auditors should still have a manual override path

### What is now implemented

- trial balance import inside the materiality workflow
- journal-entry import inside the materiality workflow
- benchmark candidate generation from imported trial balance data
- manual materiality calculation and activation
- active calculation selection
- `Materiality Application` view in Planning showing:
  - key items above performance materiality
  - sample pool below performance materiality
  - balance/FSLI scope candidates above overall materiality
  - SAD-style misstatement summary from `audit_misstatements`
- persisted scope/FSLI decision capture into `audit_materiality_scope_links`
- persisted misstatement capture into `audit_misstatements`

### What is still missing

- specific materiality for sensitive classes/disclosures
- direct sampling workflow actions from the stratified population
- qualitative materiality flags
- automatic recalculation prompts when imported financials change materially
- automated persistence of accepted scope candidates into downstream scoping/testing records

---

## Current Implemented Slice

The current implementation now covers this real workflow:

`Import trial balance / journals -> generate or manually define materiality -> set active thresholds -> stratify imported population -> review key items, sample pool, and scope candidates -> record scope decisions and misstatements -> compare recorded misstatements against CT / PM / OM`

This implemented slice now also includes:

- fuller misstatement evaluation in the audit file
- escalation of material misstatements into findings
- active benchmark and threshold-source visibility in analytics widgets
- active benchmark and threshold-source visibility in the findings workspace

This is materially closer to the external-audit process described in the reference content, but it is not the final state yet.

---

## Target User Workflow

## 1. Import finance data

Auditor imports:

- trial balance
- journal entries
- optional prior year trial balance
- optional benchmark/industry data

The imported data already lands in:

- `audit_trial_balance_snapshots`
- `audit_gl_journal_entries`
- `audit_analytics_import_batches`

## 2. Open Materiality Workspace

Inside the audit file `Planning` tab, external audits should show a dedicated `Materiality Workspace`.

The workspace should let the auditor:

- select the calculation source batch
- choose a benchmark basis
- choose a percentage
- set performance materiality percentage
- set clearly trivial percentage
- document rationale
- preview the calculated thresholds before saving

## 3. Calculate materiality

The system should calculate:

- benchmark amount
- overall materiality
- performance materiality
- clearly trivial threshold

The system should also store:

- selected benchmark type
- selected percentage
- source dataset/batch
- who calculated it
- when it was calculated
- whether the value was later overridden manually

## 4. Review and approve

Materiality should not just save silently.

It should support:

- draft
- calculated
- approved
- overridden
- superseded

This can later plug into Elsa if materiality approval becomes a formal workflow step.

## 5. Apply materiality downstream

Once calculated, the app should use the thresholds in:

- scope suggestions
- FSLI prioritization
- analytical thresholds
- journal testing
- working paper templates
- findings / misstatement evaluation
- final reporting

---

## Scope Of Implementation

## Phase 1: Materiality Calculation Foundation

Deliver:

- dedicated materiality workspace in `Planning`
- benchmark selection UI
- auto-calc from imported trial balance
- save calculation run and output
- manual override support
- audit trail events for calculation and override

## Phase 2: Scope And Analytics Integration

Deliver:

- FSLI scoping suggestions based on materiality
- trial balance movement flags using threshold
- journal testing risk flags using threshold
- materiality-aware analytics widgets
- working paper and procedure templates pre-populated with threshold context

## Phase 3: Misstatement And Reporting Integration

Deliver:

- misstatement capture against thresholds
- aggregate unadjusted differences
- compare against overall/performance materiality
- reporting view showing materiality conclusion
- final sign-off view with materiality summary

---

## Frontend Changes Needed

## Audit File / Planning

Add a dedicated `Materiality Workspace` card or subpanel with:

- source batch selector
- basis dropdown
- benchmark amount preview
- benchmark percentage input
- performance materiality percentage
- clearly trivial percentage
- rationale text
- `Calculate`
- `Save`
- `Override`
- `Approve`

## Scope Register

Add materiality-driven helpers:

- show FSLI/account balance
- show whether balance exceeds materiality
- show whether balance exceeds performance materiality
- quick action: `Scope in because material`

## Analytics

Use calculated materiality in:

- trial balance movement widget
- reasonability widget
- benchmark widget
- journal exception widget
- management override widget

## Findings / Misstatements

Add a section for:

- potential misstatement amount
- adjusted / unadjusted
- individually material?
- material in aggregate?
- linked assertion / FSLI

---

## Backend Changes Needed

## New service layer

Add a materiality service that:

- reads imported TB data
- derives candidate benchmark amounts
- calculates thresholds
- stores run history
- applies override logic
- exposes downstream summary for analytics and reporting

## New API endpoints

Recommended endpoints:

- `GET /api/v1/AuditMateriality/GetWorkspace/{referenceId}`
- `GET /api/v1/AuditMateriality/GetCandidateBenchmarks/{referenceId}`
- `POST /api/v1/AuditMateriality/Calculate`
- `POST /api/v1/AuditMateriality/Approve`
- `POST /api/v1/AuditMateriality/Override`
- `GET /api/v1/AuditMateriality/GetHistory/{referenceId}`
- `GET /api/v1/AuditMateriality/GetMisstatementSummary/{referenceId}`

## Repository logic

The repository should support:

- reading current-year TB by reference
- reading prior-year TB by reference
- deriving balances by FSLI
- aggregating misstatements
- resolving active materiality version

---

## Schema Amendments

## Existing table amendments

### `audit_engagement_plans`

The table already contains the core numeric fields, but it needs source/governance metadata.

Add:

- `materiality_source VARCHAR(50)`  
  Values: `manual`, `calculated`, `manual_override`
- `materiality_status VARCHAR(50)`  
  Values: `draft`, `calculated`, `approved`, `overridden`, `superseded`
- `materiality_benchmark_name VARCHAR(100)`  
  Examples: `profit_before_tax`, `revenue`, `total_assets`, `expenses`
- `materiality_benchmark_amount NUMERIC(18,2)`
- `materiality_percentage NUMERIC(9,4)`
- `performance_materiality_percentage NUMERIC(9,4)`
- `clearly_trivial_percentage NUMERIC(9,4)`
- `materiality_currency_code VARCHAR(10)`
- `calculated_from_import_batch_id INTEGER`
- `last_materiality_calculation_id BIGINT`
- `materiality_last_calculated_at TIMESTAMP`
- `materiality_last_calculated_by_user_id INTEGER`
- `materiality_approved_at TIMESTAMP`
- `materiality_approved_by_user_id INTEGER`
- `materiality_override_reason TEXT`

### `audit_scope_items`

Add materiality application fields:

- `fsli_balance NUMERIC(18,2)`
- `is_material_scope_item BOOLEAN DEFAULT FALSE`
- `materiality_rationale TEXT`
- `materiality_assessment_id BIGINT`

### `audit_findings`

If findings are also used to capture misstatements, add:

- `potential_misstatement_amount NUMERIC(18,2)`
- `is_adjusted BOOLEAN`
- `is_quantitatively_material BOOLEAN`
- `is_qualitatively_material BOOLEAN`
- `fsli VARCHAR(255)`

If you want a cleaner design, keep findings for audit issues and use a separate table for misstatements instead.

---

## New tables

### `audit_materiality_calculations`

Purpose:

- store every calculation run
- preserve methodology and history

Suggested fields:

- `id BIGSERIAL PRIMARY KEY`
- `reference_id INTEGER NOT NULL`
- `import_batch_id INTEGER NULL`
- `calculation_version INTEGER NOT NULL`
- `benchmark_name VARCHAR(100) NOT NULL`
- `benchmark_amount NUMERIC(18,2) NOT NULL`
- `materiality_percentage NUMERIC(9,4) NOT NULL`
- `overall_materiality NUMERIC(18,2) NOT NULL`
- `performance_materiality_percentage NUMERIC(9,4) NOT NULL`
- `performance_materiality NUMERIC(18,2) NOT NULL`
- `clearly_trivial_percentage NUMERIC(9,4) NOT NULL`
- `clearly_trivial_threshold NUMERIC(18,2) NOT NULL`
- `currency_code VARCHAR(10) NULL`
- `rationale TEXT NULL`
- `status VARCHAR(50) NOT NULL DEFAULT 'Calculated'`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- `superseded_by_id BIGINT NULL`
- `created_by_user_id INTEGER NULL`
- `created_by_name VARCHAR(255) NULL`
- `created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`
- `approved_by_user_id INTEGER NULL`
- `approved_by_name VARCHAR(255) NULL`
- `approved_at TIMESTAMP NULL`

Indexes:

- `(reference_id, is_active)`
- `(reference_id, calculation_version DESC)`
- `(import_batch_id)`

### `audit_materiality_candidates`

Purpose:

- store candidate benchmark values derived from imported finance data
- make the UI explainable

Suggested fields:

- `id BIGSERIAL PRIMARY KEY`
- `reference_id INTEGER NOT NULL`
- `import_batch_id INTEGER NULL`
- `benchmark_name VARCHAR(100) NOT NULL`
- `benchmark_amount NUMERIC(18,2) NOT NULL`
- `source_logic VARCHAR(255) NOT NULL`
- `notes TEXT NULL`
- `created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`

Examples:

- `profit_before_tax`
- `revenue`
- `total_assets`
- `total_expenses`

### `audit_misstatements`

Purpose:

- evaluate identified differences against materiality cleanly

Suggested fields:

- `id BIGSERIAL PRIMARY KEY`
- `reference_id INTEGER NOT NULL`
- `finding_id INTEGER NULL`
- `working_paper_id INTEGER NULL`
- `fsli VARCHAR(255) NULL`
- `assertion TEXT NULL`
- `description TEXT NOT NULL`
- `amount NUMERIC(18,2) NOT NULL`
- `currency_code VARCHAR(10) NULL`
- `is_adjusted BOOLEAN NOT NULL DEFAULT FALSE`
- `is_factual BOOLEAN NOT NULL DEFAULT TRUE`
- `is_judgmental BOOLEAN NOT NULL DEFAULT FALSE`
- `is_projected BOOLEAN NOT NULL DEFAULT FALSE`
- `is_quantitatively_material BOOLEAN NOT NULL DEFAULT FALSE`
- `is_qualitatively_material BOOLEAN NOT NULL DEFAULT FALSE`
- `evaluation_notes TEXT NULL`
- `calculation_id BIGINT NULL`
- `created_by_user_id INTEGER NULL`
- `created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`

Indexes:

- `(reference_id)`
- `(reference_id, is_adjusted)`
- `(reference_id, fsli)`

### `audit_materiality_scope_links`

Purpose:

- explain why a scope item is in/out of scope because of materiality

Suggested fields:

- `id BIGSERIAL PRIMARY KEY`
- `reference_id INTEGER NOT NULL`
- `scope_item_id INTEGER NOT NULL`
- `calculation_id BIGINT NOT NULL`
- `fsli VARCHAR(255) NULL`
- `balance_amount NUMERIC(18,2) NULL`
- `threshold_amount NUMERIC(18,2) NULL`
- `decision VARCHAR(50) NOT NULL`
- `decision_reason TEXT NULL`
- `created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`

Values for `decision`:

- `scope_in`
- `scope_out`
- `manual_override`

---

## Optional views

Recommended reporting views:

### `vw_audit_materiality_current`

Purpose:

- expose the active materiality calculation per reference

### `vw_audit_materiality_scope_candidates`

Purpose:

- join TB balances to scope items and show which ones exceed threshold

### `vw_audit_misstatement_summary`

Purpose:

- summarize adjusted vs unadjusted differences against current thresholds

---

## Calculation Rules

The system should support configurable methodology, not one hard-coded rule.

Recommended benchmark options:

- `profit_before_tax`
- `revenue`
- `total_assets`
- `total_expenses`

Recommended implementation approach:

- let the auditor choose the benchmark
- let the auditor choose the percentage
- calculate thresholds transparently
- allow manual override with mandatory rationale

Do not hard-code one firm methodology as universal.

---

## Data Derivation Rules

To calculate benchmark candidates from imported TB:

- Revenue:
  - sum accounts mapped to revenue FSLIs
- Total assets:
  - sum balance-sheet asset FSLIs
- Total expenses:
  - sum expense FSLIs
- Profit before tax:
  - derive from imported P&L categories if available
  - otherwise calculate from mapped revenue less expenses excluding tax lines

This means the TB import process must either:

- already provide mapped `fsli`
- or the app must maintain an account-to-FSLI mapping layer

---

## Dependencies

This feature depends on:

- imported trial balance data existing for the audit file
- finance data being mapped to meaningful FSLI/account categories
- external audit mode being selected on the audit file

Without those, the system should:

- show the materiality workspace
- but mark it as `Awaiting finance import`

---

## UX Rules

For `Internal Audit`:

- do not make materiality central
- show it only if manually captured or specifically required

For `External Audit`:

- show materiality prominently in `Planning`
- use it in scope and analytics
- show active thresholds in the audit-file header or overview

---

## Acceptance Criteria

The implementation is complete when:

1. Auditor can import TB data for an external audit file.
2. Auditor can open `Planning -> Materiality Workspace`.
3. System can suggest benchmark candidates from imported data.
4. Auditor can calculate thresholds from a selected benchmark and percentage.
5. Calculation history is persisted.
6. Manual override is supported with rationale.
7. Scope items can be flagged as material/non-material.
8. Analytics can compare movements against active materiality.
9. Misstatements can be evaluated against current thresholds.
10. The current active materiality calculation is visible in the audit file.

---

## Recommended Build Order

1. Add schema amendments and new tables.
2. Build backend materiality repository/service/API.
3. Build `Materiality Workspace` in `Planning`.
4. Calculate candidates from imported TB.
5. Save and approve materiality runs.
6. Add scope integration.
7. Add analytics threshold integration.
8. Add misstatement evaluation.
9. Add reporting and sign-off integration.

---

## Recommendation

Treat the existing manual materiality fields as:

- display fields
- override fields
- reporting fields

Do not treat them as the primary source of truth anymore.

The primary source of truth for external audit should become:

- the active row in `audit_materiality_calculations`

with `audit_engagement_plans` holding the current published summary.
