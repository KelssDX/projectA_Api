import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters (for direct DB access if needed)
DB_CONFIG = {
    "dbname": "risk_assessment",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

# API endpoint configuration
API_CONFIG = {
    "auditing_api": "http://localhost:5023/api/v1",  # Affine.Auditing.API
    "identity_api": "http://localhost:7239/api/v1",  # Affina.Identity.API
    "timeout": 30,
    "verify_ssl": False  # Set to True in production
}

# Microsoft Power BI integration settings for the Analytical Report view.
# `report_url` may include placeholders such as:
# - {referenceId}
# - {auditUniverseId}
POWER_BI_CONFIG = {
    "enabled": False,
    "mode": "link",
    "report_url": "",
    "workspace_id": "",
    "report_id": "",
    "dataset_id": ""
}

WORKFLOW_CONFIG = {
    "enabled": True,
    "service_url": "https://localhost:5001/elsa/api",
    "studio_url": "https://localhost:7001",
    "open_studio_for_admin_only": False
}

# Legacy API_BASE_URL for compatibility with existing code
API_BASE_URL = API_CONFIG["auditing_api"]

# API endpoints for Auditing API
AUDITING_ENDPOINTS = {
    "get_assessments": "/RiskAssessment/GetAssessments",
    "get_risk_assessment": "/RiskAssessment/GetRiskAssessment",
    "create_risk_assessment": "/RiskAssessment/CreateRiskAssessment",
    "update_risk_assessment": "/RiskAssessment/UpdateRiskAssessment",
    "delete_risk_assessment": "/RiskAssessment/DeleteRiskAssessment",
    "get_risks": "/RiskAssessment/GetRisks",
    "get_controls": "/RiskAssessment/GetControls",
    "get_outcomes": "/RiskAssessment/GetOutcomes",
    "get_risk_likelihoods": "/RiskAssessment/GetRiskLikelihoods",
    "get_impacts": "/RiskAssessment/GetImpacts",
    "get_key_secondary_risks": "/RiskAssessment/GetKeySecondaryRisks",
    "get_risk_categories": "/RiskAssessment/GetRiskCategories",
    "get_data_frequencies": "/RiskAssessment/GetDataFrequencies",
    "get_outcome_likelihoods": "/RiskAssessment/GetOutcomeLikelihoods",
    "get_evidence": "/RiskAssessment/GetEvidence",
    "create_reference": "/RiskAssessment/CreateReference",
    "update_reference": "/RiskAssessment/UpdateReference",
    "start_control_testing": "/RiskAssessment/StartControlTesting",
    "get_heatmap": "/RiskGraphs/GetHeatmap",
    "get_analytical_report": "/RiskGraphs/GetAnalyticalReport",
    "get_market_insights": "/RiskGraphs/GetMarketInsights",
    "get_top_risks": "/RiskGraphs/GetTopRisks",
    "get_correlation_matrix": "/RiskGraphs/GetCorrelationMatrix",
    "get_operational_risks": "/OperationalRisk/GetOperationalRisks",
    "get_departments": "/RiskAssessment/GetDepartments",
    "get_projects": "/RiskAssessment/GetProjects",
    "get_collaborator_roles": "/RiskAssessment/GetCollaboratorRoles",
    "get_project_collaborators": "/RiskAssessment/GetProjectCollaborators",
    "save_project_collaborators": "/RiskAssessment/SaveProjectCollaborators",
    "get_reference_collaborators": "/RiskAssessment/GetReferenceCollaborators",
    "save_reference_collaborators": "/RiskAssessment/SaveReferenceCollaborators",
    "seed_market_data": "/MarketRisk/SeedData",

    # Departments CRUD
    "create_department": "/RiskAssessment/CreateDepartment",
    "update_department": "/RiskAssessment/UpdateDepartment",
    "delete_department": "/RiskAssessment/DeleteDepartment",

    # Projects CRUD
    "create_project": "/RiskAssessment/CreateProject",
    "update_project": "/RiskAssessment/UpdateProject",
    "delete_project": "/RiskAssessment/DeleteProject"
}

# API endpoints for Identity API
IDENTITY_ENDPOINTS = {
    "login": "/UserLogin/login",
    "get_users": "/UserLogin/getusers",
    "get_user": "/UserLogin/getuser/{id}",
    "get_users_by_role": "/UserLogin/getusersbyrole/{role}",
    "get_users_by_department": "/UserLogin/getusersbydepartment/{departmentId}",
    "create_user": "/UserLogin/createuser",
    "update_user": "/UserLogin/updateuser/{id}",
    "delete_user": "/UserLogin/deleteuser/{id}",
    "change_password": "/UserLogin/changepassword/{id}",
    "toggle_user_status": "/UserLogin/toggleuserstatus/{id}"
}

EXPORT_DIRECTORY = 'data/exports'  # Directory for export files

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def get_auditing_api_url(endpoint_key):
    """Get the full API URL for an auditing endpoint"""
    base_url = API_CONFIG["auditing_api"]
    endpoint = AUDITING_ENDPOINTS.get(endpoint_key, "")
    return f"{base_url}{endpoint}"

def get_identity_api_url(endpoint_key):
    """Get the full API URL for an identity endpoint"""
    base_url = API_CONFIG["identity_api"]
    endpoint = IDENTITY_ENDPOINTS.get(endpoint_key, "")
    return f"{base_url}{endpoint}"

def get_workflow_studio_url():
    """Get the configured Elsa Studio URL"""
    return WORKFLOW_CONFIG.get("studio_url", "").strip()
