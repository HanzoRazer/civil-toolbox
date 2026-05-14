"""Validation utilities for calculator inputs."""

from typing import Optional


class CalculatorInputError(ValueError):
    """Raised when calculator input fails validation."""

    def __init__(self, message: str, parameter: Optional[str] = None):
        super().__init__(message)
        self.parameter = parameter


def validate_positive(value: float, name: str) -> None:
    """Validate that a value is positive (> 0)."""
    if value <= 0:
        raise CalculatorInputError(
            f"{name} must be positive, got {value}",
            parameter=name,
        )


def validate_non_negative(value: float, name: str) -> None:
    """Validate that a value is non-negative (>= 0)."""
    if value < 0:
        raise CalculatorInputError(
            f"{name} must be non-negative, got {value}",
            parameter=name,
        )


def validate_range(
    value: float,
    name: str,
    min_value: float,
    max_value: float,
    inclusive: bool = True,
) -> None:
    """Validate that a value is within a specified range."""
    if inclusive:
        if value < min_value or value > max_value:
            raise CalculatorInputError(
                f"{name} must be between {min_value} and {max_value}, got {value}",
                parameter=name,
            )
    else:
        if value <= min_value or value >= max_value:
            raise CalculatorInputError(
                f"{name} must be between {min_value} and {max_value} (exclusive), "
                f"got {value}",
                parameter=name,
            )


def validate_runoff_coefficient(c: float) -> None:
    """Validate runoff coefficient (0 < C <= 1)."""
    if c <= 0 or c > 1:
        raise CalculatorInputError(
            f"Runoff coefficient must be between 0 (exclusive) and 1 (inclusive), "
            f"got {c}",
            parameter="runoff_coefficient",
        )


def validate_curve_number(cn: float) -> None:
    """Validate SCS curve number (0 < CN <= 100)."""
    if cn <= 0 or cn > 100:
        raise CalculatorInputError(
            f"Curve number must be between 0 (exclusive) and 100 (inclusive), "
            f"got {cn}",
            parameter="curve_number",
        )


def validate_slope_percent(slope: float) -> None:
    """Validate slope as percentage (> 0)."""
    if slope <= 0:
        raise CalculatorInputError(
            f"Slope must be positive, got {slope}%",
            parameter="slope_percent",
        )


def validate_mannings_n(n: float) -> None:
    """Validate Manning's roughness coefficient (typical range 0.01-0.8)."""
    if n <= 0:
        raise CalculatorInputError(
            f"Manning's n must be positive, got {n}",
            parameter="mannings_n",
        )
    if n > 1.0:
        raise CalculatorInputError(
            f"Manning's n is unusually high (> 1.0), got {n}. "
            f"Typical values are 0.01-0.8.",
            parameter="mannings_n",
        )
