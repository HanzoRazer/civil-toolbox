"""Geometry model for GIS features."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from civil_toolbox.gis.errors import InvalidGeometryError
from civil_toolbox.gis.validation import (
    validate_geometry_type,
    validate_point_coordinates,
    validate_linestring_coordinates,
    validate_polygon_coordinates,
)


@dataclass
class Geometry:
    """A GeoJSON-compatible geometry.

    Supports Point, LineString, and Polygon geometry types.

    Attributes:
        geometry_type: The geometry type (Point, LineString, Polygon).
        coordinates: The geometry coordinates in GeoJSON format.
    """

    geometry_type: str
    coordinates: Any

    def __post_init__(self) -> None:
        self.geometry_type = validate_geometry_type(self.geometry_type)
        self._validate_coordinates()

    def _validate_coordinates(self) -> None:
        """Validate coordinates based on geometry type."""
        if self.geometry_type == "Point":
            self.coordinates = validate_point_coordinates(self.coordinates)
        elif self.geometry_type == "LineString":
            self.coordinates = validate_linestring_coordinates(self.coordinates)
        elif self.geometry_type == "Polygon":
            self.coordinates = validate_polygon_coordinates(self.coordinates)

    def to_geojson(self) -> dict[str, Any]:
        """Serialize to GeoJSON geometry object.

        Returns:
            GeoJSON geometry dictionary.
        """
        return {
            "type": self.geometry_type,
            "coordinates": self.coordinates,
        }

    @classmethod
    def from_geojson(cls, data: dict[str, Any]) -> Geometry:
        """Deserialize from GeoJSON geometry object.

        Args:
            data: GeoJSON geometry dictionary.

        Returns:
            Geometry instance.

        Raises:
            InvalidGeometryError: If data is invalid.
        """
        if not isinstance(data, dict):
            raise InvalidGeometryError(
                f"GeoJSON geometry must be a dict, got {type(data).__name__}"
            )
        geometry_type = data.get("type")
        if geometry_type is None:
            raise InvalidGeometryError("GeoJSON geometry missing 'type' field")
        coordinates = data.get("coordinates")
        if coordinates is None:
            raise InvalidGeometryError("GeoJSON geometry missing 'coordinates' field")
        return cls(geometry_type=geometry_type, coordinates=coordinates)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "geometry_type": self.geometry_type,
            "coordinates": self.coordinates,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Geometry:
        """Deserialize from dictionary.

        Args:
            data: Dictionary representation.

        Returns:
            Geometry instance.
        """
        return cls(
            geometry_type=data["geometry_type"],
            coordinates=data["coordinates"],
        )


def geometry_bounds(geometry: Geometry) -> tuple[float, float, float, float]:
    """Calculate bounding box for a geometry.

    Args:
        geometry: The geometry to calculate bounds for.

    Returns:
        Tuple of (min_x, min_y, max_x, max_y).
    """
    coords = _flatten_coordinates(geometry.coordinates)
    if not coords:
        raise InvalidGeometryError("Cannot calculate bounds for empty geometry")

    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return (min(xs), min(ys), max(xs), max(ys))


def _flatten_coordinates(coordinates: Any) -> list[list[float]]:
    """Recursively flatten nested coordinate arrays to list of points.

    Args:
        coordinates: Nested coordinate structure.

    Returns:
        List of [x, y, ...] point coordinates.
    """
    if not coordinates:
        return []

    if isinstance(coordinates[0], (int, float)):
        return [coordinates]

    result = []
    for item in coordinates:
        result.extend(_flatten_coordinates(item))
    return result
