-- ===============================================
-- RISK ASSESSMENT FRAMEWORK - DATABASE SCHEMA UPDATES
-- ===============================================
-- This script contains all the database schema changes needed to support
-- the missing frontend APIs identified in the gaps analysis.
--
-- Schema: Risk_Assess_Framework
-- Author: Generated from API Gaps Analysis
-- Date: $(date)
-- ===============================================

-- Set the schema context
SET search_path TO "Risk_Assess_Framework";

-- ===============================================
-- SECTION 1: CREATE LOOKUP TABLES (Following Schema Pattern)
-- ===============================================

-- 1. RISK LEVELS LOOKUP TABLE
-- Purpose: Centralized risk level management (follows ra_* table pattern)
CREATE TABLE ra_risklevels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard risk levels
INSERT INTO ra_risklevels (name, description, sort_order) VALUES
('High', 'High risk level requiring immediate attention', 1),
('Medium', 'Medium risk level requiring monitoring', 2),
('Low', 'Low risk level with minimal impact', 3);

-- 2. PROJECT STATUS LOOKUP TABLE
-- Purpose: Project status management
CREATE TABLE ra_projectstatus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard project statuses
INSERT INTO ra_projectstatus (name, description, sort_order) VALUES
('Not Started', 'Project has not yet begun', 1),
('In Progress', 'Project is currently being worked on', 2),
('Completed', 'Project has been finished successfully', 3),
('On Hold', 'Project is temporarily paused', 4);

-- 3. USER ROLES LOOKUP TABLE
-- Purpose: User role management
CREATE TABLE ra_userroles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard user roles
INSERT INTO ra_userroles (name, description, sort_order) VALUES
('admin', 'System administrator with full access', 1),
('auditor', 'Risk assessment auditor with assessment management rights', 2),
('user', 'Standard user with limited access', 3);

-- 4. ASSESSMENT STATUS LOOKUP TABLE
-- Purpose: Risk assessment status management
CREATE TABLE ra_assessmentstatus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard assessment statuses
INSERT INTO ra_assessmentstatus (name, description, sort_order) VALUES
('Draft', 'Assessment is being created', 1),
('In Progress', 'Assessment is actively being conducted', 2),
('Under Review', 'Assessment is being reviewed', 3),
('Completed', 'Assessment has been completed', 4),
('Approved', 'Assessment has been approved', 5);

-- 5. REFERENCE STATUS LOOKUP TABLE
-- Purpose: Assessment reference status management
CREATE TABLE ra_referencestatus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard reference statuses
INSERT INTO ra_referencestatus (name, description, sort_order) VALUES
('Active', 'Reference is currently active', 1),
('Completed', 'Reference has been completed', 2),
('Cancelled', 'Reference has been cancelled', 3);

-- ===============================================
-- SECTION 2: CREATE MAIN TABLES
-- ===============================================

-- 6. DEPARTMENTS TABLE
-- Required by: views/departments_view.py (731 lines)
-- Purpose: Department management with CRUD operations
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    head VARCHAR(255),
    risk_level_id INTEGER REFERENCES ra_risklevels(id) DEFAULT 2, -- Default to 'Medium'
    assessments INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comment to table
COMMENT ON TABLE departments IS 'Organizational departments with risk assessment tracking';
COMMENT ON COLUMN departments.assessments IS 'Count of risk assessments associated with this department';
COMMENT ON COLUMN departments.risk_level_id IS 'Foreign key to ra_risklevels table';

-- 7. PROJECTS TABLE  
-- Required by: views/projects_view.py (1246 lines)
-- Purpose: Project portfolio management with department linkage
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status_id INTEGER REFERENCES ra_projectstatus(id) DEFAULT 1, -- Default to 'Not Started'
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2),
    risk_level_id INTEGER REFERENCES ra_risklevels(id) DEFAULT 2, -- Default to 'Medium'
    manager VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comment to table
COMMENT ON TABLE projects IS 'Project portfolio with department assignment and risk tracking';
COMMENT ON COLUMN projects.department_id IS 'Foreign key reference to departments table';
COMMENT ON COLUMN projects.status_id IS 'Foreign key to ra_projectstatus table';
COMMENT ON COLUMN projects.risk_level_id IS 'Foreign key to ra_risklevels table';

-- 8. USERS TABLE (Enhanced User Management)
-- Required by: controllers/user_controller.py (429 lines)
-- Purpose: Complete user administration with role and department assignment
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role_id INTEGER REFERENCES ra_userroles(id) DEFAULT 3, -- Default to 'user'
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comment to table
COMMENT ON TABLE users IS 'System users with role-based access and department assignment';
COMMENT ON COLUMN users.password_hash IS 'Hashed password - never store plain text passwords';
COMMENT ON COLUMN users.role_id IS 'Foreign key to ra_userroles table';

-- ===============================================
-- SECTION 3: UPDATE AUTHENTICATION TABLES
-- ===============================================

-- 9. UPDATE ACCOUNTS TABLE TO MATCH FRONTEND EXPECTATIONS
-- Current: user_id, password, firstname, email
-- Frontend expects: id, username, name, email, role, department
-- Solution: Add missing columns and create proper relationships

-- Add missing columns to accounts table
ALTER TABLE accounts 
ADD COLUMN username VARCHAR(100) UNIQUE,
ADD COLUMN lastname VARCHAR(255),
ADD COLUMN role_id INTEGER REFERENCES ra_userroles(id) DEFAULT 3, -- Default to 'user'
ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
ADD COLUMN is_active BOOLEAN DEFAULT TRUE,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing accounts to have usernames (using email prefix)
UPDATE accounts SET username = split_part(email, '@', 1) WHERE username IS NULL;

-- Make username NOT NULL after populating
ALTER TABLE accounts ALTER COLUMN username SET NOT NULL;

-- Add comments to new columns
COMMENT ON COLUMN accounts.username IS 'Unique username for login (separate from email)';
COMMENT ON COLUMN accounts.lastname IS 'User last name (combined with firstname for full name)';
COMMENT ON COLUMN accounts.role_id IS 'Foreign key to ra_userroles table';
COMMENT ON COLUMN accounts.department_id IS 'Foreign key to departments table';

-- 10. CREATE VIEW FOR FRONTEND COMPATIBILITY
-- This view combines accounts data in the format frontend expects
CREATE OR REPLACE VIEW user_view AS
SELECT 
    a.user_id as id,
    a.username,
    CONCAT(a.firstname, ' ', COALESCE(a.lastname, '')) as name,
    a.email,
    r.name as role,
    d.name as department,
    a.is_active,
    a.created_at,
    a.updated_at
FROM accounts a
LEFT JOIN ra_userroles r ON a.role_id = r.id
LEFT JOIN departments d ON a.department_id = d.id;

-- Add comment to view
COMMENT ON VIEW user_view IS 'View that presents user data in frontend-compatible format';

-- ===============================================
-- SECTION 4: ALTER EXISTING TABLES
-- ===============================================

-- 11. ADD COLUMNS TO RISKASSESSMENT TABLE
-- Purpose: Link assessments to departments, projects, and auditors
-- Current table lacks organizational context
ALTER TABLE riskassessment 
ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
ADD COLUMN auditor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN status_id INTEGER REFERENCES ra_assessmentstatus(id) DEFAULT 1, -- Default to 'Draft'
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add comments to new columns
COMMENT ON COLUMN riskassessment.department_id IS 'Department this assessment belongs to';
COMMENT ON COLUMN riskassessment.project_id IS 'Project this assessment is associated with (optional)';
COMMENT ON COLUMN riskassessment.auditor_id IS 'User who is conducting/responsible for this assessment';
COMMENT ON COLUMN riskassessment.status_id IS 'Foreign key to ra_assessmentstatus table';

-- 12. ADD COLUMNS TO RISKASSESSMENTREFERENCE TABLE
-- Purpose: Link assessment references to departments and projects
-- Add metadata for better assessment management
ALTER TABLE riskassessmentreference
ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
ADD COLUMN title VARCHAR(255),
ADD COLUMN description TEXT,
ADD COLUMN status_id INTEGER REFERENCES ra_referencestatus(id) DEFAULT 1, -- Default to 'Active'
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add comments to new columns
COMMENT ON COLUMN riskassessmentreference.title IS 'Human-readable title for the assessment reference';
COMMENT ON COLUMN riskassessmentreference.description IS 'Detailed description of the assessment scope';
COMMENT ON COLUMN riskassessmentreference.status_id IS 'Foreign key to ra_referencestatus table';

-- ===============================================
-- SECTION 5: OPTIONAL REPORTING TABLES
-- ===============================================

-- 13. ASSESSMENT STATISTICS TABLE (For Dashboard Performance)
-- Required by: views/dashboard.py (420 lines), main.py lines 260-285
-- Purpose: Pre-calculated statistics for dashboard APIs
CREATE TABLE assessment_statistics (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    total_assessments INTEGER DEFAULT 0,
    completed_assessments INTEGER DEFAULT 0,
    high_risk_assessments INTEGER DEFAULT 0,
    medium_risk_assessments INTEGER DEFAULT 0,
    low_risk_assessments INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comment to table
COMMENT ON TABLE assessment_statistics IS 'Pre-calculated statistics for dashboard performance';
COMMENT ON COLUMN assessment_statistics.last_updated IS 'Timestamp when statistics were last recalculated';

-- 14. ACTIVITY LOG TABLE (Enhanced Audit Trail)
-- Purpose: Comprehensive audit logging for all entity changes
-- Note: Only create if existing auditlog table is insufficient
CREATE TABLE activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'assessment', 'department', 'project', 'user'
    entity_id INTEGER NOT NULL,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comment to table
COMMENT ON TABLE activity_log IS 'Comprehensive audit log for all system activities';
COMMENT ON COLUMN activity_log.details IS 'JSON details of what changed in the action';

-- ===============================================
-- SECTION 6: PERFORMANCE INDEXES
-- ===============================================

-- LOOKUP TABLE INDEXES
CREATE INDEX idx_ra_risklevels_name ON ra_risklevels(name);
CREATE INDEX idx_ra_risklevels_sort_order ON ra_risklevels(sort_order);
CREATE INDEX idx_ra_projectstatus_name ON ra_projectstatus(name);
CREATE INDEX idx_ra_projectstatus_sort_order ON ra_projectstatus(sort_order);
CREATE INDEX idx_ra_userroles_name ON ra_userroles(name);
CREATE INDEX idx_ra_userroles_sort_order ON ra_userroles(sort_order);
CREATE INDEX idx_ra_assessmentstatus_name ON ra_assessmentstatus(name);
CREATE INDEX idx_ra_assessmentstatus_sort_order ON ra_assessmentstatus(sort_order);
CREATE INDEX idx_ra_referencestatus_name ON ra_referencestatus(name);
CREATE INDEX idx_ra_referencestatus_sort_order ON ra_referencestatus(sort_order);

-- DEPARTMENT INDEXES
CREATE INDEX idx_departments_name ON departments(name);
CREATE INDEX idx_departments_risk_level_id ON departments(risk_level_id);
CREATE INDEX idx_departments_created_at ON departments(created_at);

-- PROJECT INDEXES
CREATE INDEX idx_projects_department_id ON projects(department_id);
CREATE INDEX idx_projects_status_id ON projects(status_id);
CREATE INDEX idx_projects_risk_level_id ON projects(risk_level_id);
CREATE INDEX idx_projects_dates ON projects(start_date, end_date);
CREATE INDEX idx_projects_manager ON projects(manager);
CREATE INDEX idx_projects_created_at ON projects(created_at);

-- USER INDEXES (for new users table)
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_department_id ON users(department_id);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ACCOUNTS INDEXES (for updated accounts table)
CREATE INDEX idx_accounts_username ON accounts(username);
CREATE INDEX idx_accounts_email ON accounts(email);
CREATE INDEX idx_accounts_department_id ON accounts(department_id);
CREATE INDEX idx_accounts_role_id ON accounts(role_id);
CREATE INDEX idx_accounts_is_active ON accounts(is_active);
CREATE INDEX idx_accounts_created_at ON accounts(created_at);

-- RISK ASSESSMENT INDEXES (New Columns)
CREATE INDEX idx_riskassessment_department_id ON riskassessment(department_id);
CREATE INDEX idx_riskassessment_project_id ON riskassessment(project_id);
CREATE INDEX idx_riskassessment_auditor_id ON riskassessment(auditor_id);
CREATE INDEX idx_riskassessment_status_id ON riskassessment(status_id);
CREATE INDEX idx_riskassessment_created_at ON riskassessment(created_at);

-- RISK ASSESSMENT REFERENCE INDEXES (New Columns)
CREATE INDEX idx_riskassessmentreference_department_id ON riskassessmentreference(department_id);
CREATE INDEX idx_riskassessmentreference_project_id ON riskassessmentreference(project_id);
CREATE INDEX idx_riskassessmentreference_status_id ON riskassessmentreference(status_id);
CREATE INDEX idx_riskassessmentreference_title ON riskassessmentreference(title);

-- STATISTICS INDEXES
CREATE INDEX idx_assessment_statistics_department_id ON assessment_statistics(department_id);
CREATE INDEX idx_assessment_statistics_last_updated ON assessment_statistics(last_updated);

-- ACTIVITY LOG INDEXES
CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX idx_activity_log_entity ON activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_log_action ON activity_log(action);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);

-- ===============================================
-- SECTION 7: TRIGGERS FOR AUTOMATIC UPDATES
-- ===============================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_riskassessment_updated_at BEFORE UPDATE ON riskassessment 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_riskassessmentreference_updated_at BEFORE UPDATE ON riskassessmentreference 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===============================================
-- SECTION 8: SAMPLE DATA (OPTIONAL)
-- ===============================================

-- Insert sample departments
INSERT INTO departments (name, head, risk_level_id, assessments) VALUES
('Information Technology', 'John Smith', 1, 0), -- High risk
('Finance', 'Sarah Johnson', 2, 0), -- Medium risk
('Human Resources', 'Mike Brown', 3, 0), -- Low risk
('Operations', 'Lisa Davis', 2, 0), -- Medium risk
('Legal & Compliance', 'David Wilson', 1, 0); -- High risk

-- Insert sample users (Note: In production, passwords should be properly hashed)
INSERT INTO users (username, password_hash, name, email, role_id, department_id) VALUES
('admin', '$2b$12$placeholder_hash_admin', 'System Administrator', 'admin@company.com', 1, NULL), -- admin role
('jsmith', '$2b$12$placeholder_hash_jsmith', 'John Smith', 'john.smith@company.com', 2, 1), -- auditor role, IT dept
('sjohnson', '$2b$12$placeholder_hash_sjohnson', 'Sarah Johnson', 'sarah.johnson@company.com', 2, 2), -- auditor role, Finance dept
('mbrown', '$2b$12$placeholder_hash_mbrown', 'Mike Brown', 'mike.brown@company.com', 3, 3), -- user role, HR dept
('ldavis', '$2b$12$placeholder_hash_ldavis', 'Lisa Davis', 'lisa.davis@company.com', 2, 4); -- auditor role, Operations dept

-- Insert sample projects
INSERT INTO projects (name, description, status_id, department_id, start_date, end_date, budget, risk_level_id, manager) VALUES
('IT Security Audit', 'Comprehensive security assessment of IT infrastructure', 2, 1, '2024-01-15', '2024-06-30', 50000.00, 1, 'John Smith'), -- In Progress, High risk
('Financial Controls Review', 'Review of financial processes and controls', 1, 2, '2024-02-01', '2024-08-31', 30000.00, 2, 'Sarah Johnson'), -- Not Started, Medium risk
('HR Policy Update', 'Update and review of HR policies and procedures', 3, 3, '2023-10-01', '2024-01-31', 15000.00, 3, 'Mike Brown'), -- Completed, Low risk
('Operational Efficiency Study', 'Analysis of operational processes for efficiency improvements', 2, 4, '2024-01-01', '2024-12-31', 75000.00, 2, 'Lisa Davis'); -- In Progress, Medium risk

-- Update existing accounts with sample data (if any exist)
-- This adds role and department assignments to existing accounts
UPDATE accounts SET 
    lastname = 'User',
    role_id = 1, -- admin role
    department_id = 1 -- IT department
WHERE email = 'admin@company.com';

-- Insert sample accounts if they don't exist
INSERT INTO accounts (username, password, firstname, lastname, email, role_id, department_id) 
SELECT * FROM (VALUES
    ('admin', 'admin123', 'System', 'Administrator', 'admin@company.com', 1, NULL),
    ('jsmith', 'password123', 'John', 'Smith', 'john.smith@company.com', 2, 1),
    ('sjohnson', 'password123', 'Sarah', 'Johnson', 'sarah.johnson@company.com', 2, 2),
    ('mbrown', 'password123', 'Mike', 'Brown', 'mike.brown@company.com', 3, 3),
    ('ldavis', 'password123', 'Lisa', 'Davis', 'lisa.davis@company.com', 2, 4)
) AS v(username, password, firstname, lastname, email, role_id, department_id)
WHERE NOT EXISTS (SELECT 1 FROM accounts WHERE email = v.email);

-- ===============================================
-- SECTION 9: VERIFICATION QUERIES
-- ===============================================

-- Verify tables were created successfully
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'Risk_Assess_Framework' 
    AND tablename IN ('ra_risklevels', 'ra_projectstatus', 'ra_userroles', 'ra_assessmentstatus', 'ra_referencestatus',
                      'departments', 'projects', 'users', 'assessment_statistics', 'activity_log')
ORDER BY tablename;

-- Verify new columns were added to existing tables
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'Risk_Assess_Framework' 
    AND table_name IN ('riskassessment', 'riskassessmentreference')
    AND column_name IN ('department_id', 'project_id', 'auditor_id', 'status_id', 'title', 'description')
ORDER BY table_name, column_name;

-- Verify foreign key constraints
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'Risk_Assess_Framework'
    AND tc.table_name IN ('accounts', 'departments', 'projects', 'users', 'riskassessment', 'riskassessmentreference', 'assessment_statistics', 'activity_log')
ORDER BY tc.table_name, kcu.column_name;

-- Verify user_view works correctly
SELECT 
    id, username, name, email, role, department, is_active
FROM user_view 
LIMIT 5;

-- ===============================================
-- END OF SCRIPT
-- ===============================================

-- NEXT STEPS:
-- 1. Review and test this script in a development environment first
-- 2. Backup your existing database before running in production
-- 3. Update your backend API models to include the new fields
-- 4. Implement the missing API endpoints identified in the gaps analysis
-- 5. Update frontend code to use APIs instead of direct database queries

-- IMPLEMENTATION PRIORITY:
-- IMMEDIATE: 
--   1. Lookup tables (ra_risklevels, ra_projectstatus, ra_userroles, ra_assessmentstatus, ra_referencestatus)
--   2. departments, users tables
--   3. riskassessment table alterations
-- HIGH: 
--   4. projects table
--   5. riskassessmentreference alterations  
-- MEDIUM: 
--   6. assessment_statistics, activity_log tables

-- NOTE: The lookup tables MUST be created first since other tables reference them! 