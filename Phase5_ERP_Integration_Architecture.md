# Phase 5 ERP Integration Architecture

## Purpose

Define a practical data-integration approach for audit analytics so the platform can ingest client data without coupling the core app directly to each ERP.

## Design Direction

- Use a staging-first architecture.
- Keep ERP-specific extraction separate from analytics computation.
- Treat `audit_analytics_import_batches` as the canonical ingestion audit log.
- Load raw or near-raw extracts into audit staging tables before transforming them into reporting views or analytics widgets.
- Support both cloud-hosted and client-environment deployment models.

## Canonical Audit Datasets

The app should standardize incoming data into these dataset families:

- `general_ledger_journals`
- `trial_balance_snapshots`
- `industry_benchmarks`
- `reasonability_forecasts`
- `holiday_calendars`
- future: `subledger_ar`, `subledger_ap`, `fixed_assets`, `inventory_movements`, `payroll_transactions`

## Connector Strategy

### SAP

- Preferred extraction:
  - scheduled CSV export
  - SAP BW extract
  - OData/API where available
- Typical datasets:
  - BKPF / BSEG style journal data
  - trial balance extracts
  - vendor and customer aging
- Integration note:
  - start with file-based ingestion because it is lower risk than direct SAP connectivity

### Oracle

- Preferred extraction:
  - read-only reporting schema
  - Oracle BI export
  - scheduled CSV
- Typical datasets:
  - GL journals
  - balances
  - budgets / forecasts
- Integration note:
  - maintain a mapping layer for chart of accounts and period labels

### Microsoft Dynamics

- Preferred extraction:
  - Dataverse export
  - OData / API
  - scheduled report export
- Typical datasets:
  - GL entries
  - trial balance
  - dimensions and business units
- Integration note:
  - dimension handling needs to map cleanly to FSLI and business-unit fields in staging

### Sage

- Preferred extraction:
  - CSV or Excel exports
  - read-only replica if available
- Typical datasets:
  - journals
  - TB
  - account master
- Integration note:
  - file-based ingestion is likely the fastest path for most Sage clients

### Xero

- Preferred extraction:
  - API pull
  - CSV exports for fallback
- Typical datasets:
  - journals
  - trial balance
  - chart of accounts
- Integration note:
  - API rate limits and token refresh should be isolated in the connector worker, not the main app

## High-Volume Ingestion Approach

### Processing Pattern

1. Extract from source system into flat files or connector payloads.
2. Register an `audit_analytics_import_batches` record.
3. Land data in staging tables in chunks.
4. Run validation and reconciliation checks.
5. Expose results to analytics widgets and reporting views.

### Technical Controls

- Use chunked imports rather than single huge inserts.
- Prefer bulk database loading for large journal populations.
- Preserve source document numbers and source system identifiers.
- Add indexes on reference, year, period, account, and user fields.
- Reject malformed rows into an exception log instead of failing the entire batch.
- Keep import batches immutable after completion.

### Data Quality Checks

- row counts against source extracts
- duplicate journal detection
- missing posting dates
- missing account numbers
- period-to-year consistency
- debit/credit versus net amount consistency
- current-year versus prior-year snapshot completeness

## Client-Environment Deployment Options

### Option 1: Cloud App + Client File Upload

- Fastest implementation path.
- Best for smaller clients or low-volume extracts.
- Sensitive data risk is higher because data leaves the client environment.

### Option 2: Cloud App + Client-Side Connector Agent

- Recommended medium-term option.
- Lightweight agent runs in the client environment.
- Agent extracts data and pushes only approved staged payloads.
- Good balance between usability and client security requirements.

### Option 3: Full Client-Hosted Deployment

- Recommended for highly sensitive audits.
- API, worker, and database run in the client environment.
- Power BI or reporting can read from the local reporting views.
- Best fit where data residency rules block external hosting.

## Security and Governance

- Use read-only ERP credentials where direct connectivity exists.
- Separate connector secrets from the main application configuration.
- Log every import with user, source system, dataset type, and row count.
- Do not allow source-system writes from the audit platform.
- Mask or omit unnecessary PII fields in staging.
- Apply retention rules to raw staging data and derived reporting data separately.

## Recommended Implementation Sequence

1. Finalize canonical dataset contracts for journals, TB, benchmarks, and forecasts.
2. Build file-ingestion first for CSV and Excel.
3. Add a connector worker abstraction with source-specific adapters.
4. Implement SAP, Dynamics, and Xero first.
5. Add Oracle and Sage adapters next.
6. Add data-quality exception logging and reconciliation dashboards.
7. Add reporting views for Power BI and native analytics on top of the staged data.

## Immediate Build Targets

- add upload and batch-management UI for analytics imports
- add batch validation and rejection logging
- add reporting views/data mart over the staging tables
- add connector-agent design for client-environment deployment
