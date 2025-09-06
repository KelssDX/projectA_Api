import aiohttp
import json
from src.core.config import API_CONFIG, get_auditing_api_url


class AuditingAPIClient:
    """Client for interacting with the Affine.Auditing.API"""
    
    def __init__(self):
        self.base_url = API_CONFIG["auditing_api"]
        self.timeout = API_CONFIG["timeout"]
        self.verify_ssl = API_CONFIG["verify_ssl"]
        self.session = None
    
    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
    
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
    
    async def get_assessments(self):
        """Get all risk assessments"""
        await self._ensure_session()
        
        url = get_auditing_api_url("get_assessments")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    raw = await response.json()
                    if not isinstance(raw, list):
                        return []
                    normalized = []
                    for item in raw:
                        if not isinstance(item, dict):
                            continue
                        normalized.append({
                            "id": item.get("id"),
                            "title": item.get("title") or item.get("name"),
                            "department_id": item.get("department_id"),
                            "department": item.get("department"),
                            "project_id": item.get("project_id"),
                            "project": item.get("project"),
                            "auditor_id": item.get("auditor_id"),
                            "auditor": item.get("auditor"),
                            "assessment_date": item.get("assessment_date"),
                            "risk_score": item.get("risk_score"),
                            "risk_level": item.get("risk_level"),
                            "scope": item.get("scope"),
                            "findings": item.get("findings"),
                            "recommendations": item.get("recommendations"),
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
                    return await response.json()
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
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get projects: {error_text}")

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
