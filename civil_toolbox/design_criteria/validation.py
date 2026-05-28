"""Validation utilities for design criteria data.

Provides consistent validation for runoff coefficients, curve numbers,
and soil groups.
"""

from civil_toolbox.design_criteria.errors import InvalidDesignCriteriaError


VALID_SOIL_GROUPS = frozenset({"A", "B", "C", "D"})


def normalize_land_use_key(value: str) -> str:
    """Normalize a land use key for consistent lookup.

    Converts to lowercase, strips whitespace, and replaces spaces
    with underscores.

    Args:
        value: The land use key to normalize.

    Returns:
        Normalized land use key.

    Example:
        >>> normalize_land_use_key("  Asphalt  ")
        'asphalt'
        >>> normalize_land_use_key("Open Space Good")
        'open_space_good'
    """
    return value.strip().lower().replace(" ", "_")


def validate_runoff_coefficient(value: float, field_name: str = "runoff_coefficient") -> float:
    """Validate a runoff coefficient value.

    Args:
        value: The coefficient to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated coefficient.

    Raises:
        InvalidDesignCriteriaError: If coefficient is outside 0-1 range.
    """
    if value < 0 or value > 1:
        raise InvalidDesignCriteriaError(
            f"{field_name} must be between 0 and 1, got {value}"
        )
    return float(value)


def validate_curve_number(value: int, field_name: str = "curve_number") -> int:
    """Validate a curve number value.

    Args:
        value: The curve number to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated curve number.

    Raises:
        InvalidDesignCriteriaError: If curve number is outside 1-100 range.
    """
    if not isinstance(value, int):
        raise InvalidDesignCriteriaError(
            f"{field_name} must be an integer, got {type(value).__name__}"
        )
    if value <= 0 or value > 100:
        raise InvalidDesignCriteriaError(
            f"{field_name} must be between 1 and 100, got {value}"
        )
    return value


def validate_soil_group(value: str, field_name: str = "soil_group") -> str:
    """Validate a hydrologic soil group.

    Args:
        value: The soil group to validate (A, B, C, or D).
        field_name: Name of the field for error messages.

    Returns:
        The validated soil group (uppercase).

    Raises:
        InvalidDesignCriteriaError: If soil group is not A, B, C, or D.
    """
    normalized = value.upper().strip()
    if normalized not in VALID_SOIL_GROUPS:
        raise InvalidDesignCriteriaError(
            f"{field_name} must be one of {sorted(VALID_SOIL_GROUPS)}, got '{value}'"
        )
    return normalized


def validate_return_period(value: int, field_name: str = "return_period_years") -> int:
    """Validate a return period value.

    Args:
        value: The return period in years.
        field_name: Name of the field for error messages.

    Returns:
        The validated return period.

    Raises:
        InvalidDesignCriteriaError: If return period is not positive.
    """
    if not isinstance(value, int):
        raise InvalidDesignCriteriaError(
            f"{field_name} must be an integer, got {type(value).__name__}"
        )
    if value <= 0:
        raise InvalidDesignCriteriaError(
            f"{field_name} must be positive, got {value}"
        )
    return value


def validate_duration_minutes(value: float, field_name: str = "duration_minutes") -> float:
    """Validate a duration value in minutes.

    Args:
        value: The duration in minutes.
        field_name: Name of the field for error messages.

    Returns:
        The validated duration.

    Raises:
        InvalidDesignCriteriaError: If duration is not positive.
    """
    if value <= 0:
        raise InvalidDesignCriteriaError(
            f"{field_name} must be positive, got {value}"
        )
    return float(value)
