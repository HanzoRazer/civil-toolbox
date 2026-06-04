"""Exception classes for inlet capacity module."""

from __future__ import annotations


class InletCapacityError(ValueError):
    """Base exception for inlet capacity analysis."""


class InvalidInletInputError(InletCapacityError):
    """Raised when inlet input data is invalid."""


class MissingInletDataError(InletCapacityError):
    """Raised when required inlet geometry/data is missing."""


class UnsupportedInletTypeError(InletCapacityError):
    """Raised when an inlet type is not supported by the analysis."""
