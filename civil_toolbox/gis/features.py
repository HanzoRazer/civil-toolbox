"""Spatial feature model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from civil_toolbox.gis.errors import InvalidGeometryError
from civil_toolbox.gis.geometry import Geometry
from civil_toolbox.gis.validation import (
    validate_non_empty_string,
    validate_feature_role,
)


def _generate_id() -> str:
    """Generate a unique feature ID."""
    return str(uuid4())


@dataclass
class SpatialFeature:
    """A spatial feature with geometry and properties.

    Links a geometry to domain or infrastructure entities via entity_id
    and entity_type fields.

    Attributes:
        id: Unique feature identifier.
        geometry: The feature geometry.
        properties: Custom properties dictionary.
        entity_id: Optional linked entity ID.
        entity_type: Optional linked entity type name.
        feature_role: The feature role (drainage_area, infrastructure_node, etc.).
        metadata: Additional metadata dictionary.
    """

    id: str
    geometry: Geometry
    properties: dict[str, Any] = field(default_factory=dict)
    entity_id: str | None = None
    entity_type: str | None = None
    feature_role: str = "other"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.id = validate_non_empty_string(self.id, "id")
        self.feature_role = validate_feature_role(self.feature_role)

    def to_geojson_feature(self) -> dict[str, Any]:
        """Serialize to GeoJSON Feature object.

        Entity linkage fields are included in properties for GeoJSON compatibility.

        Returns:
            GeoJSON Feature dictionary.
        """
        props = dict(self.properties)
        props["feature_id"] = self.id
        props["feature_role"] = self.feature_role
        if self.entity_id is not None:
            props["entity_id"] = self.entity_id
        if self.entity_type is not None:
            props["entity_type"] = self.entity_type

        return {
            "type": "Feature",
            "id": self.id,
            "geometry": self.geometry.to_geojson(),
            "properties": props,
        }

    @classmethod
    def from_geojson_feature(cls, data: dict[str, Any]) -> SpatialFeature:
        """Deserialize from GeoJSON Feature object.

        Args:
            data: GeoJSON Feature dictionary.

        Returns:
            SpatialFeature instance.

        Raises:
            InvalidGeometryError: If data is invalid.
        """
        if not isinstance(data, dict):
            raise InvalidGeometryError(
                f"GeoJSON Feature must be a dict, got {type(data).__name__}"
            )
        if data.get("type") != "Feature":
            raise InvalidGeometryError(
                f"GeoJSON Feature type must be 'Feature', got '{data.get('type')}'"
            )

        geometry_data = data.get("geometry")
        if geometry_data is None:
            raise InvalidGeometryError("GeoJSON Feature missing 'geometry' field")

        properties = dict(data.get("properties", {}))

        feature_id = data.get("id") or properties.pop("feature_id", None)
        if feature_id is None:
            feature_id = _generate_id()

        feature_role = properties.pop("feature_role", "other")
        entity_id = properties.pop("entity_id", None)
        entity_type = properties.pop("entity_type", None)

        return cls(
            id=str(feature_id),
            geometry=Geometry.from_geojson(geometry_data),
            properties=properties,
            entity_id=entity_id,
            entity_type=entity_type,
            feature_role=feature_role,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "geometry": self.geometry.to_dict(),
            "properties": dict(self.properties),
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "feature_role": self.feature_role,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpatialFeature:
        """Deserialize from dictionary.

        Args:
            data: Dictionary representation.

        Returns:
            SpatialFeature instance.
        """
        return cls(
            id=data["id"],
            geometry=Geometry.from_dict(data["geometry"]),
            properties=data.get("properties", {}),
            entity_id=data.get("entity_id"),
            entity_type=data.get("entity_type"),
            feature_role=data.get("feature_role", "other"),
            metadata=data.get("metadata", {}),
        )
