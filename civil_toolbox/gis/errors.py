"""Exception classes for GIS module."""

from __future__ import annotations


class GISError(ValueError):
    """Base exception for GIS module."""


class InvalidGeometryError(GISError):
    """Raised when geometry data is invalid."""


class InvalidGeoJSONError(GISError):
    """Raised when GeoJSON data is invalid or malformed."""


class SpatialLinkError(GISError):
    """Raised when spatial feature linking fails."""
