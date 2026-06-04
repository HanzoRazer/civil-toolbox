"""Validation utilities for inlet capacity module."""

from __future__ import annotations

from typing import Any

from civil_toolbox.inlets.errors import (
    InletCapacityError,
    InvalidInletInputError,
    MissingInletDataError,
)


# Capture-check status categories.
#   pass          - captured flow >= design flow
#   fail          - captured flow < design flow
#   warning       - evaluated, but a condition warrants attention
#   not_evaluated - capacity could not be evaluated (e.g. missing geometry)
SUPPORTED_STATUSES = {"pass", "fail", "warning", "not_evaluated"}


def require_positive(value: float, field_name: str) -> float:
    """Validate that a value is positive (> 0).

    Raises:
        InvalidInletInputError: If value is not positive.
    """
    if value <= 0:
        raise InvalidInletInputError(f"{field_name} must be positive, got {value}")
    return float(value)


def require_non_negative(value: float, field_name: str) -> float:
    """Validate that a value is non-negative (>= 0).

    Raises:
        InvalidInletInputError: If value is negative.
    """
    if value < 0:
        raise InvalidInletInputError(f"{field_name} cannot be negative, got {value}")
    return float(value)


def require_field(value: Any, field_name: str, entity_id: str | None = None) -> Any:
    """Validate that a required field is not None.

    Raises:
        MissingInletDataError: If value is None.
    """
    if value is None:
        context = f" for '{entity_id}'" if entity_id else ""
        raise MissingInletDataError(f"{field_name} is required{context}")
    return value


def validate_status(status: str) -> str:
    """Validate that a capture-check status is supported.

    Raises:
        InletCapacityError: If status is not supported.
    """
    if status not in SUPPORTED_STATUSES:
        raise InletCapacityError(
            f"status must be one of {sorted(SUPPORTED_STATUSES)}, got '{status}'"
        )
    return status
