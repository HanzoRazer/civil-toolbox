"""Exception classes for hydraulics module."""

from __future__ import annotations


class HydraulicAnalysisError(ValueError):
    """Base exception for hydraulic analysis."""


class InvalidHydraulicInputError(HydraulicAnalysisError):
    """Raised when hydraulic input data is invalid."""


class MissingHydraulicDataError(HydraulicAnalysisError):
    """Raised when required hydraulic data is missing."""


class UnsupportedHydraulicMethodError(HydraulicAnalysisError):
    """Raised when an unsupported hydraulic method is requested."""
