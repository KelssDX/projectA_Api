-- =====================================================
-- Phase 5: Audit Reporting Data Mart Views
-- Purpose:
--   Provide stable reporting-layer views for Power BI and
--   native analytics reconciliation.
-- =====================================================

SET search_path TO "Risk_Assess_Framework";

CREATE OR REPLACE VIEW vw_audit_reporting_findings_summary AS
WITH finding_summary AS (
    SELECT
        f.reference_id,
        COUNT(*) AS total_findings,
        COUNT(*) FILTER (WHERE COALESCE(fs.is_closed, FALSE) = FALSE) AS open_findings
    FROM audit_findings f
    LEFT JOIN ra_finding_status fs ON fs.id = f.status_id
    GROUP BY f.reference_id
),
recommendation_summary AS (
    SELECT
        f.reference_id,
        COUNT(*) AS total_recommendations,
        COUNT(*) FILTER (
            WHERE COALESCE(rs.name, 'Pending') NOT IN ('Implemented', 'Rejected', 'Deferred')
        ) AS open_recommendations
    FROM audit_recommendations r
    INNER JOIN audit_findings f ON f.id = r.finding_id
    LEFT JOIN ra_recommendation_status rs ON rs.id = r.status_id
    GROUP BY f.reference_id
),
management_action_summary AS (
    SELECT
        ma.reference_id,
        COUNT(*) FILTER (
            WHERE ma.due_date < CURRENT_DATE
              AND LOWER(COALESCE(ma.status, 'open')) NOT IN ('closed', 'completed', 'validated', 'cancelled', 'canceled')
        ) AS overdue_management_actions
    FROM audit_management_actions ma
    GROUP BY ma.reference_id
)
SELECT
    COALESCE(f.reference_id, r.reference_id, m.reference_id) AS reference_id,
    COALESCE(f.total_findings, 0) AS total_findings,
    COALESCE(f.open_findings, 0) AS open_findings,
    COALESCE(r.total_recommendations, 0) AS total_recommendations,
    COALESCE(r.open_recommendations, 0) AS open_recommendations,
    COALESCE(m.overdue_management_actions, 0) AS overdue_management_actions
FROM finding_summary f
FULL OUTER JOIN recommendation_summary r ON r.reference_id = f.reference_id
FULL OUTER JOIN management_action_summary m ON m.reference_id = COALESCE(f.reference_id, r.reference_id);

CREATE OR REPLACE VIEW vw_audit_reporting_execution_summary AS
WITH working_paper_summary AS (
    SELECT
        wp.reference_id,
        COUNT(*) FILTER (WHERE COALESCE(wp.is_template, FALSE) = FALSE AND COALESCE(wp.is_active, TRUE) = TRUE) AS total_working_papers,
        COUNT(DISTINCT CASE WHEN s.id IS NOT NULL THEN wp.id END) FILTER (WHERE COALESCE(wp.is_template, FALSE) = FALSE AND COALESCE(wp.is_active, TRUE) = TRUE) AS signed_off_working_papers
    FROM audit_working_papers wp
    LEFT JOIN audit_working_paper_signoffs s ON s.working_paper_id = wp.id
    GROUP BY wp.reference_id
),
document_summary AS (
    SELECT
        d.reference_id,
        COUNT(*) FILTER (WHERE COALESCE(d.is_active, TRUE) = TRUE) AS total_documents
    FROM audit_documents d
    GROUP BY d.reference_id
),
evidence_summary AS (
    SELECT
        er.reference_id,
        COUNT(*) FILTER (WHERE COALESCE(es.is_closed, FALSE) = FALSE) AS open_evidence_requests
    FROM audit_evidence_requests er
    LEFT JOIN ra_evidence_request_status es ON es.id = er.status_id
    GROUP BY er.reference_id
),
workflow_summary AS (
    SELECT
        wi.reference_id,
        COUNT(*) FILTER (WHERE COALESCE(wi.is_active, FALSE) = TRUE) AS active_workflows
    FROM audit_workflow_instances wi
    GROUP BY wi.reference_id
),
task_summary AS (
    SELECT
        wt.reference_id,
        COUNT(*) FILTER (WHERE LOWER(COALESCE(wt.status, 'pending')) = 'pending') AS pending_workflow_tasks
    FROM audit_workflow_tasks wt
    GROUP BY wt.reference_id
)
SELECT
    COALESCE(wp.reference_id, d.reference_id, er.reference_id, wi.reference_id, wt.reference_id) AS reference_id,
    COALESCE(wp.total_working_papers, 0) AS total_working_papers,
    COALESCE(wp.signed_off_working_papers, 0) AS signed_off_working_papers,
    COALESCE(d.total_documents, 0) AS total_documents,
    COALESCE(er.open_evidence_requests, 0) AS open_evidence_requests,
    COALESCE(wi.active_workflows, 0) AS active_workflows,
    COALESCE(wt.pending_workflow_tasks, 0) AS pending_workflow_tasks
FROM working_paper_summary wp
FULL OUTER JOIN document_summary d ON d.reference_id = wp.reference_id
FULL OUTER JOIN evidence_summary er ON er.reference_id = COALESCE(wp.reference_id, d.reference_id)
FULL OUTER JOIN workflow_summary wi ON wi.reference_id = COALESCE(wp.reference_id, d.reference_id, er.reference_id)
FULL OUTER JOIN task_summary wt ON wt.reference_id = COALESCE(wp.reference_id, d.reference_id, er.reference_id, wi.reference_id);

CREATE OR REPLACE VIEW vw_audit_reporting_analytics_summary AS
WITH journal_summary AS (
    SELECT reference_id, COUNT(*) AS journal_entry_rows
    FROM audit_gl_journal_entries
    GROUP BY reference_id
),
tb_summary AS (
    SELECT reference_id, COUNT(*) AS trial_balance_accounts
    FROM audit_trial_balance_snapshots
    GROUP BY reference_id
),
benchmark_summary AS (
    SELECT reference_id, COUNT(*) AS industry_benchmark_metrics
    FROM audit_industry_benchmarks
    GROUP BY reference_id
),
forecast_summary AS (
    SELECT reference_id, COUNT(*) AS reasonability_forecast_metrics
    FROM audit_reasonability_forecasts
    GROUP BY reference_id
)
SELECT
    COALESCE(j.reference_id, tb.reference_id, b.reference_id, f.reference_id) AS reference_id,
    COALESCE(j.journal_entry_rows, 0) AS journal_entry_rows,
    COALESCE(tb.trial_balance_accounts, 0) AS trial_balance_accounts,
    COALESCE(b.industry_benchmark_metrics, 0) AS industry_benchmark_metrics,
    COALESCE(f.reasonability_forecast_metrics, 0) AS reasonability_forecast_metrics
FROM journal_summary j
FULL OUTER JOIN tb_summary tb ON tb.reference_id = j.reference_id
FULL OUTER JOIN benchmark_summary b ON b.reference_id = COALESCE(j.reference_id, tb.reference_id)
FULL OUTER JOIN forecast_summary f ON f.reference_id = COALESCE(j.reference_id, tb.reference_id, b.reference_id);
