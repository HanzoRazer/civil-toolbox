"""Validation utilities for infrastructure sizing."""

from __future__ import annotations

from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


def validate_positive_flow(flow_cfs: float, field_name: str = "flow") -> float:
    """Validate that flow is non-negative.

    Args:
        flow_cfs: Flow value in cfs.
        field_name: Name of the field for error messages.

    Returns:
        The validated flow value.

    Raises:
        InvalidSizingInputError: If flow is negative.
    """
    if flow_cfs < 0:
        raise InvalidSizingInputError(
            f"{field_name} cannot be negative, got {flow_cfs}"
        )
    return float(flow_cfs)


def validate_positive_storage(storage_cuft: float, field_name: str = "storage") -> float:
    """Validate that storage is non-negative.

    Args:
        storage_cuft: Storage value in cubic feet.
        field_name: Name of the field for error messages.

    Returns:
        The validated storage value.

    Raises:
        InvalidSizingInputError: If storage is negative.
    """
    if storage_cuft < 0:
        raise InvalidSizingInputError(
            f"{field_name} cannot be negative, got {storage_cuft}"
        )
    return float(storage_cuft)


def validate_mannings_n(n: float, field_name: str = "mannings_n") -> float:
    """Validate Manning's roughness coefficient.

    Args:
        n: Manning's n value.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidSizingInputError: If n is out of valid range.
    """
    if n <= 0 or n > 0.5:
        raise InvalidSizingInputError(
            f"{field_name} must be between 0 and 0.5, got {n}"
        )
    return float(n)


def validate_positive_slope(slope: float, field_name: str = "slope") -> float:
    """Validate that slope is positive (for capacity calculations).

    Args:
        slope: Slope value in ft/ft.
        field_name: Name of the field for error messages.

    Returns:
        The validated slope value.

    Raises:
        InvalidSizingInputError: If slope is not positive.
    """
    if slope <= 0:
        raise InvalidSizingInputError(
            f"{field_name} must be positive for capacity calculation, got {slope}"
        )
    return float(slope)


def validate_positive_dimension(value: float, field_name: str) -> float:
    """Validate that a dimension is positive.

    Args:
        value: Dimension value.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidSizingInputError: If value is not positive.
    """
    if value <= 0:
        raise InvalidSizingInputError(
            f"{field_name} must be positive, got {value}"
        )
    return float(value)
