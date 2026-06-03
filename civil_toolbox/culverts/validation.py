"""Validation utilities for culvert analysis module."""

from __future__ import annotations

from typing import Any

from civil_toolbox.culverts.errors import (
    CulvertAnalysisError,
    InvalidCulvertInputError,
)


SUPPORTED_SEVERITIES = {"info", "warning", "error"}

# Control evaluation status categories.
#   unknown       - status could not be determined
#   passes        - headwater within the allowable limit
#   exceeds        - headwater exceeds the allowable limit
#   not_evaluated - control was intentionally not evaluated (e.g. missing data)
SUPPORTED_CONTROL_STATUSES = {
    "unknown",
    "passes",
    "exceeds",
    "not_evaluated",
}

# Governing-control labels for the result.
SUPPORTED_GOVERNING_CONTROLS = {"inlet", "outlet", "unknown"}


def require_positive(value: float, field_name: str) -> float:
    """Validate that a value is positive (> 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value as a float.

    Raises:
        InvalidCulvertInputError: If value is not positive.
    """
    if value <= 0:
        raise InvalidCulvertInputError(f"{field_name} must be positive, got {value}")
    return float(value)


def require_non_negative(value: float, field_name: str) -> float:
    """Validate that a value is non-negative (>= 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value as a float.

    Raises:
        InvalidCulvertInputError: If value is negative.
    """
    if value < 0:
        raise InvalidCulvertInputError(f"{field_name} cannot be negative, got {value}")
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
        InvalidCulvertInputError: If value is None.
    """
    if value is None:
        context = f" for '{entity_id}'" if entity_id else ""
        raise InvalidCulvertInputError(f"{field_name} is required{context}")
    return value


def validate_severity(severity: str) -> str:
    """Validate that a severity value is supported.

    Args:
        severity: The severity string.

    Returns:
        The validated severity.

    Raises:
        CulvertAnalysisError: If severity is not supported.
    """
    if severity not in SUPPORTED_SEVERITIES:
        raise CulvertAnalysisError(
            f"severity must be one of {sorted(SUPPORTED_SEVERITIES)}, got '{severity}'"
        )
    return severity


def validate_control_status(status: str) -> str:
    """Validate that a control status is supported.

    Args:
        status: The control status string.

    Returns:
        The validated status.

    Raises:
        CulvertAnalysisError: If status is not supported.
    """
    if status not in SUPPORTED_CONTROL_STATUSES:
        raise CulvertAnalysisError(
            f"control status must be one of {sorted(SUPPORTED_CONTROL_STATUSES)}, "
            f"got '{status}'"
        )
    return status


def validate_governing_control(control: str) -> str:
    """Validate that a governing-control label is supported.

    Args:
        control: The governing-control label.

    Returns:
        The validated label.

    Raises:
        CulvertAnalysisError: If the label is not supported.
    """
    if control not in SUPPORTED_GOVERNING_CONTROLS:
        raise CulvertAnalysisError(
            f"governing control must be one of {sorted(SUPPORTED_GOVERNING_CONTROLS)}, "
            f"got '{control}'"
        )
    return control
