"""Exception classes for culvert analysis module."""

from __future__ import annotations


class CulvertAnalysisError(ValueError):
    """Base exception for culvert analysis."""


class InvalidCulvertInputError(CulvertAnalysisError):
    """Raised when culvert input data is invalid or insufficient."""


class UnsupportedCulvertTypeError(CulvertAnalysisError):
    """Raised when a culvert shape/type is not supported by the analysis."""
