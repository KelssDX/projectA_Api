# Power BI Integration Plan for Analytical Report

## Purpose

This document outlines how Power BI can be integrated into the existing Analytical Report as an optional reporting mode, without replacing the current in-app dashboard.

The goal is to let the platform support two reporting experiences:

1. The existing native Analytical Report in `RiskAssessmentApp_Frontend`
2. An optional Power BI experience for richer executive dashboards, cross-filtering, scheduled distribution, and enterprise BI use cases

---

## Current State

### Existing Analytical Report

- Frontend view: `RiskAssessmentApp_Frontend/src/views/analytics/analytical_dashboard.py`
- Current API source: `/RiskGraphs/GetAnalyticalReport`
- Current client method: `RiskAssessmentApp_Frontend/src/api/auditing_client.py`
- Current report model: widget-based Flet dashboard with assessment-context filtering

### Current Strengths

- Already integrated into the application workflow
- Context-aware by `referenceId`
- Supports custom widgets, heatmap embedding, and drill-down UI
- No external BI licensing dependency for the current experience

### Current Gaps That Power BI Could Address

- Limited self-service slicing and dicing for business users
- No native scheduled dashboard subscriptions
- No enterprise BI semantic model for reuse across reports
- Limited ad hoc executive reporting compared with dedicated BI tools

---

## Integration Objective

Power BI should be introduced as an option, not a forced replacement.

Recommended UX:

- `Analytical Report` remains the default experience
- Add a report mode toggle:
  - `Native Dashboard`
  - `Power BI`
- If Power BI is not configured, the application continues to work normally

This keeps the current reporting feature stable while enabling a higher-end reporting path for users who need it.

---

## Integration Options

## Option 1: Link Out to Power BI Service

The application shows a button such as `Open in Power BI`, which opens a published Power BI report in the browser.

### How It Works

- Build the report in Power BI Desktop
- Publish to Power BI Service
- Store the report URL in application configuration
- Pass context using filters in the URL where feasible

### Pros

- Fastest to implement
- Minimal backend changes
- Low risk to the current application

### Cons

- Breaks the in-app experience
- Authentication and row-level security must be handled in Power BI separately
- Context passing is limited compared with embedded scenarios

### Best Use

- Phase 1 proof of concept
- Internal users already licensed for Power BI

---

## Option 2: Embed Power BI Report Inside the Analytical Report Screen

The application hosts a Power BI report inside the Analytical Report page as an alternate tab or mode.

### How It Works

- Publish a Power BI report and dataset
- Backend generates embed configuration
- Frontend renders embedded report in a web container or browser-hosted view
- Current assessment context is passed as filters

### Pros

- Better user experience than link-out
- Keeps reporting inside the product flow
- Supports interactive Power BI visuals

### Cons

- More integration work
- Requires embed token flow and Power BI workspace management
- Flet desktop constraints may require opening an embedded web view or browser wrapper

### Best Use

- Preferred medium-term option if seamless in-app BI is required

---

## Option 3: Build a Reporting Data Mart for Power BI

The application prepares curated reporting tables or views specifically for Power BI while preserving the native dashboard APIs.

### How It Works

- Create SQL views or reporting tables for risk, controls, assessments, trends, departments, and audit universe
- Power BI connects to those curated structures
- The app optionally links out to or embeds Power BI reports built on the reporting layer

### Pros

- Clean separation between transactional logic and reporting logic
- Better Power BI performance and maintainability
- Easier to create multiple reports later

### Cons

- Requires database and ETL-style design effort
- Slightly longer implementation timeline

### Best Use

- Recommended foundation for any serious Power BI rollout

---

## Recommended Approach

Recommended path:

1. Build a reporting data layer first
2. Deliver `Option 1` as a fast proof of value
3. Upgrade to `Option 2` if embedded analytics is still required after adoption

Reasoning:

- The current app already has a working native Analytical Report
- The highest long-term value is in clean reporting data structures, not just embedding a BI frame
- A phased rollout reduces risk and avoids blocking current users

---

## Proposed Architecture

## Application Layer

- Keep the existing `AnalyticalDashboard` intact
- Add a report mode selector:
  - `Native`
  - `Power BI`
- Add feature flags in config:
  - `power_bi_enabled`
  - `power_bi_embed_enabled`
  - `power_bi_report_url`
  - `power_bi_workspace_id`
  - `power_bi_report_id`

## Backend Layer

Add a small Power BI integration service in the API layer to:

- Return Power BI configuration metadata
- Optionally generate embed token payloads
- Map current `referenceId`, department, or audit-universe context into report filters

Potential API additions:

- `GET /Reporting/PowerBI/Config`
- `POST /Reporting/PowerBI/EmbedToken`
- `GET /Reporting/PowerBI/ContextFilter?referenceId={id}`

## Data Layer

Create reporting-ready SQL views or materialized reporting tables for:

- assessment summary
- risk scores
- inherent vs residual comparisons
- control coverage
- top residual risks
- heatmap points
- department comparison
- trend history
- audit findings and recommendations
- audit universe hierarchy

This layer should be optimized for analytics rather than write operations.

---

## Data Model Proposal

Power BI will work best if the reporting model is shaped into facts and dimensions.

### Suggested Dimensions

- `dim_assessment`
- `dim_department`
- `dim_project`
- `dim_risk_category`
- `dim_audit_universe`
- `dim_date`
- `dim_control`
- `dim_user_owner`

### Suggested Fact Tables / Views

- `fact_risk_assessment_scores`
- `fact_control_coverage`
- `fact_heatmap_distribution`
- `fact_findings`
- `fact_recommendations`
- `fact_risk_trends`
- `fact_audit_coverage`

This will allow Power BI to support both summary dashboards and drill-through reporting.

---

## User Experience Proposal

## Analytical Report Screen Changes

Add the following controls near the existing dashboard actions:

- `Report Mode` dropdown or segmented control
- `Open in Power BI` button when enabled
- `Refresh BI Data` button if manual refresh is needed

### Behaviour

- Default mode remains `Native Dashboard`
- If `Power BI` is selected:
  - show a configured message if Power BI is not enabled
  - otherwise open the Power BI report or embedded view
- Preserve current `referenceId` context where possible

### Suggested Modes

- `Native Dashboard`
- `Power BI Executive Dashboard`
- `Power BI Detailed Analysis`

This allows multiple BI reports later without redesigning the feature.

---

## Security and Access Control

Power BI integration must align with application-level permissions.

### Key Requirements

- Users should only see data they are authorized to view
- Power BI row-level security must match application roles
- Sensitive identifiers should not be exposed via unsecured query strings
- Embed token generation should happen server-side only

### Recommended Security Model

- Application authenticates user
- Backend resolves allowed data scope
- Backend returns embed configuration restricted to that scope
- Power BI dataset applies row-level security rules using user identity or scoped filters

---

## Technical Constraints for This Repository

This project currently uses a Flet frontend, not a browser-only SPA.

That matters because Power BI embedding is most natural in a web application. For this codebase, practical choices are:

1. Open the Power BI report in the system browser
2. Host a web-based report surface inside a Flet web view if the runtime supports it
3. Build a small web reporting page and launch it from the desktop app

Because of that, link-out integration is the least risky first implementation.

---

## Implementation Phases

## Phase 1: Planning and Data Readiness

- Confirm which Analytical Report widgets must have a Power BI equivalent
- Define reporting KPIs and filters
- Identify source tables and missing historical data
- Design reporting views / data mart
- Decide whether Power BI is licensed per user or via embedded capacity

## Phase 2: Reporting Data Layer

- Create SQL views for the analytical datasets
- Validate numbers against the existing native dashboard
- Document field meanings and business rules

## Phase 3: Power BI Report Build

- Build semantic model in Power BI
- Create executive dashboard pages
- Create drill-through pages
- Add slicers for assessment, department, audit universe, date, and risk category

## Phase 4: Application Integration

- Add configuration flags
- Add report mode selector to the Analytical Report screen
- Implement `Open in Power BI`
- Optionally add backend embed endpoints

## Phase 5: Security and UAT

- Validate row-level security
- Reconcile totals between app widgets and Power BI visuals
- Test user roles and filter propagation
- Test fallback behaviour when Power BI is unavailable

---

## Configuration Proposal

Suggested application settings:

```json
{
  "powerBi": {
    "enabled": false,
    "mode": "link",
    "reportUrl": "",
    "workspaceId": "",
    "reportId": "",
    "datasetId": "",
    "useEmbed": false
  }
}
```

If stored server-side instead, the frontend should consume a safe subset only.

---

## Backend Work Items

- Add reporting configuration model
- Add Power BI integration service abstraction
- Add endpoint for retrieving Power BI availability and metadata
- Add optional embed token endpoint
- Add mapping from `referenceId` to reporting filters
- Add audit logging for BI report access

---

## Frontend Work Items

In `RiskAssessmentApp_Frontend/src/views/analytics/analytical_dashboard.py`:

- add report mode state
- add Power BI launch or embed action
- preserve current assessment selection when switching modes
- show configuration and access errors clearly

Potential supporting work:

- new `PowerBIReportPanel` component
- config-driven visibility
- graceful fallback to native widgets

---

## Data Reconciliation Rules

To avoid mistrust in the reports, Power BI numbers must match existing app calculations.

Validation checklist:

- inherent and residual risk totals match native widgets
- top risks ordering matches API output
- heatmap counts match the heatmap endpoint
- control coverage percentages match the native dashboard logic
- trend metrics use a documented date basis

If Power BI uses a separate reporting model, these rules should be explicitly documented.

---

## Risks

- Power BI licensing or tenant restrictions may delay rollout
- Flet embedding may be less smooth than browser-based embedding
- Current APIs may not expose enough historical data for trend reporting
- Mismatched business logic between app widgets and Power BI can reduce trust
- Row-level security gaps could expose unauthorized data if not designed carefully

---

## Success Criteria

- Users can access the current native Analytical Report with no regression
- Power BI can be enabled per environment through configuration
- Assessment context can be carried into the Power BI experience
- Executive users can consume richer dashboards without leaving the product flow unnecessarily
- Power BI totals are reconciled with the application’s analytical calculations

---

## Recommendation Summary

Recommended implementation decision:

- Keep the existing Analytical Report as the default
- Introduce Power BI as an optional mode
- Start with link-out integration
- Build a proper reporting data layer before deep embedding
- Move to embedded Power BI only if the organization confirms the licensing, security, and hosting model

This approach gives the project a practical path to enterprise BI capabilities without destabilizing the current Analytical Report experience.
