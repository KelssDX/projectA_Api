import asyncio
from src.api.client import APIClient, APIError


class RiskCalculator:
    def __init__(self):
        self.api_client = APIClient()

    async def calculate_risk_api(self, risk_factors):
        """
        Calculate risk using the backend API

        Args:
            risk_factors: List of dictionaries with 'name' and 'value' keys

        Returns:
            Dictionary with 'risk_score' and 'risk_level'
        """
        try:
            response = await self.api_client.post("risk/calculate", {"factors": risk_factors})
            return response
        except APIError as e:
            # Fall back to local calculation
            print(f"API risk calculation failed: {str(e)}")
            return self.calculate_risk(risk_factors)

    def calculate_risk(self, risk_factors):
        """
        Calculate risk score and level from risk factors

        This is a simplified risk calculation algorithm.
        In a real application, this would be more sophisticated
        and take into account factor weights, dependencies,
        and organization-specific risk criteria.

        Args:
            risk_factors: List of dictionaries with 'name' and 'value' keys

        Returns:
            Dictionary with 'risk_score' and 'risk_level'
        """
        if not risk_factors:
            return {
                "risk_score": 0,
                "risk_level": "Not Applicable"
            }

        # Extract values, assuming they are numeric
        values = [factor.get("value", 0) for factor in risk_factors]

        # Calculate risk score (simple average)
        risk_score = sum(values) / len(values)

        # Determine risk level
        if risk_score < 1.5:
            risk_level = "Very Low"
        elif risk_score < 2.5:
            risk_level = "Low"
        elif risk_score < 3.5:
            risk_level = "Medium"
        elif risk_score < 4.5:
            risk_level = "High"
        else:
            risk_level = "Very High"

        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level
        }

    def get_factor_definition(self, factor_name):
        """
        Get the definition and scoring guide for a risk factor

        Args:
            factor_name: Name of the risk factor

        Returns:
            Dictionary with factor definition and scoring guide
        """
        # This is a simplified set of factor definitions
        # In a real application, these would be loaded from a database
        # or configuration file

        definitions = {
            "Data Sensitivity": {
                "description": "Classification level of data being processed or stored",
                "scoring_guide": {
                    1: "Public Information - Data that can be freely disclosed",
                    2: "Internal Use Only - Data for internal use, minimal impact if disclosed",
                    3: "Confidential - Sensitive data, moderate impact if disclosed",
                    4: "Restricted - Highly sensitive data, significant impact if disclosed",
                    5: "Top Secret - Critical data, severe impact if disclosed"
                }
            },
            "System Criticality": {
                "description": "Importance of the system to business operations",
                "scoring_guide": {
                    1: "Non-Critical - No business impact if system is unavailable",
                    2: "Low Importance - Minimal business impact if system is unavailable",
                    3: "Moderately Important - Noticeable business impact if unavailable for a day",
                    4: "Critical - Significant business impact if unavailable for a few hours",
                    5: "Mission Critical - Severe business impact if unavailable for minutes"
                }
            },
            "Regulatory Impact": {
                "description": "Potential regulatory or compliance impact",
                "scoring_guide": {
                    1: "None - No regulatory requirements apply",
                    2: "Minimal - Few regulatory requirements, minor penalties",
                    3: "Moderate - Multiple regulatory requirements, moderate penalties",
                    4: "Significant - Major regulatory requirements, significant penalties",
                    5: "Severe - Critical regulatory requirements, severe penalties or sanctions"
                }
            },
            "Financial Impact": {
                "description": "Potential financial loss if compromised",
                "scoring_guide": {
                    1: "Negligible - Less than $10,000",
                    2: "Minor - $10,000 to $100,000",
                    3: "Moderate - $100,000 to $1 million",
                    4: "Major - $1 million to $10 million",
                    5: "Severe - Greater than $10 million"
                }
            },
            "Reputation Impact": {
                "description": "Potential damage to organization's reputation",
                "scoring_guide": {
                    1: "Negligible - No impact on reputation",
                    2: "Minor - Limited negative attention",
                    3: "Moderate - Local media coverage, some stakeholder concerns",
                    4: "Major - National media coverage, significant stakeholder concerns",
                    5: "Severe - International media coverage, damaged brand, lost trust"
                }
            }
        }

        return definitions.get(factor_name, {
            "description": "No definition available",
            "scoring_guide": {}
        })

    def get_standard_risk_factors(self):
        """
        Get the standard set of risk factors used in assessments

        Returns:
            List of dictionaries with factor names and descriptions
        """
        return [
            {
                "name": "Data Sensitivity",
                "description": "Classification level of data being processed or stored"
            },
            {
                "name": "System Criticality",
                "description": "Importance of the system to business operations"
            },
            {
                "name": "Regulatory Impact",
                "description": "Potential regulatory or compliance impact"
            },
            {
                "name": "Financial Impact",
                "description": "Potential financial loss if compromised"
            },
            {
                "name": "Reputation Impact",
                "description": "Potential damage to organization's reputation"
            }
        ]
