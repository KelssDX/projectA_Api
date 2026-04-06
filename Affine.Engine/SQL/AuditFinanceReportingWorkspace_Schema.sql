-- =====================================================
-- Audit Finance Reporting Workspace Extension
-- Purpose:
--   Add trial-balance mapping, reusable mapping profiles,
--   draft financial statements, substantive support queues,
--   finance finalization capture, and finance-package
--   separation for future domain extensions.
-- =====================================================

SET search_path TO "Risk_Assess_Framework";

CREATE TABLE IF NOT EXISTS audit_domain_rule_packages (
    id SERIAL PRIMARY KEY,
    package_code VARCHAR(100) NOT NULL UNIQUE,
    package_name VARCHAR(255) NOT NULL,
    domain_code VARCHAR(100) NOT NULL,
    description TEXT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_financial_statement_mapping_profiles (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER NULL REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    engagement_type_id INTEGER NULL REFERENCES ra_engagement_type(id) ON DELETE SET NULL,
    rule_package_id INTEGER NULL REFERENCES audit_domain_rule_packages(id) ON DELETE SET NULL,
    profile_code VARCHAR(150) NOT NULL UNIQUE,
    profile_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(150) NULL,
    industry_name VARCHAR(255) NULL,
    notes TEXT NULL,
    is_reusable BOOLEAN NOT NULL DEFAULT FALSE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    created_by_name VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_financial_statement_profile_rules (
    id BIGSERIAL PRIMARY KEY,
    mapping_profile_id INTEGER NOT NULL REFERENCES audit_financial_statement_mapping_profiles(id) ON DELETE CASCADE,
    account_number VARCHAR(100) NOT NULL,
    account_name VARCHAR(255) NULL,
    fsli VARCHAR(255) NULL,
    statement_type VARCHAR(100) NOT NULL,
    section_name VARCHAR(255) NOT NULL,
    line_name VARCHAR(255) NOT NULL,
    classification VARCHAR(100) NULL,
    display_order INTEGER NOT NULL DEFAULT 100,
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_audit_fs_profile_rule UNIQUE (mapping_profile_id, account_number)
);

CREATE TABLE IF NOT EXISTS audit_financial_statement_mappings (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    fiscal_year INTEGER NOT NULL,
    mapping_profile_id INTEGER NULL REFERENCES audit_financial_statement_mapping_profiles(id) ON DELETE SET NULL,
    account_number VARCHAR(100) NOT NULL,
    account_name VARCHAR(255) NULL,
    fsli VARCHAR(255) NULL,
    business_unit VARCHAR(255) NULL,
    current_balance NUMERIC(18, 2) NOT NULL DEFAULT 0,
    statement_type VARCHAR(100) NULL,
    section_name VARCHAR(255) NULL,
    line_name VARCHAR(255) NULL,
    classification VARCHAR(100) NULL,
    display_order INTEGER NOT NULL DEFAULT 100,
    notes TEXT NULL,
    is_auto_mapped BOOLEAN NOT NULL DEFAULT TRUE,
    is_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_audit_fs_mapping UNIQUE (reference_id, fiscal_year, account_number)
);

CREATE TABLE IF NOT EXISTS audit_finance_finalization (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL UNIQUE REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    active_mapping_profile_id INTEGER NULL REFERENCES audit_financial_statement_mapping_profiles(id) ON DELETE SET NULL,
    active_rule_package_id INTEGER NULL REFERENCES audit_domain_rule_packages(id) ON DELETE SET NULL,
    overall_conclusion TEXT NULL,
    recommendation_summary TEXT NULL,
    release_readiness_status VARCHAR(100) NOT NULL DEFAULT 'In Preparation',
    draft_statement_status VARCHAR(100) NOT NULL DEFAULT 'Not Generated',
    outstanding_items TEXT NULL,
    reviewer_notes TEXT NULL,
    ready_for_release BOOLEAN NOT NULL DEFAULT FALSE,
    last_generated_statement_year INTEGER NULL,
    last_generated_at TIMESTAMP NULL,
    updated_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    updated_by_name VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_substantive_support_requests (
    id BIGSERIAL PRIMARY KEY,
    reference_id INTEGER NOT NULL REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    fiscal_year INTEGER NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_record_id BIGINT NULL,
    source_key VARCHAR(255) NOT NULL,
    transaction_identifier VARCHAR(255) NOT NULL,
    journal_number VARCHAR(100) NULL,
    posting_date DATE NULL,
    account_number VARCHAR(100) NULL,
    account_name VARCHAR(255) NULL,
    fsli VARCHAR(255) NULL,
    amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    description TEXT NULL,
    triage_reason VARCHAR(255) NOT NULL,
    risk_flags TEXT NULL,
    support_status VARCHAR(100) NOT NULL DEFAULT 'Requested',
    support_summary TEXT NULL,
    linked_procedure_id INTEGER NULL REFERENCES audit_procedures(id) ON DELETE SET NULL,
    linked_walkthrough_id INTEGER NULL REFERENCES audit_walkthroughs(id) ON DELETE SET NULL,
    linked_control_id INTEGER NULL REFERENCES audit_risk_control_matrix(id) ON DELETE SET NULL,
    linked_finding_id INTEGER NULL REFERENCES audit_findings(id) ON DELETE SET NULL,
    notes TEXT NULL,
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_audit_support_request UNIQUE (reference_id, source_key, triage_reason)
);

CREATE INDEX IF NOT EXISTS idx_audit_fs_profiles_reference
    ON audit_financial_statement_mapping_profiles(reference_id, is_active, is_default);

CREATE INDEX IF NOT EXISTS idx_audit_fs_mappings_reference
    ON audit_financial_statement_mappings(reference_id, fiscal_year, statement_type, section_name, display_order);

CREATE INDEX IF NOT EXISTS idx_audit_support_requests_reference
    ON audit_substantive_support_requests(reference_id, fiscal_year, support_status, requested_at DESC);

CREATE OR REPLACE FUNCTION update_audit_domain_rule_packages_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_audit_fs_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_audit_fs_profile_rules_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_audit_fs_mappings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_audit_finance_finalization_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_audit_support_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_audit_domain_rule_packages_updated_at ON audit_domain_rule_packages;
CREATE TRIGGER trigger_update_audit_domain_rule_packages_updated_at
    BEFORE UPDATE ON audit_domain_rule_packages
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_domain_rule_packages_updated_at();

DROP TRIGGER IF EXISTS trigger_update_audit_fs_profiles_updated_at ON audit_financial_statement_mapping_profiles;
CREATE TRIGGER trigger_update_audit_fs_profiles_updated_at
    BEFORE UPDATE ON audit_financial_statement_mapping_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_fs_profiles_updated_at();

DROP TRIGGER IF EXISTS trigger_update_audit_fs_profile_rules_updated_at ON audit_financial_statement_profile_rules;
CREATE TRIGGER trigger_update_audit_fs_profile_rules_updated_at
    BEFORE UPDATE ON audit_financial_statement_profile_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_fs_profile_rules_updated_at();

DROP TRIGGER IF EXISTS trigger_update_audit_fs_mappings_updated_at ON audit_financial_statement_mappings;
CREATE TRIGGER trigger_update_audit_fs_mappings_updated_at
    BEFORE UPDATE ON audit_financial_statement_mappings
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_fs_mappings_updated_at();

DROP TRIGGER IF EXISTS trigger_update_audit_finance_finalization_updated_at ON audit_finance_finalization;
CREATE TRIGGER trigger_update_audit_finance_finalization_updated_at
    BEFORE UPDATE ON audit_finance_finalization
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_finance_finalization_updated_at();

DROP TRIGGER IF EXISTS trigger_update_audit_support_requests_updated_at ON audit_substantive_support_requests;
CREATE TRIGGER trigger_update_audit_support_requests_updated_at
    BEFORE UPDATE ON audit_substantive_support_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_support_requests_updated_at();

INSERT INTO audit_domain_rule_packages
(
    package_code,
    package_name,
    domain_code,
    description,
    is_default,
    is_active
)
SELECT
    'finance_audit_core',
    'Finance Audit Core',
    'finance',
    'Default finance-audit mapping, triage, and finalization package kept separate from future IT-audit or domain extensions.',
    TRUE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM audit_domain_rule_packages
    WHERE package_code = 'finance_audit_core'
);

INSERT INTO audit_domain_rule_packages
(
    package_code,
    package_name,
    domain_code,
    description,
    is_default,
    is_active
)
SELECT
    'future_domain_extension_placeholder',
    'Future Domain Extension Placeholder',
    'extension',
    'Placeholder package so finance-audit defaults remain explicitly separated from future domain-specific extensions.',
    FALSE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM audit_domain_rule_packages
    WHERE package_code = 'future_domain_extension_placeholder'
);

INSERT INTO audit_financial_statement_mapping_profiles
(
    reference_id,
    rule_package_id,
    profile_code,
    profile_name,
    notes,
    is_reusable,
    is_default,
    is_active
)
SELECT
    NULL,
    pkg.id,
    'finance_core_default_mapping',
    'Finance Core Default Mapping',
    'Reusable starter profile for finance-audit trial balance mapping. Apply it to engagements and refine the rules from imported account structures.',
    TRUE,
    TRUE,
    TRUE
FROM audit_domain_rule_packages pkg
WHERE pkg.package_code = 'finance_audit_core'
  AND NOT EXISTS (
      SELECT 1
      FROM audit_financial_statement_mapping_profiles
      WHERE profile_code = 'finance_core_default_mapping'
  );
