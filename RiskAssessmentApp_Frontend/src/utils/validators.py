import re
import datetime
from enum import Enum


class ValidationResult:
    """Result of a validation operation."""

    def __init__(self, is_valid=True, errors=None):
        """Initialize validation result.

        Args:
            is_valid: Whether the validation passed
            errors: List of error messages or None
        """
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, error):
        """Add an error message to the result.

        Args:
            error: Error message to add
        """
        self.errors.append(error)
        self.is_valid = False

    def __bool__(self):
        """Boolean representation of validation result.

        Returns:
            bool: True if valid, False otherwise
        """
        return self.is_valid


class RiskLevel(Enum):
    """Enum of valid risk levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Validators:
    """Validation utilities for the risk assessment application."""

    @staticmethod
    def validate_required(value, field_name):
        """Validate that a value is not empty.

        Args:
            value: Value to validate
            field_name: Name of the field (for error message)

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        if value is None or (isinstance(value, str) and value.strip() == ""):
            result.add_error(f"{field_name} is required")

        return result

    @staticmethod
    def validate_string_length(value, field_name, min_length=None, max_length=None):
        """Validate a string's length.

        Args:
            value: String to validate
            field_name: Name of the field (for error message)
            min_length: Minimum length (optional)
            max_length: Maximum length (optional)

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        if value is None:
            return result  # Skip validation if value is None

        if not isinstance(value, str):
            result.add_error(f"{field_name} must be a string")
            return result

        if min_length is not None and len(value) < min_length:
            result.add_error(f"{field_name} must be at least {min_length} characters")

        if max_length is not None and len(value) > max_length:
            result.add_error(f"{field_name} must be at most {max_length} characters")

        return result

    @staticmethod
    def validate_email(email):
        """Validate an email address.

        Args:
            email: Email to validate

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        if not email:
            return result  # Skip validation if email is empty

        # Simple regex for email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email):
            result.add_error("Invalid email address")

        return result

    @staticmethod
    def validate_date(date, field_name="Date"):
        """Validate a date.

        Args:
            date: Date to validate (string, datetime.date, or datetime.datetime)
            field_name: Name of the field (for error message)

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        if not date:
            return result  # Skip validation if date is empty

        # If it's already a date or datetime object
        if isinstance(date, (datetime.date, datetime.datetime)):
            return result

        # If it's a string, try to parse it
        if isinstance(date, str):
            try:
                # Try to parse as YYYY-MM-DD
                datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                result.add_error(f"{field_name} must be in YYYY-MM-DD format")

        else:
            result.add_error(f"{field_name} must be a date")

        return result

    @staticmethod
    def validate_numeric(value, field_name, min_value=None, max_value=None):
        """Validate a numeric value.

        Args:
            value: Numeric value to validate
            field_name: Name of the field (for error message)
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        if value is None:
            return result  # Skip validation if value is None

        # Check if it's a number
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                result.add_error(f"{field_name} must be a number")
                return result

        # Check min/max constraints
        if min_value is not None and value < min_value:
            result.add_error(f"{field_name} must be at least {min_value}")

        if max_value is not None and value > max_value:
            result.add_error(f"{field_name} must be at most {max_value}")

        return result

    @staticmethod
    def validate_risk_level(level):
        """Validate that a risk level is valid.

        Args:
            level: Risk level to validate

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        if not level:
            return result  # Skip validation if level is empty

        valid_levels = [item.value for item in RiskLevel]

        if level not in valid_levels:
            result.add_error(f"Risk level must be one of: {', '.join(valid_levels)}")

        return result

    @staticmethod
    def validate_risk_factors(factors):
        """Validate risk factors.

        Args:
            factors: List of risk factors to validate

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        if not factors:
            return result  # Skip validation if factors is empty

        if not isinstance(factors, list):
            result.add_error("Risk factors must be a list")
            return result

        for i, factor in enumerate(factors):
            if not isinstance(factor, dict):
                result.add_error(f"Risk factor at position {i} must be a dictionary")
                continue

            if "name" not in factor:
                result.add_error(f"Risk factor at position {i} must have a 'name' field")

            if "value" not in factor:
                result.add_error(f"Risk factor at position {i} must have a 'value' field")

            # Validate the value is numeric
            if "value" in factor:
                value_result = Validators.validate_numeric(
                    factor["value"],
                    f"Value for risk factor '{factor.get('name', f'at position {i}')}'"
                )

                if not value_result:
                    for error in value_result.errors:
                        result.add_error(error)

        return result

    @staticmethod
    def validate_assessment(assessment):
        """Validate an entire assessment.

        Args:
            assessment: Assessment object to validate

        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()

        # Check required fields
        for field, name in [
            (assessment.title, "Title"),
            (assessment.department, "Department"),
            (assessment.assessment_date, "Assessment date")
        ]:
            field_result = Validators.validate_required(field, name)
            if not field_result:
                for error in field_result.errors:
                    result.add_error(error)

        # Validate date
        date_result = Validators.validate_date(assessment.assessment_date)
        if not date_result:
            for error in date_result.errors:
                result.add_error(error)

        # Validate risk level if it's set
        if assessment.risk_level:
            level_result = Validators.validate_risk_level(assessment.risk_level)
            if not level_result:
                for error in level_result.errors:
                    result.add_error(error)

        # Validate risk factors if they're set
        if assessment.risk_factors:
            factors_result = Validators.validate_risk_factors(assessment.risk_factors)
            if not factors_result:
                for error in factors_result.errors:
                    result.add_error(error)

        # Validate risk score if it's set
        if assessment.risk_score is not None:
            score_result = Validators.validate_numeric(
                assessment.risk_score,
                "Risk score",
                min_value=0,
                max_value=5
            )
            if not score_result:
                for error in score_result.errors:
                    result.add_error(error)

        return result
