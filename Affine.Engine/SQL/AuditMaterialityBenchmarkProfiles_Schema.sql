-- =====================================================
-- Audit Materiality Benchmark Profiles Extension
-- Purpose:
--   Persist benchmark profile defaults, explicit validation
--   state, entity or industry rationale context, and
--   approval history for active materiality decisions.
-- =====================================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS audit_materiality_benchmark_profiles (
    id SERIAL PRIMARY KEY,
    profile_code VARCHAR(100) NOT NULL UNIQUE,
    profile_name VARCHAR(255) NOT NULL,
    engagement_type_id INTEGER NULL REFERENCES ra_engagement_type(id) ON DELETE SET NULL,
    entity_type VARCHAR(150) NULL,
    industry_name VARCHAR(255) NULL,
    profit_before_tax_percentage NUMERIC(9, 4) NOT NULL DEFAULT 5,
    revenue_percentage NUMERIC(9, 4) NOT NULL DEFAULT 1,
    total_assets_percentage NUMERIC(9, 4) NOT NULL DEFAULT 1,
    expenses_percentage NUMERIC(9, 4) NOT NULL DEFAULT 1,
    performance_percentage NUMERIC(9, 4) NOT NULL DEFAULT 75,
    clearly_trivial_percentage NUMERIC(9, 4) NOT NULL DEFAULT 5,
    benchmark_rationale TEXT NULL,
    validation_status VARCHAR(100) NOT NULL DEFAULT 'Pending auditor confirmation',
    validation_notes TEXT NULL,
    approved_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    approved_by_name VARCHAR(255) NULL,
    approved_at TIMESTAMP NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 100,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_materiality_benchmark_profiles_active
    ON audit_materiality_benchmark_profiles(is_active, sort_order, profile_name);

ALTER TABLE audit_materiality_calculations
    ADD COLUMN IF NOT EXISTS benchmark_profile_id INTEGER NULL REFERENCES audit_materiality_benchmark_profiles(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS entity_type VARCHAR(150) NULL,
    ADD COLUMN IF NOT EXISTS industry_name VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS benchmark_selection_rationale TEXT NULL;

ALTER TABLE audit_materiality_candidates
    ADD COLUMN IF NOT EXISTS benchmark_profile_id INTEGER NULL REFERENCES audit_materiality_benchmark_profiles(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS entity_type VARCHAR(150) NULL,
    ADD COLUMN IF NOT EXISTS industry_name VARCHAR(255) NULL;

ALTER TABLE audit_engagement_plans
    ADD COLUMN IF NOT EXISTS materiality_benchmark_profile_id INTEGER NULL REFERENCES audit_materiality_benchmark_profiles(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS materiality_entity_type VARCHAR(150) NULL,
    ADD COLUMN IF NOT EXISTS materiality_industry_name VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS materiality_benchmark_selection_rationale TEXT NULL;

CREATE TABLE IF NOT EXISTS audit_materiality_approval_history (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    previous_calculation_id BIGINT NULL REFERENCES audit_materiality_calculations(id) ON DELETE SET NULL,
    calculation_id BIGINT NOT NULL REFERENCES audit_materiality_calculations(id) ON DELETE CASCADE,
    benchmark_profile_id INTEGER NULL REFERENCES audit_materiality_benchmark_profiles(id) ON DELETE SET NULL,
    action_type VARCHAR(100) NOT NULL DEFAULT 'activated',
    action_label VARCHAR(255) NULL,
    benchmark_code VARCHAR(100) NULL,
    benchmark_name VARCHAR(255) NULL,
    percentage_applied NUMERIC(9, 4) NOT NULL DEFAULT 0,
    performance_percentage_applied NUMERIC(9, 4) NOT NULL DEFAULT 0,
    clearly_trivial_percentage_applied NUMERIC(9, 4) NOT NULL DEFAULT 0,
    overall_materiality NUMERIC(18, 2) NOT NULL DEFAULT 0,
    performance_materiality NUMERIC(18, 2) NOT NULL DEFAULT 0,
    clearly_trivial_threshold NUMERIC(18, 2) NOT NULL DEFAULT 0,
    entity_type VARCHAR(150) NULL,
    industry_name VARCHAR(255) NULL,
    benchmark_selection_rationale TEXT NULL,
    override_reason TEXT NULL,
    approved_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    approved_by_name VARCHAR(255) NULL,
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_materiality_approval_history_reference
    ON audit_materiality_approval_history(reference_id, created_at DESC);

CREATE OR REPLACE FUNCTION update_audit_materiality_benchmark_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_materiality_benchmark_profiles_updated_at ON audit_materiality_benchmark_profiles;
CREATE TRIGGER trigger_update_audit_materiality_benchmark_profiles_updated_at
    BEFORE UPDATE ON audit_materiality_benchmark_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_materiality_benchmark_profiles_updated_at();

INSERT INTO audit_materiality_benchmark_profiles
(
    profile_code,
    profile_name,
    entity_type,
    profit_before_tax_percentage,
    revenue_percentage,
    total_assets_percentage,
    expenses_percentage,
    performance_percentage,
    clearly_trivial_percentage,
    benchmark_rationale,
    validation_status,
    validation_notes,
    is_default,
    sort_order,
    is_active
)
SELECT
    'general_external_baseline',
    'General External Audit Baseline',
    'General',
    5,
    1,
    1,
    1,
    75,
    5,
    'Baseline working profile while client or auditor-specific materiality rules are being confirmed.',
    'Pending auditor confirmation',
    'The March 10, 2026 demo notes confirmed the benchmark types in scope, but exact percentages still require auditor confirmation before this profile can be treated as validated.',
    TRUE,
    10,
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM audit_materiality_benchmark_profiles
    WHERE profile_code = 'general_external_baseline'
);
