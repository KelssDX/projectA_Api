-- =====================================================
-- Phase 5: Audit Analytics Staging Schema
-- Purpose:
--   Introduce staging tables for journal-entry and trial-balance
--   analytics used by external-audit style analytical procedures.
-- =====================================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS audit_analytics_import_batches (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NULL,
    dataset_type VARCHAR(50) NOT NULL,
    batch_name VARCHAR(255) NULL,
    source_system VARCHAR(100) NULL,
    source_file_name VARCHAR(255) NULL,
    row_count INTEGER NOT NULL DEFAULT 0,
    imported_by_user_id INTEGER NULL,
    imported_by_name VARCHAR(255) NULL,
    imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_analytics_import_batches_reference
    ON audit_analytics_import_batches(reference_id, dataset_type, imported_at DESC);

CREATE TABLE IF NOT EXISTS audit_gl_journal_entries (
    id BIGSERIAL PRIMARY KEY,
    import_batch_id INTEGER NULL REFERENCES audit_analytics_import_batches(id) ON DELETE SET NULL,
    reference_id INTEGER NULL,
    company_code VARCHAR(50) NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NULL,
    posting_date DATE NOT NULL,
    document_date DATE NULL,
    journal_number VARCHAR(100) NOT NULL,
    line_number INTEGER NOT NULL DEFAULT 1,
    account_number VARCHAR(100) NULL,
    account_name VARCHAR(255) NULL,
    fsli VARCHAR(255) NULL,
    business_unit VARCHAR(255) NULL,
    cost_center VARCHAR(100) NULL,
    user_id VARCHAR(100) NULL,
    user_name VARCHAR(255) NULL,
    description TEXT NULL,
    amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    debit_amount NUMERIC(18, 2) NULL,
    credit_amount NUMERIC(18, 2) NULL,
    currency_code VARCHAR(10) NULL,
    source_system VARCHAR(100) NULL,
    source_document_number VARCHAR(100) NULL,
    is_manual BOOLEAN NOT NULL DEFAULT FALSE,
    is_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_gl_journal_entries_reference_year
    ON audit_gl_journal_entries(reference_id, fiscal_year, fiscal_period);

CREATE INDEX IF NOT EXISTS idx_audit_gl_journal_entries_posting_date
    ON audit_gl_journal_entries(posting_date);

CREATE INDEX IF NOT EXISTS idx_audit_gl_journal_entries_user
    ON audit_gl_journal_entries(user_name, user_id);

CREATE TABLE IF NOT EXISTS audit_holiday_calendar (
    id SERIAL PRIMARY KEY,
    holiday_date DATE NOT NULL,
    holiday_name VARCHAR(255) NOT NULL,
    country_code VARCHAR(10) NULL,
    region_code VARCHAR(50) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (holiday_date, country_code, region_code)
);

CREATE INDEX IF NOT EXISTS idx_audit_holiday_calendar_date
    ON audit_holiday_calendar(holiday_date);

CREATE TABLE IF NOT EXISTS audit_trial_balance_snapshots (
    id BIGSERIAL PRIMARY KEY,
    import_batch_id INTEGER NULL REFERENCES audit_analytics_import_batches(id) ON DELETE SET NULL,
    reference_id INTEGER NULL,
    fiscal_year INTEGER NOT NULL,
    period_label VARCHAR(50) NULL,
    as_of_date DATE NULL,
    account_number VARCHAR(100) NOT NULL,
    account_name VARCHAR(255) NULL,
    fsli VARCHAR(255) NULL,
    business_unit VARCHAR(255) NULL,
    current_balance NUMERIC(18, 2) NOT NULL DEFAULT 0,
    currency_code VARCHAR(10) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_trial_balance_reference_year
    ON audit_trial_balance_snapshots(reference_id, fiscal_year);

CREATE INDEX IF NOT EXISTS idx_audit_trial_balance_account
    ON audit_trial_balance_snapshots(account_number, fiscal_year);

-- Seed a small holiday calendar for South African local testing.
INSERT INTO audit_holiday_calendar (holiday_date, holiday_name, country_code, region_code, is_active)
VALUES
    ('2025-01-01', 'New Year''s Day', 'ZA', 'ZA', TRUE),
    ('2025-03-21', 'Human Rights Day', 'ZA', 'ZA', TRUE),
    ('2025-04-18', 'Good Friday', 'ZA', 'ZA', TRUE),
    ('2025-04-21', 'Family Day', 'ZA', 'ZA', TRUE),
    ('2025-04-27', 'Freedom Day', 'ZA', 'ZA', TRUE),
    ('2025-05-01', 'Workers'' Day', 'ZA', 'ZA', TRUE),
    ('2025-06-16', 'Youth Day', 'ZA', 'ZA', TRUE),
    ('2025-08-09', 'National Women''s Day', 'ZA', 'ZA', TRUE),
    ('2025-09-24', 'Heritage Day', 'ZA', 'ZA', TRUE),
    ('2025-12-16', 'Day of Reconciliation', 'ZA', 'ZA', TRUE),
    ('2025-12-25', 'Christmas Day', 'ZA', 'ZA', TRUE),
    ('2025-12-26', 'Day of Goodwill', 'ZA', 'ZA', TRUE),
    ('2026-01-01', 'New Year''s Day', 'ZA', 'ZA', TRUE),
    ('2026-03-21', 'Human Rights Day', 'ZA', 'ZA', TRUE),
    ('2026-04-03', 'Good Friday', 'ZA', 'ZA', TRUE),
    ('2026-04-06', 'Family Day', 'ZA', 'ZA', TRUE),
    ('2026-04-27', 'Freedom Day', 'ZA', 'ZA', TRUE),
    ('2026-05-01', 'Workers'' Day', 'ZA', 'ZA', TRUE),
    ('2026-06-16', 'Youth Day', 'ZA', 'ZA', TRUE),
    ('2026-08-09', 'National Women''s Day', 'ZA', 'ZA', TRUE),
    ('2026-09-24', 'Heritage Day', 'ZA', 'ZA', TRUE),
    ('2026-12-16', 'Day of Reconciliation', 'ZA', 'ZA', TRUE),
    ('2026-12-25', 'Christmas Day', 'ZA', 'ZA', TRUE),
    ('2026-12-26', 'Day of Goodwill', 'ZA', 'ZA', TRUE)
ON CONFLICT (holiday_date, country_code, region_code) DO NOTHING;

CREATE TABLE IF NOT EXISTS audit_industry_benchmarks (
    id BIGSERIAL PRIMARY KEY,
    import_batch_id INTEGER NULL REFERENCES audit_analytics_import_batches(id) ON DELETE SET NULL,
    reference_id INTEGER NULL,
    fiscal_year INTEGER NOT NULL,
    industry_code VARCHAR(100) NULL,
    industry_name VARCHAR(255) NULL,
    metric_name VARCHAR(255) NOT NULL,
    unit_of_measure VARCHAR(50) NULL,
    company_value NUMERIC(18, 4) NOT NULL DEFAULT 0,
    benchmark_median NUMERIC(18, 4) NOT NULL DEFAULT 0,
    benchmark_lower_quartile NUMERIC(18, 4) NULL,
    benchmark_upper_quartile NUMERIC(18, 4) NULL,
    benchmark_source VARCHAR(255) NULL,
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_industry_benchmarks_reference_year
    ON audit_industry_benchmarks(reference_id, fiscal_year);

CREATE INDEX IF NOT EXISTS idx_audit_industry_benchmarks_metric
    ON audit_industry_benchmarks(metric_name, fiscal_year);

CREATE TABLE IF NOT EXISTS audit_reasonability_forecasts (
    id BIGSERIAL PRIMARY KEY,
    import_batch_id INTEGER NULL REFERENCES audit_analytics_import_batches(id) ON DELETE SET NULL,
    reference_id INTEGER NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_category VARCHAR(100) NULL,
    forecast_basis VARCHAR(100) NULL,
    actual_value NUMERIC(18, 2) NOT NULL DEFAULT 0,
    expected_value NUMERIC(18, 2) NOT NULL DEFAULT 0,
    budget_value NUMERIC(18, 2) NULL,
    prior_year_value NUMERIC(18, 2) NULL,
    threshold_amount NUMERIC(18, 2) NULL,
    threshold_percent NUMERIC(9, 2) NULL,
    explanation TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_reasonability_forecasts_reference_year
    ON audit_reasonability_forecasts(reference_id, fiscal_year, fiscal_period);

CREATE INDEX IF NOT EXISTS idx_audit_reasonability_forecasts_metric
    ON audit_reasonability_forecasts(metric_name, fiscal_year);
