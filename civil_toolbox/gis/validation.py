"""Validation utilities for GIS models."""

from __future__ import annotations

from typing import Any

from civil_toolbox.gis.errors import InvalidGeometryError


SUPPORTED_GEOMETRY_TYPES = {"Point", "LineString", "Polygon"}

SUPPORTED_FEATURE_ROLES = {
    "drainage_area",
    "flow_path",
    "infrastructure_node",
    "infrastructure_link",
    "project_boundary",
    "reference",
    "other",
}
