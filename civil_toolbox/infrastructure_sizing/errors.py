"""Exception classes for infrastructure sizing."""

from __future__ import annotations


class InfrastructureSizingError(Exception):
    """Base exception for infrastructure sizing module."""


class InvalidSizingInputError(InfrastructureSizingError, ValueError):
    """Raised when sizing input is invalid."""


class CapacityCalculationError(InfrastructureSizingError):
    """Raised when capacity calculation fails."""
