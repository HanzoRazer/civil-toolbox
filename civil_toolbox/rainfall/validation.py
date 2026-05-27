"""Validation utilities for rainfall IDF data.

Provides consistent validation for IDF curve inputs.
"""

from civil_toolbox.rainfall.errors import InvalidIDFDataError


def require_positive(value: float, field_name: str) -> float:
    """Require a value to be positive (> 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidIDFDataError: If value is not positive.
    """
    if value <= 0:
        raise InvalidIDFDataError(f"{field_name} must be positive, got {value}")
    return value


def require_non_negative(value: float, field_name: str) -> float:
    """Require a value to be non-negative (>= 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidIDFDataError: If value is negative.
    """
    if value < 0:
        raise InvalidIDFDataError(f"{field_name} cannot be negative, got {value}")
    return value


def validate_return_period(return_period_years: int) -> int:
    """Validate a return period value.

    Args:
        return_period_years: Return period in years.

    Returns:
        The validated return period.

    Raises:
        InvalidIDFDataError: If return period is not positive.
    """
    if not isinstance(return_period_years, int):
        raise InvalidIDFDataError(
            f"return_period_years must be an integer, got {type(return_period_years).__name__}"
        )
    if return_period_years <= 0:
        raise InvalidIDFDataError(
            f"return_period_years must be positive, got {return_period_years}"
        )
    return return_period_years


def validate_duration_minutes(duration_minutes: float) -> float:
    """Validate a duration value in minutes.

    Args:
        duration_minutes: Duration in minutes.

    Returns:
        The validated duration.

    Raises:
        InvalidIDFDataError: If duration is not positive.
    """
    if duration_minutes <= 0:
        raise InvalidIDFDataError(
            f"duration_minutes must be positive, got {duration_minutes}"
        )
    return float(duration_minutes)


def validate_intensity_in_per_hr(intensity: float) -> float:
    """Validate a rainfall intensity value.

    Args:
        intensity: Rainfall intensity in inches per hour.

    Returns:
        The validated intensity.

    Raises:
        InvalidIDFDataError: If intensity is negative.
    """
    if intensity < 0:
        raise InvalidIDFDataError(
            f"rainfall_intensity_in_per_hr cannot be negative, got {intensity}"
        )
    return float(intensity)


def validate_depth_in(depth: float | None) -> float | None:
    """Validate an optional rainfall depth value.

    Args:
        depth: Rainfall depth in inches, or None.

    Returns:
        The validated depth, or None.

    Raises:
        InvalidIDFDataError: If depth is negative.
    """
    if depth is None:
        return None
    if depth < 0:
        raise InvalidIDFDataError(f"rainfall_depth_in cannot be negative, got {depth}")
    return float(depth)
