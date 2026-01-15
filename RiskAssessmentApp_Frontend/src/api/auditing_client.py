import aiohttp
import asyncio
import json
from src.core.config import API_CONFIG, get_auditing_api_url
from src.data.mock_data import (
    MOCK_ANALYTICAL_REPORT, 
    MOCK_MARKET_DATA, 
    MOCK_MARKET_METRICS, 
    MOCK_TOP_RISKS
)


class AuditingAPIClient:
    """Client for interacting with the Affine.Auditing.API"""
    
    def __init__(self):
        self.base_url = API_CONFIG["auditing_api"]
        self.timeout = API_CONFIG["timeout"]
        self.verify_ssl = API_CONFIG["verify_ssl"]
        self.session = None
    
    async def _ensure_session(self):
        """Ensure HTTP session is created for the current event loop"""
        current_loop = asyncio.get_event_loop()
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
        elif hasattr(self, '_session_loop') and self._session_loop != current_loop:
            try:
                await self.session.close()
            except:
                pass
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
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
    
    async def get_mock_analytical_report(self):
        return MOCK_ANALYTICAL_REPORT

    async def get_mock_market_data(self):
        return MOCK_MARKET_DATA

    async def get_mock_market_metrics(self):
        return MOCK_MARKET_METRICS

    async def get_mock_top_risks(self):
        return MOCK_TOP_RISKS

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
