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


def validate_non_empty_string(value: str, field_name: str) -> str:
    """Validate that a string is non-empty.

    Args:
        value: The string to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated string (stripped).

    Raises:
        InvalidGeometryError: If value is empty or not a string.
    """
    if not isinstance(value, str):
        raise InvalidGeometryError(f"{field_name} must be a string, got {type(value).__name__}")
    stripped = value.strip()
    if not stripped:
        raise InvalidGeometryError(f"{field_name} cannot be empty")
    return stripped


def validate_geometry_type(geometry_type: str) -> str:
    """Validate that a geometry type is supported.

    Args:
        geometry_type: The geometry type string.

    Returns:
        The validated geometry type.

    Raises:
        InvalidGeometryError: If geometry type is not supported.
    """
    if geometry_type not in SUPPORTED_GEOMETRY_TYPES:
        raise InvalidGeometryError(
            f"geometry_type must be one of {sorted(SUPPORTED_GEOMETRY_TYPES)}, "
            f"got '{geometry_type}'"
        )
    return geometry_type


def validate_feature_role(feature_role: str) -> str:
    """Validate that a feature role is supported.

    Args:
        feature_role: The feature role string.

    Returns:
        The validated feature role.

    Raises:
        InvalidGeometryError: If feature role is not supported.
    """
    if feature_role not in SUPPORTED_FEATURE_ROLES:
        raise InvalidGeometryError(
            f"feature_role must be one of {sorted(SUPPORTED_FEATURE_ROLES)}, "
            f"got '{feature_role}'"
        )
    return feature_role


def validate_point_coordinates(coordinates: Any) -> list[float]:
    """Validate Point coordinates.

    Point coordinates must be a list/tuple of at least 2 numeric values [x, y]
    or [x, y, z].

    Args:
        coordinates: The coordinates to validate.

    Returns:
        Validated coordinates as list of floats.

    Raises:
        InvalidGeometryError: If coordinates are invalid.
    """
    if not isinstance(coordinates, (list, tuple)):
        raise InvalidGeometryError(
            f"Point coordinates must be a list or tuple, got {type(coordinates).__name__}"
        )
    if len(coordinates) < 2:
        raise InvalidGeometryError(
            f"Point coordinates must have at least 2 values [x, y], got {len(coordinates)}"
        )
    try:
        return [float(c) for c in coordinates]
    except (TypeError, ValueError) as e:
        raise InvalidGeometryError(f"Point coordinates must be numeric: {e}") from e


def validate_linestring_coordinates(coordinates: Any) -> list[list[float]]:
    """Validate LineString coordinates.

    LineString coordinates must be a list of at least 2 points.

    Args:
        coordinates: The coordinates to validate.

    Returns:
        Validated coordinates as list of point lists.

    Raises:
        InvalidGeometryError: If coordinates are invalid.
    """
    if not isinstance(coordinates, (list, tuple)):
        raise InvalidGeometryError(
            f"LineString coordinates must be a list, got {type(coordinates).__name__}"
        )
    if len(coordinates) < 2:
        raise InvalidGeometryError(
            f"LineString must have at least 2 points, got {len(coordinates)}"
        )
    validated = []
    for i, point in enumerate(coordinates):
        try:
            validated.append(validate_point_coordinates(point))
        except InvalidGeometryError as e:
            raise InvalidGeometryError(f"LineString point {i}: {e}") from e
    return validated


def validate_polygon_coordinates(coordinates: Any) -> list[list[list[float]]]:
    """Validate Polygon coordinates.

    Polygon coordinates must be a list of rings, where each ring is a list
    of at least 4 points with the first and last point being equal (closed).

    Args:
        coordinates: The coordinates to validate.

    Returns:
        Validated coordinates as list of ring lists.

    Raises:
        InvalidGeometryError: If coordinates are invalid or rings are not closed.
    """
    if not isinstance(coordinates, (list, tuple)):
        raise InvalidGeometryError(
            f"Polygon coordinates must be a list of rings, got {type(coordinates).__name__}"
        )
    if len(coordinates) < 1:
        raise InvalidGeometryError("Polygon must have at least one ring")

    validated = []
    for ring_idx, ring in enumerate(coordinates):
        if not isinstance(ring, (list, tuple)):
            raise InvalidGeometryError(
                f"Polygon ring {ring_idx} must be a list, got {type(ring).__name__}"
            )
        if len(ring) < 4:
            raise InvalidGeometryError(
                f"Polygon ring {ring_idx} must have at least 4 points, got {len(ring)}"
            )

        validated_ring = []
        for point_idx, point in enumerate(ring):
            try:
                validated_ring.append(validate_point_coordinates(point))
            except InvalidGeometryError as e:
                raise InvalidGeometryError(
                    f"Polygon ring {ring_idx} point {point_idx}: {e}"
                ) from e

        first = validated_ring[0]
        last = validated_ring[-1]
        if first[0] != last[0] or first[1] != last[1]:
            raise InvalidGeometryError(
                f"Polygon ring {ring_idx} is not closed: first point {first[:2]} "
                f"does not match last point {last[:2]}"
            )

        validated.append(validated_ring)

    return validated
