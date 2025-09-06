from datetime import datetime


class Assessment:
    """
    Model representing a risk assessment.
    """

    def __init__(self, id=None, title=None, department_id=None, department=None,
                 project_id=None, project=None, auditor_id=None, auditor=None,
                 assessment_date=None, risk_score=None, risk_level=None,
                 scope=None, findings=None, recommendations=None, risk_factors=None,
                 created_at=None, updated_at=None):
        """
        Initialize an assessment object.

        Args:
            id: Unique identifier for the assessment (int or string)
            title: Title of the assessment
            department_id: ID of the department being assessed
            department: Name of the department being assessed
            project_id: ID of the project being assessed
            project: Name of the project being assessed
            auditor_id: ID of the user conducting the assessment
            auditor: Name of the user conducting the assessment
            assessment_date: Date when the assessment was conducted
            risk_score: Numeric risk score (float)
            risk_level: Risk level (High, Medium, Low)
            scope: Assessment scope description
            findings: Assessment findings
            recommendations: Recommendations based on findings
            risk_factors: List of risk factors and their scores
            created_at: Timestamp when the assessment was created
            updated_at: Timestamp when the assessment was last updated
        """
        self.id = id
        self.title = title
        self.department_id = department_id
        self.department = department
        self.project_id = project_id
        self.project = project
        self.auditor_id = auditor_id
        self.auditor = auditor
        self.assessment_date = assessment_date
        self.risk_score = risk_score
        self.risk_level = risk_level
        self.scope = scope
        self.findings = findings
        self.recommendations = recommendations
        self.risk_factors = risk_factors or []
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_json(cls, json_data):
        """
        Create an Assessment instance from JSON data returned by API.

        Args:
            json_data: Dictionary of assessment data from API

        Returns:
            Assessment: Instance of Assessment class
        """
        # Format ID if numeric (e.g., 1 -> "A-001")
        assessment_id = json_data.get("id")
        if isinstance(assessment_id, int):
            assessment_id = f"A-{assessment_id:03d}"

        # Parse dates if they're strings
        assessment_date = json_data.get("assessment_date")
        if isinstance(assessment_date, str):
            try:
                assessment_date = datetime.strptime(assessment_date, "%Y-%m-%d").date()
            except ValueError:
                pass

        created_at = json_data.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, "%Y-%m-%d")
                except ValueError:
                    pass

        updated_at = json_data.get("updated_at")
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    updated_at = datetime.strptime(updated_at, "%Y-%m-%d")
                except ValueError:
                    pass

        # Format risk factors if they're in a different format
        risk_factors = json_data.get("risk_factors", [])
        if isinstance(risk_factors, list):
            # Ensure each risk factor has name and value keys
            formatted_factors = []
            for factor in risk_factors:
                if isinstance(factor, dict):
                    # If factor is already a dict with name and value, use it
                    if "name" in factor and "value" in factor:
                        formatted_factors.append(factor)
                    # If factor uses different keys, convert to standard format
                    elif "factor_name" in factor and "factor_value" in factor:
                        formatted_factors.append({
                            "name": factor["factor_name"],
                            "value": factor["factor_value"],
                            "description": factor.get("description", "")
                        })
            risk_factors = formatted_factors

        return cls(
            id=assessment_id,
            title=json_data.get("title"),
            department_id=json_data.get("department_id"),
            department=json_data.get("department"),
            project_id=json_data.get("project_id"),
            project=json_data.get("project"),
            auditor_id=json_data.get("auditor_id"),
            auditor=json_data.get("auditor"),
            assessment_date=assessment_date,
            risk_score=json_data.get("risk_score"),
            risk_level=json_data.get("risk_level"),
            scope=json_data.get("scope"),
            findings=json_data.get("findings"),
            recommendations=json_data.get("recommendations"),
            risk_factors=risk_factors,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_json(self):
        """
        Convert assessment to JSON for API requests.

        Returns:
            dict: Assessment data as a dictionary
        """
        # Format dates as strings if they're datetime objects
        assessment_date = self.assessment_date
        if hasattr(assessment_date, "strftime"):
            assessment_date = assessment_date.strftime("%Y-%m-%d")

        created_at = self.created_at
        if hasattr(created_at, "strftime"):
            created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

        updated_at = self.updated_at
        if hasattr(updated_at, "strftime"):
            updated_at = updated_at.strftime("%Y-%m-%d %H:%M:%S")

        # Extract numeric ID if it's in "A-001" format
        assessment_id = self.id
        if isinstance(assessment_id, str) and assessment_id.startswith("A-"):
            try:
                assessment_id = int(assessment_id[2:])
            except ValueError:
                pass

        return {
            "id": assessment_id,
            "title": self.title,
            "department_id": self.department_id,
            "department": self.department,
            "project_id": self.project_id,
            "project": self.project,
            "auditor_id": self.auditor_id,
            "auditor": self.auditor,
            "assessment_date": assessment_date,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "scope": self.scope,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "risk_factors": self.risk_factors,
            "created_at": created_at,
            "updated_at": updated_at
        }

    def __str__(self):
        """String representation of the assessment"""
        return f"{self.id}: {self.title} - {self.risk_level} Risk"

    def calculate_risk_score(self):
        """
        Calculate risk score based on risk factors.

        Returns:
            float: Calculated risk score
        """
        if not self.risk_factors:
            return 0.0

        # Extract values from risk factors
        values = []
        for factor in self.risk_factors:
            if isinstance(factor, dict) and "value" in factor:
                try:
                    values.append(float(factor["value"]))
                except (ValueError, TypeError):
                    pass

        if not values:
            return 0.0

        # Calculate average score
        return round(sum(values) / len(values), 2)

    def determine_risk_level(self, score=None):
        """
        Determine risk level based on risk score.

        Args:
            score: Risk score to use (defaults to self.risk_score)

        Returns:
            str: Risk level (High, Medium, Low)
        """
        if score is None:
            score = self.risk_score

        if score is None:
            score = self.calculate_risk_score()

        if score >= 3.5:
            return "High"
        elif score >= 2.0:
            return "Medium"
        else:
            return "Low"

    def update_risk_assessment(self):
        """
        Update risk score and level based on current risk factors.
        """
        self.risk_score = self.calculate_risk_score()
        self.risk_level = self.determine_risk_level(self.risk_score)
