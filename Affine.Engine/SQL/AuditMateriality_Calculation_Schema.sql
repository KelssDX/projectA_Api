-- =====================================================
-- Audit Materiality Calculation Extension
-- Purpose:
--   Add data-driven materiality candidate generation,
--   calculation history, active selection, and downstream
--   scaffolding for scope links and misstatement analysis.
-- =====================================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS audit_materiality_calculations (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    fiscal_year INTEGER NULL,
    candidate_id BIGINT NULL,
    benchmark_code VARCHAR(100) NOT NULL,
    benchmark_name VARCHAR(255) NOT NULL,
    benchmark_source VARCHAR(100) NOT NULL DEFAULT 'trial_balance',
    source_table VARCHAR(100) NULL,
    benchmark_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    percentage_applied NUMERIC(9, 4) NOT NULL DEFAULT 0,
    overall_materiality NUMERIC(18, 2) NOT NULL DEFAULT 0,
    performance_percentage_applied NUMERIC(9, 4) NOT NULL DEFAULT 75,
    performance_materiality NUMERIC(18, 2) NOT NULL DEFAULT 0,
    clearly_trivial_percentage_applied NUMERIC(9, 4) NOT NULL DEFAULT 5,
    clearly_trivial_threshold NUMERIC(18, 2) NOT NULL DEFAULT 0,
    calculation_summary VARCHAR(500) NULL,
    rationale TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    is_manual_override BOOLEAN NOT NULL DEFAULT FALSE,
    approved_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    approved_by_name VARCHAR(255) NULL,
    approved_at TIMESTAMP NULL,
    created_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    created_by_name VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_materiality_calculations_reference_id
    ON audit_materiality_calculations(reference_id, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_materiality_calculations_active_reference
    ON audit_materiality_calculations(reference_id)
    WHERE is_active = TRUE;

CREATE TABLE IF NOT EXISTS audit_materiality_candidates (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    fiscal_year INTEGER NULL,
    candidate_code VARCHAR(100) NOT NULL,
    candidate_name VARCHAR(255) NOT NULL,
    benchmark_source VARCHAR(100) NOT NULL DEFAULT 'trial_balance',
    source_table VARCHAR(100) NULL,
    source_metric_label VARCHAR(255) NULL,
    benchmark_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    recommended_percentage NUMERIC(9, 4) NOT NULL DEFAULT 0,
    recommended_overall_materiality NUMERIC(18, 2) NOT NULL DEFAULT 0,
    recommended_performance_percentage NUMERIC(9, 4) NOT NULL DEFAULT 75,
    recommended_performance_materiality NUMERIC(18, 2) NOT NULL DEFAULT 0,
    recommended_clearly_trivial_percentage NUMERIC(9, 4) NOT NULL DEFAULT 5,
    recommended_clearly_trivial_threshold NUMERIC(18, 2) NOT NULL DEFAULT 0,
    notes TEXT NULL,
    is_selected BOOLEAN NOT NULL DEFAULT FALSE,
    selected_calculation_id BIGINT NULL,
    generated_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    generated_by_name VARCHAR(255) NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_materiality_candidates_reference_id
    ON audit_materiality_candidates(reference_id, generated_at DESC);

CREATE TABLE IF NOT EXISTS audit_misstatements (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    finding_id INTEGER NULL REFERENCES audit_findings(id) ON DELETE SET NULL,
    materiality_calculation_id BIGINT NULL REFERENCES audit_materiality_calculations(id) ON DELETE SET NULL,
    fsli VARCHAR(255) NULL,
    account_number VARCHAR(100) NULL,
    transaction_identifier VARCHAR(255) NULL,
    description TEXT NOT NULL,
    actual_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    projected_amount NUMERIC(18, 2) NULL,
    evaluation_basis VARCHAR(100) NULL,
    exceeds_clearly_trivial BOOLEAN NOT NULL DEFAULT FALSE,
    exceeds_performance_materiality BOOLEAN NOT NULL DEFAULT FALSE,
    exceeds_overall_materiality BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(100) NOT NULL DEFAULT 'Open',
    created_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    created_by_name VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_misstatements_reference_id
    ON audit_misstatements(reference_id, created_at DESC);

CREATE TABLE IF NOT EXISTS audit_materiality_scope_links (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    materiality_calculation_id BIGINT NOT NULL REFERENCES audit_materiality_calculations(id) ON DELETE CASCADE,
    scope_item_id INTEGER NULL REFERENCES audit_scope_items(id) ON DELETE CASCADE,
    fsli VARCHAR(255) NULL,
    benchmark_relevance VARCHAR(255) NULL,
    inclusion_reason TEXT NULL,
    is_above_threshold BOOLEAN NOT NULL DEFAULT FALSE,
    coverage_percent NUMERIC(9, 2) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_materiality_scope_links_reference_id
    ON audit_materiality_scope_links(reference_id, materiality_calculation_id);

ALTER TABLE audit_engagement_plans
    ADD COLUMN IF NOT EXISTS materiality_source VARCHAR(50) NOT NULL DEFAULT 'Manual',
    ADD COLUMN IF NOT EXISTS active_materiality_calculation_id BIGINT NULL REFERENCES audit_materiality_calculations(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS materiality_last_calculated_at TIMESTAMP NULL,
    ADD COLUMN IF NOT EXISTS materiality_override_reason TEXT NULL,
    ADD COLUMN IF NOT EXISTS selected_materiality_benchmark VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS selected_materiality_benchmark_amount NUMERIC(18, 2) NULL,
    ADD COLUMN IF NOT EXISTS selected_materiality_benchmark_percentage NUMERIC(9, 4) NULL;

ALTER TABLE audit_scope_items
    ADD COLUMN IF NOT EXISTS materiality_relevance VARCHAR(100) NULL,
    ADD COLUMN IF NOT EXISTS materiality_notes TEXT NULL;

CREATE OR REPLACE FUNCTION update_audit_materiality_calculations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_materiality_calculations_updated_at ON audit_materiality_calculations;
CREATE TRIGGER trigger_update_audit_materiality_calculations_updated_at
    BEFORE UPDATE ON audit_materiality_calculations
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_materiality_calculations_updated_at();

CREATE OR REPLACE FUNCTION update_audit_misstatements_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_misstatements_updated_at ON audit_misstatements;
CREATE TRIGGER trigger_update_audit_misstatements_updated_at
    BEFORE UPDATE ON audit_misstatements
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_misstatements_updated_at();
