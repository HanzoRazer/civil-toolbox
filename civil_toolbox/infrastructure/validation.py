"""Validation utilities for infrastructure models."""

from __future__ import annotations

from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


def validate_positive(value: float, field_name: str) -> float:
    """Validate that a value is positive (> 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidInfrastructureError: If value is not positive.
    """
    if value <= 0:
        raise InvalidInfrastructureError(f"{field_name} must be positive, got {value}")
    return float(value)


def validate_non_negative(value: float, field_name: str) -> float:
    """Validate that a value is non-negative (>= 0).

    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidInfrastructureError: If value is negative.
    """
    if value < 0:
        raise InvalidInfrastructureError(f"{field_name} cannot be negative, got {value}")
    return float(value)


def validate_mannings_n(value: float, field_name: str = "mannings_n") -> float:
    """Validate Manning's n roughness coefficient.

    Typical range: 0.008 (smooth) to 0.15 (rough).

    Args:
        value: The Manning's n value.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidInfrastructureError: If value is out of range.
    """
    if value <= 0 or value > 0.5:
        raise InvalidInfrastructureError(
            f"{field_name} must be between 0 and 0.5, got {value}"
        )
    return float(value)


def validate_slope(value: float, field_name: str = "slope_ft_per_ft") -> float:
    """Validate slope as ft/ft (dimensionless).

    Args:
        value: The slope value.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidInfrastructureError: If slope is negative.
    """
    if value < 0:
        raise InvalidInfrastructureError(f"{field_name} cannot be negative, got {value}")
    return float(value)


def validate_pipe_shape(shape: str, field_name: str = "shape") -> str:
    """Validate pipe shape.

    Args:
        shape: The pipe shape string.
        field_name: Name of the field for error messages.

    Returns:
        The normalized (lowercase) shape.

    Raises:
        InvalidInfrastructureError: If shape is invalid.
    """
    normalized = shape.strip().lower()
    valid_shapes = {"circular", "box", "arch", "elliptical"}
    if normalized not in valid_shapes:
        raise InvalidInfrastructureError(
            f"{field_name} must be one of {sorted(valid_shapes)}, got '{shape}'"
        )
    return normalized


def validate_inlet_type(inlet_type: str, field_name: str = "inlet_type") -> str:
    """Validate inlet type.

    Args:
        inlet_type: The inlet type string.
        field_name: Name of the field for error messages.

    Returns:
        The normalized (lowercase) inlet type.

    Raises:
        InvalidInfrastructureError: If inlet type is invalid.
    """
    normalized = inlet_type.strip().lower()
    valid_types = {"grate", "curb_opening", "combination", "slotted"}
    if normalized not in valid_types:
        raise InvalidInfrastructureError(
            f"{field_name} must be one of {sorted(valid_types)}, got '{inlet_type}'"
        )
    return normalized


def validate_channel_shape(shape: str, field_name: str = "shape") -> str:
    """Validate open channel shape.

    Args:
        shape: The channel shape string.
        field_name: Name of the field for error messages.

    Returns:
        The normalized (lowercase) shape.

    Raises:
        InvalidInfrastructureError: If shape is invalid.
    """
    normalized = shape.strip().lower()
    valid_shapes = {"rectangular", "trapezoidal", "triangular", "parabolic"}
    if normalized not in valid_shapes:
        raise InvalidInfrastructureError(
            f"{field_name} must be one of {sorted(valid_shapes)}, got '{shape}'"
        )
    return normalized


def validate_outlet_type(outlet_type: str, field_name: str = "outlet_type") -> str:
    """Validate outlet structure type.

    Args:
        outlet_type: The outlet type string.
        field_name: Name of the field for error messages.

    Returns:
        The normalized (lowercase) outlet type.

    Raises:
        InvalidInfrastructureError: If outlet type is invalid.
    """
    normalized = outlet_type.strip().lower()
    valid_types = {"orifice", "weir", "riser", "culvert", "combined"}
    if normalized not in valid_types:
        raise InvalidInfrastructureError(
            f"{field_name} must be one of {sorted(valid_types)}, got '{outlet_type}'"
        )
    return normalized
