import aiohttp
import asyncio
import json
import mimetypes
import os
from src.core.config import API_CONFIG, get_auditing_api_url



class AuditingAPIClient:
    """Client for interacting with the Affine.Auditing.API"""
    
    def __init__(self):
        self.base_url = API_CONFIG["auditing_api"]
        self.timeout = API_CONFIG["timeout"]
        self.verify_ssl = API_CONFIG["verify_ssl"]
        self.session = None
        self.current_user = None

    def set_current_user(self, user):
        self.current_user = user
        if self.session is not None and not self.session.closed:
            self.session.headers.clear()
            self.session.headers.update(self._build_headers())

    def _get_user_value(self, *keys):
        if self.current_user is None:
            return None
        if isinstance(self.current_user, dict):
            for key in keys:
                value = self.current_user.get(key)
                if value not in (None, ""):
                    return value
            return None
        for key in keys:
            value = getattr(self.current_user, key, None)
            if value not in (None, ""):
                return value
        return None

    def _build_headers(self, include_content_type=True):
        headers = {
            "Accept": "application/json"
        }
        if include_content_type:
            headers["Content-Type"] = "application/json"

        user_id = self._get_user_value("id", "Id")
        role = self._get_user_value("role", "Role", "userType", "UserType")
        user_name = self._get_user_value("name", "Name", "username", "Username")
        user_email = self._get_user_value("email", "Email")

        if user_id not in (None, ""):
            headers["X-Audit-User-Id"] = str(user_id)
        if role not in (None, ""):
            headers["X-Audit-User-Role"] = str(role)
        if user_name not in (None, ""):
            headers["X-Audit-User-Name"] = str(user_name)
        if user_email not in (None, ""):
            headers["X-Audit-User-Email"] = str(user_email)

        return headers

    def _normalize_collaborator_role(self, item):
        if not isinstance(item, dict):
            return None
        return {
            "id": item.get("id", item.get("Id")),
            "name": item.get("name", item.get("Name", "")),
            "description": item.get("description", item.get("Description", "")),
            "color": item.get("color", item.get("Color", "#64748b")),
            "is_client_role": bool(item.get("isClientRole", item.get("IsClientRole", False))),
            "sort_order": item.get("sortOrder", item.get("SortOrder")),
            "is_active": bool(item.get("isActive", item.get("IsActive", True))),
        }

    def _normalize_collaborator_assignment(self, item):
        if not isinstance(item, dict):
            return None
        return {
            "id": item.get("id", item.get("Id")),
            "project_id": item.get("projectId", item.get("project_id", item.get("ProjectId"))),
            "reference_id": item.get("referenceId", item.get("reference_id", item.get("ReferenceId"))),
            "user_id": item.get("userId", item.get("user_id", item.get("UserId"))),
            "user_name": item.get("userName", item.get("user_name", item.get("UserName", "Unknown User"))),
            "user_email": item.get("userEmail", item.get("user_email", item.get("UserEmail", ""))),
            "user_system_role": item.get("userSystemRole", item.get("user_system_role", item.get("UserSystemRole", ""))),
            "collaborator_role_id": item.get("collaboratorRoleId", item.get("collaborator_role_id", item.get("CollaboratorRoleId"))),
            "collaborator_role_name": item.get("collaboratorRoleName", item.get("collaborator_role_name", item.get("CollaboratorRoleName", "Collaborator"))),
            "collaborator_role_color": item.get("collaboratorRoleColor", item.get("collaborator_role_color", item.get("CollaboratorRoleColor", "#64748b"))),
            "can_edit": bool(item.get("canEdit", item.get("can_edit", item.get("CanEdit", False)))),
            "can_review": bool(item.get("canReview", item.get("can_review", item.get("CanReview", False)))),
            "can_upload_evidence": bool(item.get("canUploadEvidence", item.get("can_upload_evidence", item.get("CanUploadEvidence", False)))),
            "can_manage_access": bool(item.get("canManageAccess", item.get("can_manage_access", item.get("CanManageAccess", False)))),
            "notes": item.get("notes", item.get("Notes", "")),
            "assigned_by_user_id": item.get("assignedByUserId", item.get("assigned_by_user_id", item.get("AssignedByUserId"))),
            "assigned_by_name": item.get("assignedByName", item.get("assigned_by_name", item.get("AssignedByName", ""))),
            "created_at": item.get("createdAt", item.get("created_at", item.get("CreatedAt"))),
            "updated_at": item.get("updatedAt", item.get("updated_at", item.get("UpdatedAt"))),
            "is_inherited_from_project": bool(item.get("isInheritedFromProject", item.get("is_inherited_from_project", item.get("IsInheritedFromProject", False)))),
        }
    
    async def _ensure_session(self):
        """Ensure HTTP session is created for the current event loop"""
        current_loop = asyncio.get_event_loop()
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers=self._build_headers()
            )
        elif hasattr(self, '_session_loop') and self._session_loop != current_loop:
            try:
                await self.session.close()
            except:
                pass
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers=self._build_headers()
            )
        elif self.session is not None and not self.session.closed:
            self.session.headers.clear()
            self.session.headers.update(self._build_headers())
        self._session_loop = current_loop
    
    async def get_risk_assessment(self, reference_id):
        """Get a risk assessment by reference ID"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_risk_assessment")
        params = {"referenceId": reference_id}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get risk assessment: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def create_risk_assessment(self, assessment_data):
        """Create a new risk assessment"""
        await self._ensure_session()
        
        url = get_auditing_api_url("create_risk_assessment")
        
        try:
            async with self.session.post(url, json=assessment_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create risk assessment: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def update_risk_assessment(self, reference_id, update_data):
        """Update an existing risk assessment"""
        await self._ensure_session()
        
        url = get_auditing_api_url("update_risk_assessment") + f"/{reference_id}"
        
        try:
            async with self.session.put(url, json=update_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update risk assessment: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def update_reference(self, reference_id, reference_data):
        """Update a risk assessment reference (header info like Assessor)"""
        await self._ensure_session()
        
        url = get_auditing_api_url("update_reference") + f"/{reference_id}"
        
        try:
            async with self.session.put(url, json=reference_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update reference: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def delete_risk_assessment(self, reference_id, assessment_id):
        """Delete a risk assessment by its ID and reference ID"""
        await self._ensure_session()
        
        url = get_auditing_api_url("delete_risk_assessment") + f"/{reference_id}/{assessment_id}"
        
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to delete risk assessment: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_assessments(self):
        """Get all risk assessments"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_assessments")
        print(f"DEBUG: [AuditingAPIClient] Fetching assessments from: {url}")
        
        try:
            async with self.session.get(url) as response:
                print(f"DEBUG: [AuditingAPIClient] Response Status: {response.status}")
                if response.status == 200:
                    raw = await response.json()
                    print(f"DEBUG: [AuditingAPIClient] Raw response count: {len(raw) if isinstance(raw, list) else 'NOT A LIST'}")
                    if not isinstance(raw, list):
                        print(f"DEBUG: [AuditingAPIClient] ERROR: Expected list but got {type(raw)}")
                        return []
                    normalized = []
                    for item in raw:
                        if not isinstance(item, dict):
                            continue
                        
                        # Map API response to frontend expected format
                        # API returns: id, title, auditor, assessment_date, risk_score, risk_level, created_at, updated_at
                        normalized.append({
                            "id": f"A-{item.get('id', 0):03d}",  # Format as A-001, A-002, etc.
                            "reference_id": item.get("id"),      # Keep raw ID for API calls
                            "title": item.get("title", "Untitled Assessment"),
                            "department_id": item.get("department_id"),
                            "department": item.get("department") or "General",
                            "project_id": item.get("project_id"),
                            "project": item.get("project"),
                            "engagement_type_id": item.get("engagement_type_id"),
                            "engagement_type_name": item.get("engagement_type_name"),
                            "auditor_id": item.get("auditor_id"),
                            "auditor": item.get("auditor", "Unknown"),
                            "assessment_date": item.get("assessment_date"),
                            "risk_score": float(item.get("risk_score", 0)) if item.get("risk_score") is not None else 0.0,
                            "risk_level": item.get("risk_level", "Low"),
                            "scope": item.get("scope", ""),
                            "findings": item.get("findings", ""),
                            "recommendations": item.get("recommendations", ""),
                            "risk_factors": item.get("risk_factors") or [],
                            "created_at": item.get("created_at"),
                            "updated_at": item.get("updated_at"),
                        })
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get assessments: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_risks(self):
        """Get all risks"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_risks")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get risks: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_controls(self):
        """Get all controls"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_controls")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get controls: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_outcomes(self):
        """Get all outcomes"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_outcomes")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get outcomes: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_risk_likelihoods(self):
        """Get all risk likelihoods"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_risk_likelihoods")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get risk likelihoods: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_impacts(self):
        """Get all impacts"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_impacts")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get impacts: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_key_secondary_risks(self):
        """Get all key secondary risks"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_key_secondary_risks")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get key secondary risks: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_risk_categories(self):
        """Get all risk categories"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_risk_categories")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get risk categories: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_departments(self):
        """Get all departments with details"""
        await self._ensure_session()

        url = get_auditing_api_url("get_departments")

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    raw = await response.json()
                    if not isinstance(raw, list):
                        return []
                    
                    # Map risk_level_id to risk_level string
                    risk_level_mapping = {
                        1: "High",
                        2: "Medium", 
                        3: "Low"
                    }
                    
                    normalized = []
                    for dept in raw:
                        if not isinstance(dept, dict):
                            continue
                        
                        risk_level_id = dept.get("riskLevelId") or dept.get("risk_level_id")
                        risk_level = risk_level_mapping.get(risk_level_id, "Low")
                        
                        normalized.append({
                            "id": dept.get("id"),
                            "name": dept.get("name", "Unknown Department"),
                            "head": dept.get("head", "Unknown"),
                            "risk_level_id": risk_level_id,
                            "risk_level": risk_level,
                            "assessments": dept.get("assessments", 0),
                            "created_at": dept.get("createdAt") or dept.get("created_at"),
                            "updated_at": dept.get("updatedAt") or dept.get("updated_at"),
                        })
                    
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get departments: {error_text}")

        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_projects(self):
        """Get all projects with details"""
        await self._ensure_session()

        url = get_auditing_api_url("get_projects")

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    raw = await response.json()
                    if not isinstance(raw, list):
                        return []
                    
                    # Map status_id and risk_level_id to strings
                    status_mapping = {
                        1: "Planning",
                        2: "Active", 
                        3: "Completed",
                        4: "On Hold",
                        5: "Cancelled"
                    }
                    
                    risk_level_mapping = {
                        1: "High",
                        2: "Medium", 
                        3: "Low"
                    }
                    
                    normalized = []
                    for project in raw:
                        if not isinstance(project, dict):
                            continue
                        
                        status_id = project.get("statusId") or project.get("status_id")
                        risk_level_id = project.get("riskLevelId") or project.get("risk_level_id")
                        
                        normalized.append({
                            "id": project.get("id"),
                            "name": project.get("name", "Unknown Project"),
                            "description": project.get("description", ""),
                            "status_id": status_id,
                            "status": status_mapping.get(status_id, "Unknown"),
                            "department_id": project.get("departmentId") or project.get("department_id"),
                            "start_date": project.get("startDate") or project.get("start_date"),
                            "end_date": project.get("endDate") or project.get("end_date"),
                            "budget": project.get("budget", "0"),
                            "risk_level_id": risk_level_id,
                            "risk_level": risk_level_mapping.get(risk_level_id, "Low"),
                            "manager": project.get("manager", "Unknown"),
                            "collaborator_count": project.get("collaboratorCount", project.get("collaborator_count", 0)) or 0,
                            "created_at": project.get("createdAt") or project.get("created_at"),
                            "updated_at": project.get("updatedAt") or project.get("updated_at"),
                        })
                    
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get projects: {error_text}")

        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_department(self, department_data):
        """Create a department"""
        await self._ensure_session()
        url = get_auditing_api_url("create_department")

        try:
            async with self.session.post(url, json=department_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create department: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_department(self, department_id, department_data):
        """Update a department"""
        await self._ensure_session()
        url = get_auditing_api_url("update_department") + f"/{department_id}"

        try:
            async with self.session.put(url, json=department_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update department: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_department(self, department_id):
        """Delete a department"""
        await self._ensure_session()
        url = get_auditing_api_url("delete_department") + f"/{department_id}"

        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to delete department: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_project(self, project_data):
        """Create a project"""
        await self._ensure_session()
        url = get_auditing_api_url("create_project")

        try:
            async with self.session.post(url, json=project_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create project: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_project(self, project_id, project_data):
        """Update a project"""
        await self._ensure_session()
        url = get_auditing_api_url("update_project") + f"/{project_id}"

        try:
            async with self.session.put(url, json=project_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update project: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_project(self, project_id):
        """Delete a project"""
        await self._ensure_session()
        url = get_auditing_api_url("delete_project") + f"/{project_id}"

        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to delete project: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_collaborator_roles(self):
        """Get available collaborator role options"""
        await self._ensure_session()
        url = get_auditing_api_url("get_collaborator_roles")

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    raw = await response.json()
                    normalized = []
                    for item in (raw if isinstance(raw, list) else []):
                        normalized_item = self._normalize_collaborator_role(item)
                        if normalized_item:
                            normalized.append(normalized_item)
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get collaborator roles: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_project_collaborators(self, project_id):
        """Get collaborators assigned to an audit project"""
        await self._ensure_session()
        url = get_auditing_api_url("get_project_collaborators") + f"/{project_id}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    raw = await response.json()
                    normalized = []
                    for item in (raw if isinstance(raw, list) else []):
                        normalized_item = self._normalize_collaborator_assignment(item)
                        if normalized_item:
                            normalized.append(normalized_item)
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get project collaborators: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def save_project_collaborators(self, project_id, collaborators):
        """Replace audit project collaborator assignments"""
        await self._ensure_session()
        url = get_auditing_api_url("save_project_collaborators") + f"/{project_id}"
        payload = {"collaborators": collaborators or []}

        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    raw = await response.json()
                    normalized = []
                    for item in (raw if isinstance(raw, list) else []):
                        normalized_item = self._normalize_collaborator_assignment(item)
                        if normalized_item:
                            normalized.append(normalized_item)
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to save project collaborators: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_reference_collaborators(self, reference_id):
        """Get collaborators assigned to an audit file, including inherited project access"""
        await self._ensure_session()
        url = get_auditing_api_url("get_reference_collaborators") + f"/{reference_id}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    raw = await response.json()
                    normalized = []
                    for item in (raw if isinstance(raw, list) else []):
                        normalized_item = self._normalize_collaborator_assignment(item)
                        if normalized_item:
                            normalized.append(normalized_item)
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get audit file collaborators: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def save_reference_collaborators(self, reference_id, collaborators):
        """Replace explicit audit file collaborator assignments"""
        await self._ensure_session()
        url = get_auditing_api_url("save_reference_collaborators") + f"/{reference_id}"
        payload = {"collaborators": collaborators or []}

        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    raw = await response.json()
                    normalized = []
                    for item in (raw if isinstance(raw, list) else []):
                        normalized_item = self._normalize_collaborator_assignment(item)
                        if normalized_item:
                            normalized.append(normalized_item)
                    return normalized
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to save audit file collaborators: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_data_frequencies(self):
        """Get all data frequencies"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_data_frequencies")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get data frequencies: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_outcome_likelihoods(self):
        """Get all outcome likelihoods"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_outcome_likelihoods")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get outcome likelihoods: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_evidence(self):
        """Get all evidence"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_evidence")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get evidence: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def create_reference(self, reference_data):
        """Create a new risk assessment reference"""
        await self._ensure_session()
        
        url = get_auditing_api_url("create_reference")
        
        try:
            async with self.session.post(url, json=reference_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create reference: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def start_control_testing(self, reference_id, testing_data):
        """Start control testing for a risk assessment"""
        await self._ensure_session()
        
        url = get_auditing_api_url("start_control_testing") + f"/{reference_id}"
        
        try:
            async with self.session.post(url, json=testing_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to start control testing: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_heatmap(self, reference_id, department_id=None):
        """Get risk heatmap data for a reference"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_heatmap")
        params = {"referenceId": reference_id}
        if department_id is not None:
            params["departmentId"] = department_id
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get heatmap: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_heatmap_data(self, reference_id, audit_universe_id=None):
        """Alias for get_heatmap to support new widget interface"""
        # Map audit_universe_id to department_id if applicable, or ignore for now
        # Assuming audit_universe_id corresponds to department_id for this API
        return await self.get_heatmap(reference_id, department_id=audit_universe_id)

    async def get_analytical_report(self, reference_id):
        """Get analytical report data for a reference"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_analytical_report")
        params = {"referenceId": reference_id}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get analytical report: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def seed_market_data(self):
        """Trigger market data seeding"""
        await self._ensure_session()
        
        url = get_auditing_api_url("seed_market_data") 

        try:
            async with self.session.post(url) as response:
                if response.status == 200: return True
                else: 
                     # Non-critical, just log or ignore for now to prevent crash
                     print(f"Seed warning: {await response.text()}")
                     return False
        except Exception as e:
            print(f"Seed error: {e}")
            return False

    async def get_share_price_data(self, symbol):
        """Get share price history for a symbol"""
        await self._ensure_session()
        url = get_auditing_api_url("seed_market_data").replace("SeedData", "GetSharePriceData") # Hacky but works given the structure
        # Better: Add to config, but for speed:
        base = self.base_url.rstrip('/')
        url = f"{base}/MarketRisk/GetSharePriceData"
        
        params = {"symbol": symbol}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200: return await response.json()
                else: return []
        except Exception as e:
            print(f"Error fetching price data: {e}")
            return []

    async def calculate_risk_metrics(self, symbol):
        """Get calculated risk metrics"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/MarketRisk/CalculateRiskMetrics"
        
        params = {"symbol": symbol}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200: return await response.json()
                else: return {}
        except Exception as e:
            print(f"Error fetching risk metrics: {e}")
            return {}

    async def get_market_insights(self, symbol="IBM"):
        """Get market volatility and risk metrics"""
        await self._ensure_session()
        url = get_auditing_api_url("get_market_insights")
        params = {"symbol": symbol}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200: return await response.json()
                else: raise Exception(await response.text())
        except aiohttp.ClientError as e: raise Exception(f"Error: {e}")

    async def get_top_risks(self, count=10, reference_id=None):
        """Get top residual risks"""
        await self._ensure_session()
        url = get_auditing_api_url("get_top_risks")
        params = {"count": count}
        if reference_id:
            params["referenceId"] = reference_id
            
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200: return await response.json()
                else: raise Exception(await response.text())
        except aiohttp.ClientError as e: raise Exception(f"Error: {e}")

    async def get_correlation_matrix(self):
        """Get correlation matrix"""
        await self._ensure_session()
        url = get_auditing_api_url("get_correlation_matrix")
        try:
            async with self.session.get(url) as response:
                if response.status == 200: return await response.json()
                else: raise Exception(await response.text())
        except aiohttp.ClientError as e: raise Exception(f"Error: {e}")

    async def get_operational_risks(self, reference_id):
        """Get operational risks for a reference"""
        await self._ensure_session()
        url = get_auditing_api_url("get_operational_risks")
        params = {"referenceId": reference_id}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200: return await response.json()
                else: raise Exception(await response.text())
        except aiohttp.ClientError as e: raise Exception(f"Error: {e}")
    


    # =====================================================
    # AUDIT UNIVERSE METHODS
    # =====================================================

    async def get_audit_universe_hierarchy(self):
        """Get the full audit universe hierarchy as a tree"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/GetHierarchy"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get hierarchy: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_audit_universe_flat(self):
        """Get the audit universe as a flat list with paths"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/GetFlatHierarchy"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_audit_universe_node(self, node_id):
        """Get a single audit universe node by ID"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/GetNode/{node_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get node: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_audit_universe_node_with_children(self, node_id):
        """Get a node with its immediate children"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/GetNodeWithChildren/{node_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_audit_universe_node(self, node_data):
        """Create a new audit universe node"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/CreateNode"
        try:
            async with self.session.post(url, json=node_data) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create node: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_audit_universe_node(self, node_id, node_data):
        """Update an existing audit universe node"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/UpdateNode/{node_id}"
        try:
            async with self.session.put(url, json=node_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update node: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_audit_universe_node(self, node_id):
        """Delete an audit universe node"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/DeleteNode/{node_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                else:
                    return False
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_audit_universe_levels(self):
        """Get all level definitions"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/GetLevels"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def search_audit_universe(self, query):
        """Search audit universe nodes"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/Search"
        params = {"query": query}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def link_department_to_node(self, audit_universe_id, department_id):
        """Link a department to an audit universe node"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/LinkDepartment"
        data = {"auditUniverseId": audit_universe_id, "departmentId": department_id}
        try:
            async with self.session.post(url, json=data) as response:
                return response.status == 200
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_linked_departments(self, node_id):
        """Get departments linked to a node"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditUniverse/GetLinkedDepartments/{node_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    # =====================================================
    # AUDIT FINDINGS METHODS
    # =====================================================

    async def get_findings_aging(self, reference_id=None, audit_universe_id=None):
        """Get findings aging analysis"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetFindingsAging"
        params = {}
        if reference_id:
            params["referenceId"] = reference_id
        if audit_universe_id:
            params["auditUniverseId"] = audit_universe_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_findings_by_reference(self, reference_id):
        """Get all findings for an assessment reference"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_finding(self, finding_data):
        """Create a new audit finding"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/CreateFinding"
        try:
            async with self.session.post(url, json=finding_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create finding: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_finding(self, finding_id, finding_data):
        """Update an audit finding"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/UpdateFinding/{finding_id}"
        try:
            async with self.session.put(url, json=finding_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update finding: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_finding(self, finding_id):
        """Delete an audit finding"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/DeleteFinding/{finding_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete finding: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_recommendations_by_finding(self, finding_id):
        """Get recommendations linked to a finding"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetRecommendationsByFinding/{finding_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_recommendation(self, recommendation_data):
        """Create a recommendation for a finding"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/CreateRecommendation"
        try:
            async with self.session.post(url, json=recommendation_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create recommendation: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_recommendation(self, recommendation_id, recommendation_data):
        """Update a recommendation"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/UpdateRecommendation/{recommendation_id}"
        try:
            async with self.session.put(url, json=recommendation_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update recommendation: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_recommendation(self, recommendation_id):
        """Delete a recommendation"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/DeleteRecommendation/{recommendation_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete recommendation: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_audit_coverage_map(self, year, quarter=None):
        """Get audit coverage map for visualization"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetAuditCoverageMap"
        params = {"year": year}
        if quarter:
            params["quarter"] = quarter
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_management_override_analytics(self, reference_id=None, year=None, period=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/GetManagementOverrideAnalytics"
        params = {}
        if reference_id is not None:
            params["referenceId"] = reference_id
        if year is not None:
            params["year"] = year
        if period is not None:
            params["period"] = period
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_journal_exception_analytics(self, reference_id=None, year=None, period=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/GetJournalExceptionAnalytics"
        params = {}
        if reference_id is not None:
            params["referenceId"] = reference_id
        if year is not None:
            params["year"] = year
        if period is not None:
            params["period"] = period
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_user_posting_concentration(self, reference_id=None, year=None, period=None, top_users=5):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/GetUserPostingConcentration"
        params = {"topUsers": top_users}
        if reference_id is not None:
            params["referenceId"] = reference_id
        if year is not None:
            params["year"] = year
        if period is not None:
            params["period"] = period
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_trial_balance_movement(self, reference_id=None, current_year=None, prior_year=None, top_accounts=10):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/GetTrialBalanceMovement"
        params = {"topAccounts": top_accounts}
        if reference_id is not None:
            params["referenceId"] = reference_id
        if current_year is not None:
            params["currentYear"] = current_year
        if prior_year is not None:
            params["priorYear"] = prior_year
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_industry_benchmark_analytics(self, reference_id=None, year=None, top_metrics=6):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/GetIndustryBenchmarkAnalytics"
        params = {"topMetrics": top_metrics}
        if reference_id is not None:
            params["referenceId"] = reference_id
        if year is not None:
            params["year"] = year
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_reasonability_forecast_analytics(self, reference_id=None, year=None, top_items=6):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/GetReasonabilityForecastAnalytics"
        params = {"topItems": top_items}
        if reference_id is not None:
            params["referenceId"] = reference_id
        if year is not None:
            params["year"] = year
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_analytics_import_batches(self, reference_id=None, dataset_type=None, limit=20):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/GetImportBatches"
        params = {"limit": limit}
        if reference_id is not None:
            params["referenceId"] = reference_id
        if dataset_type:
            params["datasetType"] = dataset_type
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def upload_audit_analytics_file(self, file_path, import_data):
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditAnalytics/ImportCsv"
        guessed_type = mimetypes.guess_type(file_path)[0] or "text/csv"
        form = aiohttp.FormData()

        for key, value in (import_data or {}).items():
            if value is None:
                continue
            form.add_field(key, str(value))

        with open(file_path, "rb") as file_handle:
            form.add_field(
                "file",
                file_handle,
                filename=os.path.basename(file_path),
                content_type=guessed_type
            )

            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            async with aiohttp.ClientSession(connector=connector, headers=self._build_headers(include_content_type=False)) as upload_session:
                try:
                    async with upload_session.post(url, data=form) as response:
                        if response.status in (200, 201):
                            return await response.json()
                        error_text = await response.text()
                        raise Exception(f"Failed to import analytics file: {error_text}")
                except aiohttp.ClientError as e:
                    raise Exception(f"Connection error: {str(e)}")

    async def get_risk_trend(self, reference_id=None, audit_universe_id=None, months=12):
        """Get risk trend data"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetRiskTrend"
        params = {"months": months}
        if reference_id:
            params["referenceId"] = reference_id
        if audit_universe_id:
            params["auditUniverseId"] = audit_universe_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_risk_velocity(self, reference_id=None, audit_universe_id=None):
        """Get risk velocity metrics"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetRiskVelocity"
        params = {}
        if reference_id:
            params["referenceId"] = reference_id
        if audit_universe_id:
            params["auditUniverseId"] = audit_universe_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_finding_severities(self):
        """Get all finding severity levels"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetSeverities"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_finding_statuses(self):
        """Get all finding status values"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetFindingStatuses"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_recommendation_statuses(self):
        """Get all recommendation status values"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditFindings/GetRecommendationStatuses"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    # =====================================================
    # AUDIT PROCEDURES METHODS
    # =====================================================

    async def get_procedures_by_reference(self, reference_id):
        """Get all procedures for an assessment reference"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/GetByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_procedure_library(self, search_text=None, engagement_type_id=None):
        """Get reusable library procedures"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/GetLibrary"
        params = {}
        if search_text:
            params["search"] = search_text
        if engagement_type_id is not None:
            params["engagementTypeId"] = engagement_type_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_procedure(self, procedure_data):
        """Create a new audit procedure"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/CreateProcedure"
        try:
            async with self.session.post(url, json=procedure_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create procedure: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_procedure(self, procedure_id, procedure_data):
        """Update an audit procedure"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/UpdateProcedure/{procedure_id}"
        try:
            async with self.session.put(url, json=procedure_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update procedure: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_procedure(self, procedure_id):
        """Delete an audit procedure"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/DeleteProcedure/{procedure_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete procedure: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_procedure_from_template(self, procedure_data):
        """Create an assessment-linked procedure from a library template"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/CreateFromTemplate"
        try:
            async with self.session.post(url, json=procedure_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create procedure from template: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_procedure_types(self):
        """Get available procedure types"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/GetTypes"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_procedure_statuses(self):
        """Get available procedure statuses"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditProcedures/GetStatuses"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    # =====================================================
    # AUDIT WORKING PAPERS METHODS
    # =====================================================

    async def get_working_papers_by_reference(self, reference_id):
        """Get all working papers for an assessment reference"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/GetByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_working_paper_templates(self, search_text=None, engagement_type_id=None):
        """Get reusable working paper templates"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/GetTemplates"
        params = {}
        if search_text:
            params["search"] = search_text
        if engagement_type_id is not None:
            params["engagementTypeId"] = engagement_type_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_working_paper(self, working_paper_data):
        """Create a new working paper"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/CreateWorkingPaper"
        try:
            async with self.session.post(url, json=working_paper_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create working paper: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_working_paper(self, working_paper_id, working_paper_data):
        """Update a working paper"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/UpdateWorkingPaper/{working_paper_id}"
        try:
            async with self.session.put(url, json=working_paper_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update working paper: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_working_paper(self, working_paper_id):
        """Delete a working paper"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/DeleteWorkingPaper/{working_paper_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete working paper: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_working_paper_from_template(self, working_paper_data):
        """Create a working paper from a template"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/CreateFromTemplate"
        try:
            async with self.session.post(url, json=working_paper_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create working paper from template: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_working_paper_statuses(self):
        """Get available working paper statuses"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/GetStatuses"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_working_paper_signoffs(self, working_paper_id):
        """Get sign-off history for a working paper"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/GetSignoffs/{working_paper_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def add_working_paper_signoff(self, signoff_data):
        """Add a sign-off entry to a working paper"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/AddSignoff"
        try:
            async with self.session.post(url, json=signoff_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to add working paper sign-off: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_working_paper_references(self, working_paper_id):
        """Get cross-references for a working paper"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/GetReferences/{working_paper_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def add_working_paper_reference(self, reference_data):
        """Add a cross-reference between working papers"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkingPapers/AddReference"
        try:
            async with self.session.post(url, json=reference_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to add working paper reference: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    # =====================================================
    # AUDIT DOCUMENT LIBRARY METHODS
    # =====================================================

    async def get_documents_by_reference(self, reference_id):
        """Get all audit documents for an assessment reference"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/GetByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_document_categories(self):
        """Get available audit document categories"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/GetCategories"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_document_visibility_options(self):
        """Get available audit document visibility options"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/GetVisibilityOptions"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def upload_audit_document(self, file_path, document_data):
        """Upload an audit document with metadata"""
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/UploadDocument"
        guessed_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        form = aiohttp.FormData()

        for key, value in (document_data or {}).items():
            if value is None:
                continue
            form.add_field(key, str(value))

        with open(file_path, "rb") as file_handle:
            form.add_field(
                "file",
                file_handle,
                filename=os.path.basename(file_path),
                content_type=guessed_type
            )

            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            async with aiohttp.ClientSession(connector=connector, headers=self._build_headers(include_content_type=False)) as upload_session:
                try:
                    async with upload_session.post(url, data=form) as response:
                        if response.status in (200, 201):
                            return await response.json()
                        error_text = await response.text()
                        raise Exception(f"Failed to upload audit document: {error_text}")
                except aiohttp.ClientError as e:
                    raise Exception(f"Connection error: {str(e)}")

    async def update_audit_document_security(self, document_id, security_data):
        """Update audit document visibility and access grants"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/UpdateDocumentSecurity/{document_id}"
        try:
            async with self.session.put(url, json=security_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update document security: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def review_audit_document_security(self, document_id, review_data):
        """Approve or reject a restricted document security review"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/ReviewDocumentSecurity/{document_id}"
        try:
            async with self.session.post(url, json=review_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to review document security: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_audit_document(self, document_id):
        """Delete an audit document"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/DeleteDocument/{document_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete audit document: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    def get_audit_document_download_url(self, document_id):
        """Build download URL for an audit document"""
        base = self.base_url.rstrip('/')
        return f"{base}/AuditDocuments/DownloadDocument/{document_id}"

    async def get_evidence_requests_by_reference(self, reference_id):
        """Get evidence requests for an assessment reference"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/GetEvidenceRequestsByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_document_access_logs(self, reference_id, document_id=None, limit=25):
        """Get recent document access log entries for an assessment reference"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/GetAccessLogsByReference/{reference_id}"
        params = {"limit": limit}
        if document_id is not None:
            params["documentId"] = document_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to get document access logs: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_evidence_request_statuses(self):
        """Get available evidence request statuses"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/GetEvidenceRequestStatuses"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_evidence_request(self, request_data):
        """Create a new evidence request"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/CreateEvidenceRequest"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create evidence request: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def review_evidence_request_item(self, review_data):
        """Review an uploaded evidence request item"""
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditDocuments/ReviewEvidenceRequestItem"
        try:
            async with self.session.post(url, json=review_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to review evidence request item: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    # =====================================================
    # AUDIT EXECUTION METHODS
    # =====================================================

    async def get_planning_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetPlanningByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def upsert_planning(self, planning_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/UpsertPlanning"
        try:
            async with self.session.post(url, json=planning_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to save planning data: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_engagement_types(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetEngagementTypes"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_planning_statuses(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetPlanningStatuses"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_materiality_workspace(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/GetWorkspace/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to load materiality workspace: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def generate_materiality_candidates(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/GenerateCandidates"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to generate materiality candidates: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_materiality_calculations_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/GetCalculationsByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to load materiality calculations: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_materiality_calculation(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/CreateCalculation"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create materiality calculation: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def set_active_materiality_calculation(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/SetActiveCalculation"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to activate materiality calculation: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_materiality_scope_link(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/CreateScopeLink"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create materiality scope link: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_materiality_scope_link(self, scope_link_id, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/UpdateScopeLink/{scope_link_id}"
        try:
            async with self.session.put(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update materiality scope link: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_materiality_scope_link(self, scope_link_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/DeleteScopeLink/{scope_link_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to delete materiality scope link: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_materiality_misstatement(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/CreateMisstatement"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create misstatement: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_materiality_misstatement(self, misstatement_id, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/UpdateMisstatement/{misstatement_id}"
        try:
            async with self.session.put(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update misstatement: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_materiality_misstatement(self, misstatement_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditMateriality/DeleteMisstatement/{misstatement_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to delete misstatement: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_finance_audit_workspace(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/GetFinanceAuditWorkspace/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to load finance audit workspace: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def generate_trial_balance_mappings(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/GenerateTrialBalanceMappings"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to generate trial balance mappings: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def save_trial_balance_mapping(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/SaveTrialBalanceMapping"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to save trial balance mapping: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def save_mapping_profile_from_current(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/SaveMappingProfileFromCurrent"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to save mapping profile: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def generate_draft_financial_statements(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/GenerateDraftFinancialStatements"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to generate draft financial statements: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def generate_support_queue(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/GenerateSupportQueue"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to generate support queue: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_support_request(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/UpdateSupportRequest"
        try:
            async with self.session.put(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update support request: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def upsert_finance_finalization(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/UpsertFinanceFinalization"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to save finance finalization: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_scope_items_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetScopeItemsByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_scope_item(self, scope_item_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/CreateScopeItem"
        try:
            async with self.session.post(url, json=scope_item_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create scope item: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_scope_item(self, scope_item_id, scope_item_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/UpdateScopeItem/{scope_item_id}"
        try:
            async with self.session.put(url, json=scope_item_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update scope item: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_scope_item(self, scope_item_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/DeleteScopeItem/{scope_item_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete scope item: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_risk_control_matrix_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetRiskControlMatrixByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_risk_control_matrix_entry(self, entry_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/CreateRiskControlMatrixEntry"
        try:
            async with self.session.post(url, json=entry_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create risk/control matrix entry: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_risk_control_matrix_entry(self, entry_id, entry_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/UpdateRiskControlMatrixEntry/{entry_id}"
        try:
            async with self.session.put(url, json=entry_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update risk/control matrix entry: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_risk_control_matrix_entry(self, entry_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/DeleteRiskControlMatrixEntry/{entry_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete risk/control matrix entry: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_control_classifications(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetControlClassifications"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_control_types(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetControlTypes"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_control_frequencies(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetControlFrequencies"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_walkthroughs_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetWalkthroughsByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_walkthrough(self, walkthrough_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/CreateWalkthrough"
        try:
            async with self.session.post(url, json=walkthrough_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create walkthrough: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_walkthrough(self, walkthrough_id, walkthrough_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/UpdateWalkthrough/{walkthrough_id}"
        try:
            async with self.session.put(url, json=walkthrough_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update walkthrough: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_walkthrough(self, walkthrough_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/DeleteWalkthrough/{walkthrough_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete walkthrough: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def add_walkthrough_exception(self, exception_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/AddWalkthroughException"
        try:
            async with self.session.post(url, json=exception_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to add walkthrough exception: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_management_actions_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/GetManagementActionsByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def create_management_action(self, action_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/CreateManagementAction"
        try:
            async with self.session.post(url, json=action_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to create management action: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def update_management_action(self, action_id, action_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/UpdateManagementAction/{action_id}"
        try:
            async with self.session.put(url, json=action_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to update management action: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def delete_management_action(self, action_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditExecution/DeleteManagementAction/{action_id}"
        try:
            async with self.session.delete(url) as response:
                if response.status == 200:
                    return True
                error_text = await response.text()
                raise Exception(f"Failed to delete management action: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    # =====================================================
    # AUDIT WORKFLOW METHODS
    # =====================================================

    async def get_workflow_inbox(self, user_id=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/GetInbox"
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return {"workflows": [], "tasks": [], "notifications": []}
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_review_workspace(self, user_id=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReviews/GetWorkspace"
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to load review workspace: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_reviews_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReviews/GetByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_review_notes(self, review_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReviews/GetReviewNotes/{review_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def add_review_note(self, note_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReviews/AddReviewNote"
        try:
            async with self.session.post(url, json=note_data or {}) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to add review note: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_review_signoffs_by_reference(self, reference_id, limit=100):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReviews/GetSignoffsByReference/{reference_id}"
        params = {"limit": limit}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_workflow_instances_by_reference(self, reference_id):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/GetWorkflowInstancesByReference/{reference_id}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_workflow_timeline(self, reference_id, limit=100):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/GetTimeline/{reference_id}"
        params = {"limit": limit}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def record_audit_trail_event(self, event_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditTrail/RecordEvent"
        try:
            async with self.session.post(url, json=event_data) as response:
                if response.status in (200, 201):
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to record audit trail event: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_audit_trail_events(self, reference_id, limit=100):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditTrail/GetByReference/{reference_id}"
        params = {"limit": limit}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_audit_trail_dashboard(self, reference_id, limit=50):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditTrail/GetDashboard/{reference_id}"
        params = {"limit": limit}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_power_bi_reconciliation(self, reference_id=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditReporting/GetPowerBIReconciliation"
        params = {}
        if reference_id is not None:
            params["referenceId"] = reference_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_platform_configuration(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditPlatform/GetClientConfiguration"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to get platform configuration: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_retention_policies(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditPlatform/GetRetentionPolicies"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to get retention policies: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_usage_summary(self, days=30):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditPlatform/GetUsageSummary"
        params = {"days": days}
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to get usage summary: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def record_usage_event(self, event_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditPlatform/RecordUsageEvent"
        try:
            async with self.session.post(url, json=event_data or {}) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to record usage event: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def archive_assessment(self, reference_id, request_data=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditPlatform/ArchiveAssessment/{reference_id}"
        try:
            async with self.session.post(url, json=request_data or {}) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to archive assessment: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def sync_workflow_state(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/SyncElsaState"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to sync workflow state: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def run_workflow_reminder_sweep(self):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/RunReminderSweep"
        try:
            async with self.session.post(url, json={}) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to run workflow reminder sweep: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_workflow_tasks(self, user_id=None, pending_only=False):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/GetTasks"
        params = {"pendingOnly": str(bool(pending_only)).lower()}
        if user_id is not None:
            params["userId"] = user_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def complete_workflow_task(self, task_id, completion_data=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/CompleteTask/{task_id}"
        payload = completion_data or {}
        try:
            async with self.session.put(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to complete workflow task: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def get_workflow_notifications(self, user_id=None, unread_only=False):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/GetNotifications"
        params = {"unreadOnly": str(bool(unread_only)).lower()}
        if user_id is not None:
            params["userId"] = user_id
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def mark_workflow_notification_read(self, notification_id, read_data=None):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/MarkNotificationRead/{notification_id}"
        payload = read_data or {}
        try:
            async with self.session.put(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to mark notification as read: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_planning_approval_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartPlanningApproval"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start planning approval workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_annual_audit_plan_approval_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartAnnualAuditPlanApproval"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start annual audit plan approval workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_scope_approval_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartScopeApproval"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start scope approval workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_walkthrough_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartWalkthrough"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start walkthrough workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_working_paper_review_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartWorkingPaperReview"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start working paper review workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_finding_review_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartFindingReview"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start finding review workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_management_response_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartManagementResponse"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start management response workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_remediation_followup_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartRemediationFollowUp"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start remediation follow-up workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def start_final_report_signoff_workflow(self, request_data):
        await self._ensure_session()
        base = self.base_url.rstrip('/')
        url = f"{base}/AuditWorkflow/StartFinalReportSignOff"
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                raise Exception(f"Failed to start final report sign-off workflow: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")

    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close() 
