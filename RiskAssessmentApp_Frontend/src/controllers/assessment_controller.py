import asyncio
from src.api.auditing_client import AuditingAPIClient
from src.utils.db import Database
from src.api.risk_calculator import RiskCalculator


class AssessmentController:
    def __init__(self, current_user=None):
        self.auditing_client = AuditingAPIClient()
        self.auditing_client.set_current_user(current_user)
        self.risk_calculator = RiskCalculator()

    async def get_risk_assessment(self, reference_id):
        """
        Get a risk assessment by reference ID from the backend API

        Args:
            reference_id: ID of the risk assessment reference

        Returns:
            Risk assessment object if found, None otherwise
        """
        try:
            # Use the Auditing API
            assessment_data = await self.auditing_client.get_risk_assessment(reference_id)
            return assessment_data
            
        except Exception as e:
            print(f"Failed to get risk assessment: {str(e)}")
            return None

    async def create_risk_assessment(self, assessment_data):
        """
        Create a new risk assessment using the backend API

        Args:
            assessment_data: Dictionary containing risk assessment data
                Should follow the RiskAssessmentCreateWrapper structure

        Returns:
            Created assessment response if successful, None otherwise
        """
        try:
            # Use the Auditing API
            result = await self.auditing_client.create_risk_assessment(assessment_data)
            return result
            
        except Exception as e:
            print(f"Failed to create risk assessment: {str(e)}")
            return None

    async def update_risk_assessment(self, reference_id, update_data):
        """
        Update an existing risk assessment using the backend API

        Args:
            reference_id: ID of the risk assessment reference
            update_data: List of RiskAssessmentUpdateRequest objects

        Returns:
            Updated assessment response if successful, None otherwise
        """
        try:
            # Use the Auditing API
            result = await self.auditing_client.update_risk_assessment(reference_id, update_data)
            return result
            
        except Exception as e:
            print(f"Failed to update risk assessment: {str(e)}")
            return None

    async def create_reference(self, reference_data):
        """
        Create a new risk assessment reference

        Args:
            reference_data: Dictionary containing reference data

        Returns:
            Created reference response if successful, None otherwise
        """
        try:
            # Use the Auditing API
            result = await self.auditing_client.create_reference(reference_data)
            return result
            
        except Exception as e:
            print(f"Failed to create reference: {str(e)}")
            return None

    async def start_control_testing(self, reference_id, testing_data):
        """
        Start control testing for a risk assessment

        Args:
            reference_id: ID of the risk assessment reference
            testing_data: Dictionary containing control testing data

        Returns:
            Control testing response if successful, None otherwise
        """
        try:
            # Use the Auditing API
            result = await self.auditing_client.start_control_testing(reference_id, testing_data)
            return result
            
        except Exception as e:
            print(f"Failed to start control testing: {str(e)}")
            return None

    async def get_heatmap_data(self, reference_id):
        """
        Get risk heatmap data for a reference

        Args:
            reference_id: ID of the risk assessment reference

        Returns:
            Heatmap data if found, None otherwise
        """
        try:
            # Use the Auditing API
            heatmap_data = await self.auditing_client.get_heatmap(reference_id)
            return heatmap_data
            
        except Exception as e:
            print(f"Failed to get heatmap data: {str(e)}")
            return None

    # Lookup data methods
    async def get_risks(self):
        """Get all available risks from the API"""
        try:
            return await self.auditing_client.get_risks()
        except Exception as e:
            print(f"Failed to get risks: {str(e)}")
            return []

    async def get_controls(self):
        """Get all available controls from the API"""
        try:
            return await self.auditing_client.get_controls()
        except Exception as e:
            print(f"Failed to get controls: {str(e)}")
            return []

    async def get_outcomes(self):
        """Get all available outcomes from the API"""
        try:
            return await self.auditing_client.get_outcomes()
        except Exception as e:
            print(f"Failed to get outcomes: {str(e)}")
            return []

    async def get_risk_likelihoods(self):
        """Get all available risk likelihoods from the API"""
        try:
            return await self.auditing_client.get_risk_likelihoods()
        except Exception as e:
            print(f"Failed to get risk likelihoods: {str(e)}")
            return []

    async def get_impacts(self):
        """Get all available impacts from the API"""
        try:
            return await self.auditing_client.get_impacts()
        except Exception as e:
            print(f"Failed to get impacts: {str(e)}")
            return []

    async def get_key_secondary_risks(self):
        """Get all available key secondary risks from the API"""
        try:
            return await self.auditing_client.get_key_secondary_risks()
        except Exception as e:
            print(f"Failed to get key secondary risks: {str(e)}")
            return []

    async def get_risk_categories(self):
        """Get all available risk categories from the API"""
        try:
            return await self.auditing_client.get_risk_categories()
        except Exception as e:
            print(f"Failed to get risk categories: {str(e)}")
            return []

    async def get_data_frequencies(self):
        """Get all available data frequencies from the API"""
        try:
            return await self.auditing_client.get_data_frequencies()
        except Exception as e:
            print(f"Failed to get data frequencies: {str(e)}")
            return []

    async def get_outcome_likelihoods(self):
        """Get all available outcome likelihoods from the API"""
        try:
            return await self.auditing_client.get_outcome_likelihoods()
        except Exception as e:
            print(f"Failed to get outcome likelihoods: {str(e)}")
            return []

    async def get_evidence(self):
        """Get all available evidence from the API"""
        try:
            return await self.auditing_client.get_evidence()
        except Exception as e:
            print(f"Failed to get evidence: {str(e)}")
            return []

    # Legacy methods for backward compatibility (fall back to database)
    async def get_assessments(self, filters=None):
        """
        Get list of assessments with optional filtering
        
        Note: This method falls back to database queries since the API
        doesn't have a general "get assessments" endpoint.

        Args:
            filters: Dictionary of filter criteria (optional)

        Returns:
            List of assessment objects
        """
        try:
            query = """
            SELECT 
                a.id,
                a.title,
                a.department_id,
                d.name AS department,
                a.project_id,
                p.name AS project,
                a.auditor_id,
                u.name AS auditor,
                a.assessment_date,
                a.risk_score,
                a.risk_level,
                a.scope,
                a.findings,
                a.recommendations,
                a.created_at,
                a.updated_at
            FROM 
                assessments a
            LEFT JOIN 
                departments d ON a.department_id = d.id
            LEFT JOIN 
                projects p ON a.project_id = p.id
            LEFT JOIN 
                users u ON a.auditor_id = u.id
            """

            # Build WHERE clause for filters
            where_clauses = []
            params = []
            param_idx = 1

            if filters:
                if filters.get("department_id"):
                    where_clauses.append(f"a.department_id = ${param_idx}")
                    params.append(filters["department_id"])
                    param_idx += 1

                if filters.get("project_id"):
                    where_clauses.append(f"a.project_id = ${param_idx}")
                    params.append(filters["project_id"])
                    param_idx += 1

                if filters.get("risk_level"):
                    where_clauses.append(f"a.risk_level = ${param_idx}")
                    params.append(filters["risk_level"])
                    param_idx += 1

                if filters.get("auditor_id"):
                    where_clauses.append(f"a.auditor_id = ${param_idx}")
                    params.append(filters["auditor_id"])
                    param_idx += 1

                if filters.get("from_date"):
                    where_clauses.append(f"a.assessment_date >= ${param_idx}")
                    params.append(filters["from_date"])
                    param_idx += 1

                if filters.get("to_date"):
                    where_clauses.append(f"a.assessment_date <= ${param_idx}")
                    params.append(filters["to_date"])
                    param_idx += 1

                if filters.get("search"):
                    where_clauses.append(
                        f"(a.title ILIKE ${param_idx} OR d.name ILIKE ${param_idx} OR p.name ILIKE ${param_idx})")
                    params.append(f"%{filters['search']}%")
                    param_idx += 1

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY a.assessment_date DESC"

            # Execute query
            rows = await Database.fetch(query, *params)

            # Convert rows to assessment objects
            assessments = []
            for row in rows:
                assessment = dict(row)
                assessment["id"] = f"A-{assessment['id']:03d}"  # Format ID as A-001
                assessment["date"] = assessment["assessment_date"].strftime("%Y-%m-%d")
                assessments.append(assessment)

            return assessments

        except Exception as db_error:
            print(f"Database get assessments failed: {str(db_error)}")
            return []

    async def get_assessment(self, assessment_id):
        """
        Get a single assessment by ID
        
        Note: This method falls back to database queries for legacy format

        Args:
            assessment_id: ID of the assessment to retrieve

        Returns:
            Assessment object if found, None otherwise
        """
        try:
            # Extract numeric ID from format A-001
            if assessment_id.startswith("A-"):
                numeric_id = int(assessment_id[2:])
            else:
                numeric_id = int(assessment_id)

            query = """
            SELECT 
                a.id,
                a.title,
                a.department_id,
                d.name AS department,
                a.project_id,
                p.name AS project,
                a.auditor_id,
                u.name AS auditor,
                a.assessment_date,
                a.risk_score,
                a.risk_level,
                a.scope,
                a.findings,
                a.recommendations,
                a.created_at,
                a.updated_at
            FROM 
                assessments a
            LEFT JOIN 
                departments d ON a.department_id = d.id
            LEFT JOIN 
                projects p ON a.project_id = p.id
            LEFT JOIN 
                users u ON a.auditor_id = u.id
            WHERE
                a.id = $1
            """

            row = await Database.fetchrow(query, numeric_id)

            if row:
                assessment = dict(row)
                assessment["id"] = f"A-{assessment['id']:03d}"  # Format ID as A-001
                assessment["date"] = assessment["assessment_date"].strftime("%Y-%m-%d")

                # Get risk factors
                factors_query = """
                SELECT factor_name, factor_value
                FROM risk_factors
                WHERE assessment_id = $1
                """

                factors = await Database.fetch(factors_query, numeric_id)
                assessment["risk_factors"] = [dict(f) for f in factors]

                return assessment

            return None

        except Exception as db_error:
            print(f"Database get assessment failed: {str(db_error)}")
            return None

    async def calculate_risk_level(self, risk_factors):
        """
        Calculate risk level based on provided risk factors

        Args:
            risk_factors: List of dictionaries with 'name' and 'value' keys

        Returns:
            Dictionary with 'risk_score' and 'risk_level'
        """
        # Use local calculation (API doesn't have a specific risk calculation endpoint)
        return self.risk_calculator.calculate_risk(risk_factors)

    async def delete_assessment(self, assessment_id):
        """
        Delete an assessment
        
        Note: This method falls back to database operations since the API
        doesn't have a delete endpoint.

        Args:
            assessment_id: ID of the assessment to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract numeric ID from format A-001
            if assessment_id.startswith("A-"):
                numeric_id = int(assessment_id[2:])
            else:
                numeric_id = int(assessment_id)

            # Start a transaction
            async with Database.get_pool().acquire() as conn:
                async with conn.transaction():
                    # Delete risk factors first (foreign key constraint)
                    await conn.execute(
                        "DELETE FROM risk_factors WHERE assessment_id = $1",
                        numeric_id
                    )

                    # Delete assessment
                    await conn.execute(
                        "DELETE FROM assessments WHERE id = $1",
                        numeric_id
                    )

            return True

        except Exception as db_error:
            print(f"Database delete assessment failed: {str(db_error)}")
            return False

    def _build_query_params(self, filters):
        """Helper to build query string from filter dictionary"""
        params = []
        for key, value in filters.items():
            if value is not None:
                params.append(f"{key}={value}")

        return "&".join(params)

    async def close(self):
        """Close API connections"""
        try:
            await self.auditing_client.close()
        except Exception as e:
            print(f"Error closing API connections: {str(e)}")
