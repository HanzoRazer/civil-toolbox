"""Validation utilities for hydraulics module."""

from __future__ import annotations

from typing import Any

from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError, MissingHydraulicDataError


SUPPORTED_SEVERITIES = {"info", "warning", "error"}

SUPPORTED_SURCHARGE_STATUSES = {
    "free_surface",
    "pressurized",
    "surcharged_above_crown",
    "surcharged_above_rim",
    "unknown",
}


def require_positive(value: float, field_name: str) -> float:
    """Validate that a value is positive (> 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidHydraulicInputError: If value is not positive.
    """
    if value <= 0:
        raise InvalidHydraulicInputError(f"{field_name} must be positive, got {value}")
    return float(value)


def require_non_negative(value: float, field_name: str) -> float:
    """Validate that a value is non-negative (>= 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidHydraulicInputError: If value is negative.
    """
    if value < 0:
        raise InvalidHydraulicInputError(f"{field_name} cannot be negative, got {value}")
    return float(value)


def require_field(value: Any, field_name: str, entity_id: str | None = None) -> Any:
    """Validate that a required field is not None.

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.
        entity_id: Optional entity ID for context.

    Returns:
        The validated value.

    Raises:
        MissingHydraulicDataError: If value is None.
    """
    if value is None:
        context = f" for '{entity_id}'" if entity_id else ""
        raise MissingHydraulicDataError(f"{field_name} is required{context}")
    return value


def validate_severity(severity: str) -> str:
    """Validate that a severity value is supported.

    Args:
        severity: The severity string.

    Returns:
        The validated severity.

    Raises:
        InvalidHydraulicInputError: If severity is not supported.
    """
    if severity not in SUPPORTED_SEVERITIES:
        raise InvalidHydraulicInputError(
            f"severity must be one of {sorted(SUPPORTED_SEVERITIES)}, got '{severity}'"
        )
    return severity


def validate_surcharge_status(status: str) -> str:
    """Validate that a surcharge status is supported.

    Args:
        status: The surcharge status string.

    Returns:
        The validated status.

    Raises:
        InvalidHydraulicInputError: If status is not supported.
    """
    if status not in SUPPORTED_SURCHARGE_STATUSES:
        raise InvalidHydraulicInputError(
            f"surcharge_status must be one of {sorted(SUPPORTED_SURCHARGE_STATUSES)}, "
            f"got '{status}'"
        )
    return status
