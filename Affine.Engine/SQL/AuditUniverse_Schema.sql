-- ===============================================
-- AUDIT UNIVERSE & FINDINGS SCHEMA
-- ===============================================
-- This script creates the audit universe hierarchy, findings,
-- recommendations, and coverage tracking tables.
--
-- Schema: Risk_Assess_Framework
-- Author: Enterprise Audit Analytics Platform
-- Date: 2026-01-18
-- ===============================================

SET search_path TO "Risk_Assess_Framework";

-- ===============================================
-- SECTION 1: AUDIT UNIVERSE HIERARCHY
-- ===============================================

-- 1. AUDIT UNIVERSE TABLE
-- Hierarchical structure for auditable entities (Entity > Division > Process > Sub-Process)
CREATE TABLE IF NOT EXISTS audit_universe (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES audit_universe(id) ON DELETE SET NULL,
    level INTEGER NOT NULL DEFAULT 1, -- 1=Entity, 2=Division, 3=Process, 4=Sub-Process
    level_name VARCHAR(100), -- e.g., "Entity", "Division", "Business Process"
    description TEXT,
    risk_rating VARCHAR(20) DEFAULT 'Medium', -- High, Medium, Low
    last_audit_date DATE,
    next_audit_date DATE,
    audit_frequency_months INTEGER DEFAULT 12,
    owner VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_universe IS 'Hierarchical structure of all auditable entities in the organization';
COMMENT ON COLUMN audit_universe.level IS '1=Entity, 2=Division, 3=Process, 4=Sub-Process';
COMMENT ON COLUMN audit_universe.level_name IS 'Human-readable name for this level in the hierarchy';
COMMENT ON COLUMN audit_universe.audit_frequency_months IS 'How often this entity should be audited';

-- 2. AUDIT UNIVERSE LEVEL NAMES LOOKUP
CREATE TABLE IF NOT EXISTS ra_audit_universe_levels (
    id SERIAL PRIMARY KEY,
    level INTEGER NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50), -- Icon identifier for frontend display
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_audit_universe_levels (level, name, description, icon, sort_order) VALUES
(1, 'Entity', 'Top-level organizational entity (e.g., Corporation, Business Unit)', 'building', 1),
(2, 'Division', 'Division or department within an entity', 'sitemap', 2),
(3, 'Process', 'Business process within a division', 'cogs', 3),
(4, 'Sub-Process', 'Detailed sub-process or activity', 'tasks', 4)
ON CONFLICT (level) DO NOTHING;

-- 3. AUDIT UNIVERSE - DEPARTMENT LINK TABLE
-- Links audit universe nodes to departments for risk assessment integration
CREATE TABLE IF NOT EXISTS audit_universe_department_link (
    id SERIAL PRIMARY KEY,
    audit_universe_id INTEGER NOT NULL REFERENCES audit_universe(id) ON DELETE CASCADE,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(audit_universe_id, department_id)
);

COMMENT ON TABLE audit_universe_department_link IS 'Links audit universe nodes to departments for integrated risk tracking';

-- ===============================================
-- SECTION 2: AUDIT FINDINGS
-- ===============================================

-- 4. FINDING SEVERITY LOOKUP
CREATE TABLE IF NOT EXISTS ra_finding_severity (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20), -- Hex color for UI display
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_finding_severity (name, description, color, sort_order) VALUES
('Critical', 'Requires immediate attention and resolution', '#DC2626', 1),
('High', 'Significant issue requiring prompt action', '#EA580C', 2),
('Medium', 'Moderate issue requiring timely attention', '#CA8A04', 3),
('Low', 'Minor issue for planned resolution', '#16A34A', 4)
ON CONFLICT (name) DO NOTHING;

-- 5. FINDING STATUS LOOKUP
CREATE TABLE IF NOT EXISTS ra_finding_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    is_closed BOOLEAN DEFAULT FALSE, -- Whether this status means the finding is closed
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_finding_status (name, description, color, is_closed, sort_order) VALUES
('Open', 'Finding has been identified and is awaiting action', '#3B82F6', FALSE, 1),
('In Progress', 'Remediation activities are underway', '#8B5CF6', FALSE, 2),
('Pending Verification', 'Remediation complete, awaiting verification', '#F59E0B', FALSE, 3),
('Closed', 'Finding has been fully remediated and verified', '#10B981', TRUE, 4),
('Overdue', 'Finding has exceeded its due date without closure', '#EF4444', FALSE, 5),
('Accepted', 'Risk accepted by management without remediation', '#6B7280', TRUE, 6)
ON CONFLICT (name) DO NOTHING;

-- 6. AUDIT FINDINGS TABLE
CREATE TABLE IF NOT EXISTS audit_findings (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE SET NULL,
    audit_universe_id INTEGER REFERENCES audit_universe(id) ON DELETE SET NULL,
    finding_number VARCHAR(50) UNIQUE, -- Auto-generated finding number (e.g., FND-2026-001)
    finding_title VARCHAR(500) NOT NULL,
    finding_description TEXT,
    severity_id INTEGER REFERENCES ra_finding_severity(id) DEFAULT 3, -- Default Medium
    status_id INTEGER REFERENCES ra_finding_status(id) DEFAULT 1, -- Default Open
    identified_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    closed_date DATE,
    assigned_to VARCHAR(255),
    assigned_to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    root_cause TEXT,
    business_impact TEXT,
    created_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_findings IS 'Audit findings identified during risk assessments';
COMMENT ON COLUMN audit_findings.finding_number IS 'Auto-generated unique finding identifier';
COMMENT ON COLUMN audit_findings.root_cause IS 'Root cause analysis of the finding';
COMMENT ON COLUMN audit_findings.business_impact IS 'Description of the business impact if unaddressed';

-- 7. AUTO-GENERATE FINDING NUMBER
CREATE OR REPLACE FUNCTION generate_finding_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.finding_number IS NULL THEN
        NEW.finding_number := 'FND-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                             LPAD(nextval('audit_findings_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_generate_finding_number ON audit_findings;
CREATE TRIGGER trigger_generate_finding_number
    BEFORE INSERT ON audit_findings
    FOR EACH ROW
    EXECUTE FUNCTION generate_finding_number();

-- ===============================================
-- SECTION 3: AUDIT RECOMMENDATIONS
-- ===============================================

-- 8. RECOMMENDATION STATUS LOOKUP
CREATE TABLE IF NOT EXISTS ra_recommendation_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ra_recommendation_status (name, description, color, sort_order) VALUES
('Pending', 'Recommendation awaiting management response', '#6B7280', 1),
('Agreed', 'Management has agreed to implement', '#3B82F6', 2),
('In Progress', 'Implementation is underway', '#8B5CF6', 3),
('Implemented', 'Recommendation has been fully implemented', '#10B981', 4),
('Rejected', 'Management has rejected the recommendation', '#EF4444', 5),
('Deferred', 'Implementation has been deferred', '#F59E0B', 6)
ON CONFLICT (name) DO NOTHING;

-- 9. AUDIT RECOMMENDATIONS TABLE
CREATE TABLE IF NOT EXISTS audit_recommendations (
    id SERIAL PRIMARY KEY,
    finding_id INTEGER NOT NULL REFERENCES audit_findings(id) ON DELETE CASCADE,
    recommendation_number VARCHAR(50) UNIQUE, -- Auto-generated (e.g., REC-2026-001)
    recommendation TEXT NOT NULL,
    priority INTEGER DEFAULT 2, -- 1=High, 2=Medium, 3=Low
    management_response TEXT,
    agreed_date DATE,
    target_date DATE,
    implementation_date DATE,
    responsible_person VARCHAR(255),
    responsible_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status_id INTEGER REFERENCES ra_recommendation_status(id) DEFAULT 1, -- Default Pending
    verification_notes TEXT,
    verified_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_recommendations IS 'Recommendations/action plans for audit findings';
COMMENT ON COLUMN audit_recommendations.priority IS '1=High, 2=Medium, 3=Low priority';

-- 10. AUTO-GENERATE RECOMMENDATION NUMBER
CREATE OR REPLACE FUNCTION generate_recommendation_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.recommendation_number IS NULL THEN
        NEW.recommendation_number := 'REC-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                                    LPAD(nextval('audit_recommendations_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_generate_recommendation_number ON audit_recommendations;
CREATE TRIGGER trigger_generate_recommendation_number
    BEFORE INSERT ON audit_recommendations
    FOR EACH ROW
    EXECUTE FUNCTION generate_recommendation_number();

-- ===============================================
-- SECTION 4: AUDIT COVERAGE TRACKING
-- ===============================================

-- 11. AUDIT COVERAGE TABLE
CREATE TABLE IF NOT EXISTS audit_coverage (
    id SERIAL PRIMARY KEY,
    audit_universe_id INTEGER NOT NULL REFERENCES audit_universe(id) ON DELETE CASCADE,
    period_year INTEGER NOT NULL,
    period_quarter INTEGER, -- 1-4 or NULL for annual
    planned_audits INTEGER DEFAULT 0,
    completed_audits INTEGER DEFAULT 0,
    coverage_percentage DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN planned_audits > 0
             THEN ROUND((completed_audits::DECIMAL / planned_audits * 100), 2)
             ELSE 0
        END
    ) STORED,
    total_findings INTEGER DEFAULT 0,
    critical_findings INTEGER DEFAULT 0,
    high_findings INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(audit_universe_id, period_year, period_quarter)
);

COMMENT ON TABLE audit_coverage IS 'Tracks audit coverage by universe node and time period';
COMMENT ON COLUMN audit_coverage.coverage_percentage IS 'Auto-calculated coverage percentage';

-- ===============================================
-- SECTION 5: RISK TREND HISTORY
-- ===============================================

-- 12. RISK TREND HISTORY TABLE
-- Captures periodic snapshots of risk levels for trend analysis
CREATE TABLE IF NOT EXISTS risk_trend_history (
    id SERIAL PRIMARY KEY,
    reference_id INTEGER REFERENCES riskassessmentreference(reference_id) ON DELETE CASCADE,
    audit_universe_id INTEGER REFERENCES audit_universe(id) ON DELETE SET NULL,
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    period_type VARCHAR(20) DEFAULT 'monthly', -- daily, weekly, monthly, quarterly
    critical_count INTEGER DEFAULT 0,
    high_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    low_count INTEGER DEFAULT 0,
    very_low_count INTEGER DEFAULT 0,
    total_inherent_score DECIMAL(10,2) DEFAULT 0,
    total_residual_score DECIMAL(10,2) DEFAULT 0,
    assessment_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(reference_id, snapshot_date, period_type)
);

COMMENT ON TABLE risk_trend_history IS 'Historical snapshots of risk levels for trend analysis';

-- ===============================================
-- SECTION 6: INDEXES FOR PERFORMANCE
-- ===============================================

-- Audit Universe indexes
CREATE INDEX IF NOT EXISTS idx_audit_universe_parent_id ON audit_universe(parent_id);
CREATE INDEX IF NOT EXISTS idx_audit_universe_level ON audit_universe(level);
CREATE INDEX IF NOT EXISTS idx_audit_universe_risk_rating ON audit_universe(risk_rating);
CREATE INDEX IF NOT EXISTS idx_audit_universe_is_active ON audit_universe(is_active);
CREATE INDEX IF NOT EXISTS idx_audit_universe_code ON audit_universe(code);
CREATE INDEX IF NOT EXISTS idx_audit_universe_next_audit ON audit_universe(next_audit_date);

-- Audit Universe Department Link indexes
CREATE INDEX IF NOT EXISTS idx_audit_universe_dept_link_universe ON audit_universe_department_link(audit_universe_id);
CREATE INDEX IF NOT EXISTS idx_audit_universe_dept_link_dept ON audit_universe_department_link(department_id);

-- Audit Findings indexes
CREATE INDEX IF NOT EXISTS idx_audit_findings_reference ON audit_findings(reference_id);
CREATE INDEX IF NOT EXISTS idx_audit_findings_universe ON audit_findings(audit_universe_id);
CREATE INDEX IF NOT EXISTS idx_audit_findings_severity ON audit_findings(severity_id);
CREATE INDEX IF NOT EXISTS idx_audit_findings_status ON audit_findings(status_id);
CREATE INDEX IF NOT EXISTS idx_audit_findings_due_date ON audit_findings(due_date);
CREATE INDEX IF NOT EXISTS idx_audit_findings_identified_date ON audit_findings(identified_date);
CREATE INDEX IF NOT EXISTS idx_audit_findings_assigned_to ON audit_findings(assigned_to_user_id);

-- Audit Recommendations indexes
CREATE INDEX IF NOT EXISTS idx_audit_recommendations_finding ON audit_recommendations(finding_id);
CREATE INDEX IF NOT EXISTS idx_audit_recommendations_status ON audit_recommendations(status_id);
CREATE INDEX IF NOT EXISTS idx_audit_recommendations_target_date ON audit_recommendations(target_date);
CREATE INDEX IF NOT EXISTS idx_audit_recommendations_responsible ON audit_recommendations(responsible_user_id);

-- Audit Coverage indexes
CREATE INDEX IF NOT EXISTS idx_audit_coverage_universe ON audit_coverage(audit_universe_id);
CREATE INDEX IF NOT EXISTS idx_audit_coverage_period ON audit_coverage(period_year, period_quarter);

-- Risk Trend History indexes
CREATE INDEX IF NOT EXISTS idx_risk_trend_reference ON risk_trend_history(reference_id);
CREATE INDEX IF NOT EXISTS idx_risk_trend_date ON risk_trend_history(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_risk_trend_universe ON risk_trend_history(audit_universe_id);

-- ===============================================
-- SECTION 7: TRIGGERS FOR AUTOMATIC UPDATES
-- ===============================================

-- Apply updated_at triggers
CREATE TRIGGER IF NOT EXISTS update_audit_universe_updated_at
    BEFORE UPDATE ON audit_universe
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_audit_findings_updated_at
    BEFORE UPDATE ON audit_findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_audit_recommendations_updated_at
    BEFORE UPDATE ON audit_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_audit_coverage_updated_at
    BEFORE UPDATE ON audit_coverage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===============================================
-- SECTION 8: SAMPLE/SEED DATA
-- ===============================================

-- Insert sample audit universe hierarchy
INSERT INTO audit_universe (name, code, parent_id, level, level_name, description, risk_rating, owner, audit_frequency_months) VALUES
-- Level 1: Entities
('Corporate Headquarters', 'CORP-HQ', NULL, 1, 'Entity', 'Main corporate entity', 'High', 'CEO', 12),
('Regional Operations', 'REG-OPS', NULL, 1, 'Entity', 'Regional business operations', 'Medium', 'COO', 12)
ON CONFLICT (code) DO NOTHING;

-- Get IDs for parent references
DO $$
DECLARE
    corp_id INTEGER;
    reg_id INTEGER;
    finance_id INTEGER;
    it_id INTEGER;
    ops_id INTEGER;
BEGIN
    SELECT id INTO corp_id FROM audit_universe WHERE code = 'CORP-HQ';
    SELECT id INTO reg_id FROM audit_universe WHERE code = 'REG-OPS';

    -- Level 2: Divisions
    INSERT INTO audit_universe (name, code, parent_id, level, level_name, description, risk_rating, owner, audit_frequency_months) VALUES
    ('Finance Division', 'FIN-DIV', corp_id, 2, 'Division', 'Corporate finance and accounting', 'High', 'CFO', 6),
    ('Information Technology', 'IT-DIV', corp_id, 2, 'Division', 'IT infrastructure and systems', 'High', 'CIO', 6),
    ('Operations Division', 'OPS-DIV', reg_id, 2, 'Division', 'Manufacturing and logistics', 'Medium', 'VP Operations', 12),
    ('Human Resources', 'HR-DIV', corp_id, 2, 'Division', 'HR and talent management', 'Low', 'CHRO', 12)
    ON CONFLICT (code) DO NOTHING;

    SELECT id INTO finance_id FROM audit_universe WHERE code = 'FIN-DIV';
    SELECT id INTO it_id FROM audit_universe WHERE code = 'IT-DIV';
    SELECT id INTO ops_id FROM audit_universe WHERE code = 'OPS-DIV';

    -- Level 3: Processes
    INSERT INTO audit_universe (name, code, parent_id, level, level_name, description, risk_rating, owner, audit_frequency_months) VALUES
    ('Financial Reporting', 'FIN-REP', finance_id, 3, 'Process', 'Financial statement preparation and reporting', 'High', 'Controller', 3),
    ('Accounts Payable', 'FIN-AP', finance_id, 3, 'Process', 'Vendor payment processing', 'Medium', 'AP Manager', 6),
    ('Treasury Management', 'FIN-TRS', finance_id, 3, 'Process', 'Cash management and investments', 'High', 'Treasurer', 6),
    ('Cybersecurity', 'IT-SEC', it_id, 3, 'Process', 'Information security management', 'Critical', 'CISO', 3),
    ('IT Change Management', 'IT-CHG', it_id, 3, 'Process', 'System change control', 'High', 'IT Manager', 6),
    ('Data Management', 'IT-DAT', it_id, 3, 'Process', 'Data governance and quality', 'Medium', 'Data Officer', 12),
    ('Supply Chain', 'OPS-SCM', ops_id, 3, 'Process', 'Procurement and supply chain', 'Medium', 'SCM Director', 12),
    ('Quality Assurance', 'OPS-QA', ops_id, 3, 'Process', 'Product quality control', 'High', 'QA Manager', 6)
    ON CONFLICT (code) DO NOTHING;

END $$;

-- Insert sample findings
INSERT INTO audit_findings (finding_title, finding_description, severity_id, status_id, identified_date, due_date, root_cause, business_impact) VALUES
('Inadequate Access Control Review', 'User access rights are not reviewed periodically as required by policy', 1, 1, '2026-01-10', '2026-02-28', 'Lack of automated access review process', 'Potential unauthorized access to sensitive data'),
('Missing Segregation of Duties', 'Same individual can create and approve purchase orders', 2, 2, '2025-12-15', '2026-01-31', 'System configuration does not enforce SoD', 'Risk of fraudulent transactions'),
('Incomplete Backup Testing', 'Disaster recovery backups have not been tested in 18 months', 2, 1, '2026-01-05', '2026-03-15', 'No scheduled DR testing program', 'Extended downtime risk in case of disaster'),
('Outdated Security Patches', 'Critical servers missing security patches older than 90 days', 1, 2, '2025-11-20', '2026-01-15', 'Manual patching process with no tracking', 'Vulnerability to known exploits')
ON CONFLICT DO NOTHING;

-- Insert sample recommendations for findings
INSERT INTO audit_recommendations (finding_id, recommendation, priority, management_response, status_id)
SELECT
    f.id,
    'Implement automated quarterly access review process using identity management system',
    1,
    'Agreed. Will implement using existing IAM tool.',
    2
FROM audit_findings f WHERE f.finding_title = 'Inadequate Access Control Review'
ON CONFLICT DO NOTHING;

INSERT INTO audit_recommendations (finding_id, recommendation, priority, management_response, status_id)
SELECT
    f.id,
    'Configure system to enforce segregation of duties with dual approval workflow',
    1,
    NULL,
    1
FROM audit_findings f WHERE f.finding_title = 'Missing Segregation of Duties'
ON CONFLICT DO NOTHING;

-- Insert sample audit coverage data
INSERT INTO audit_coverage (audit_universe_id, period_year, period_quarter, planned_audits, completed_audits, total_findings, critical_findings, high_findings)
SELECT id, 2025, 4, 4, 3, 12, 2, 5 FROM audit_universe WHERE code = 'FIN-DIV'
ON CONFLICT DO NOTHING;

INSERT INTO audit_coverage (audit_universe_id, period_year, period_quarter, planned_audits, completed_audits, total_findings, critical_findings, high_findings)
SELECT id, 2025, 4, 3, 2, 8, 1, 3 FROM audit_universe WHERE code = 'IT-DIV'
ON CONFLICT DO NOTHING;

INSERT INTO audit_coverage (audit_universe_id, period_year, period_quarter, planned_audits, completed_audits, total_findings, critical_findings, high_findings)
SELECT id, 2026, 1, 5, 1, 4, 1, 2 FROM audit_universe WHERE code = 'OPS-DIV'
ON CONFLICT DO NOTHING;

-- ===============================================
-- SECTION 9: VERIFICATION QUERIES
-- ===============================================

-- Verify tables created
SELECT tablename FROM pg_tables
WHERE schemaname = 'Risk_Assess_Framework'
AND tablename IN ('audit_universe', 'audit_findings', 'audit_recommendations', 'audit_coverage', 'risk_trend_history',
                  'audit_universe_department_link', 'ra_audit_universe_levels', 'ra_finding_severity',
                  'ra_finding_status', 'ra_recommendation_status')
ORDER BY tablename;

-- View audit universe hierarchy
SELECT
    au.id,
    REPEAT('  ', au.level - 1) || au.name AS hierarchy,
    au.code,
    au.level,
    au.level_name,
    au.risk_rating,
    au.owner
FROM audit_universe au
ORDER BY
    COALESCE(au.parent_id, au.id),
    au.level,
    au.name;

-- ===============================================
-- END OF SCRIPT
-- ===============================================
