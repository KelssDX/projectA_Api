from datetime import datetime, timezone


class Assessment:
    """
    Model representing a risk assessment.
    """

    @staticmethod
    def _parse_date_value(value):
        if not isinstance(value, str):
            return value

        raw = value.strip()
        if not raw:
            return None

        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
        except ValueError:
            pass

        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue

        return None

    @staticmethod
    def _parse_datetime_value(value):
        if not isinstance(value, str):
            return value

        raw = value.strip()
        if not raw:
            return None

        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except ValueError:
            pass

        for fmt in (
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue

        return None

    def __init__(self, id=None, reference_id=None, title=None, department_id=None, department=None,
                 project_id=None, project=None, auditor_id=None, auditor=None,
                 assessment_date=None, risk_score=None, risk_level=None,
                 scope=None, findings=None, recommendations=None, risk_factors=None,
                 created_at=None, updated_at=None, engagement_type_id=None, engagement_type_name=None):
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
        self.reference_id = reference_id
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
        self.engagement_type_id = engagement_type_id
        self.engagement_type_name = engagement_type_name

    @classmethod
    def from_json(cls, json_data):
        """
        Create an Assessment instance from JSON data returned by API.

        Args:
            json_data: Dictionary of assessment data from API

        Returns:
            Assessment: Instance of Assessment class
        """
        raw_id = json_data.get("id")
        reference_id = (
            json_data.get("reference_id")
            or json_data.get("referenceId")
            or json_data.get("ReferenceId")
        )

        numeric_id = None
        if isinstance(raw_id, int):
            numeric_id = raw_id
        else:
            try:
                numeric_id = int(raw_id) if raw_id is not None else None
            except (TypeError, ValueError):
                if isinstance(raw_id, str) and raw_id.startswith("A-"):
                    try:
                        numeric_id = int(raw_id[2:])
                    except ValueError:
                        numeric_id = None

        if reference_id is None and numeric_id is not None:
            reference_id = numeric_id

        formatted_id = raw_id
        if numeric_id is not None:
            formatted_id = f"A-{numeric_id:03d}"
        elif isinstance(reference_id, int):
            formatted_id = f"A-{reference_id:03d}"

        if formatted_id is None and reference_id is not None:
            formatted_id = f"A-{reference_id:03d}"

        assessment_date = (
            json_data.get("assessment_date")
            or json_data.get("assessmentDate")
        )
        assessment_date = cls._parse_date_value(assessment_date)

        created_at = json_data.get("created_at") or json_data.get("createdAt")
        created_at = cls._parse_datetime_value(created_at)

        updated_at = json_data.get("updated_at") or json_data.get("updatedAt")
        updated_at = cls._parse_datetime_value(updated_at)

        risk_factors = json_data.get("risk_factors") or json_data.get("riskFactors") or []
        if isinstance(risk_factors, list):
            formatted_factors = []
            for factor in risk_factors:
                if isinstance(factor, dict):
                    if "name" in factor and "value" in factor:
                        formatted_factors.append(factor)
                    elif "factor_name" in factor and "factor_value" in factor:
                        formatted_factors.append({
                            "name": factor["factor_name"],
                            "value": factor["factor_value"],
                            "description": factor.get("description", "")
                        })
            risk_factors = formatted_factors

        return cls(
            id=formatted_id,
            reference_id=reference_id,
            title=json_data.get("title") or json_data.get("client"),
            department_id=json_data.get("department_id") or json_data.get("departmentId"),
            department=json_data.get("department"),
            project_id=json_data.get("project_id") or json_data.get("projectId"),
            project=json_data.get("project"),
            auditor_id=json_data.get("auditor_id") or json_data.get("auditorId"),
            auditor=json_data.get("auditor") or json_data.get("assessor"),
            assessment_date=assessment_date,
            risk_score=json_data.get("risk_score") or json_data.get("riskScore"),
            risk_level=json_data.get("risk_level") or json_data.get("riskLevel"),
            scope=json_data.get("scope"),
            findings=json_data.get("findings"),
            recommendations=json_data.get("recommendations"),
            risk_factors=risk_factors,
            created_at=created_at,
            updated_at=updated_at,
            engagement_type_id=json_data.get("engagement_type_id") or json_data.get("engagementTypeId"),
            engagement_type_name=json_data.get("engagement_type_name") or json_data.get("engagementTypeName"),
        )

    def to_json(self):
        """
        Convert assessment to JSON for API requests.

        Returns:
            dict: Assessment data as a dictionary
        """
        assessment_date = self.assessment_date
        if hasattr(assessment_date, "strftime"):
            assessment_date = assessment_date.strftime("%Y-%m-%d")

        created_at = self.created_at
        if hasattr(created_at, "strftime"):
            created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

        updated_at = self.updated_at
        if hasattr(updated_at, "strftime"):
            updated_at = updated_at.strftime("%Y-%m-%d %H:%M:%S")

        numeric_id = self.reference_id
        if numeric_id is None:
            raw_id = self.id
            if isinstance(raw_id, str) and raw_id.startswith("A-"):
                try:
                    numeric_id = int(raw_id[2:])
                except ValueError:
                    numeric_id = None
            elif isinstance(raw_id, int):
                numeric_id = raw_id
            else:
                numeric_id = raw_id

        return {
            "id": numeric_id,
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
            "updated_at": updated_at,
            "reference_id": self.reference_id,
            "engagement_type_id": self.engagement_type_id,
            "engagement_type_name": self.engagement_type_name,
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

