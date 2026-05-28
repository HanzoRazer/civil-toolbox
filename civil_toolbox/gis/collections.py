"""Spatial feature collection model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from civil_toolbox.gis.errors import InvalidGeometryError, InvalidGeoJSONError
from civil_toolbox.gis.features import SpatialFeature
from civil_toolbox.gis.geometry import geometry_bounds


def _generate_id() -> str:
    """Generate a unique collection ID."""
    return str(uuid4())


@dataclass
class SpatialFeatureCollection:
    """A collection of spatial features.

    Attributes:
        id: Unique collection identifier.
        name: Human-readable collection name.
        features: List of spatial features.
        coordinate_reference: Optional coordinate reference system identifier.
        metadata: Additional metadata dictionary.
    """

    id: str = field(default_factory=_generate_id)
    name: str = ""
    features: list[SpatialFeature] = field(default_factory=list)
    coordinate_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validate_unique_ids()

    def _validate_unique_ids(self) -> None:
        """Validate that all feature IDs are unique."""
        seen: set[str] = set()
        for feature in self.features:
            if feature.id in seen:
                raise InvalidGeometryError(
                    f"Duplicate feature ID: '{feature.id}'"
                )
            seen.add(feature.id)

    def get_feature(self, feature_id: str) -> SpatialFeature | None:
        """Get a feature by ID.

        Args:
            feature_id: The feature ID to find.

        Returns:
            The feature if found, None otherwise.
        """
        for feature in self.features:
            if feature.id == feature_id:
                return feature
        return None

    def find_by_entity(self, entity_id: str) -> list[SpatialFeature]:
        """Find all features linked to an entity.

        Args:
            entity_id: The entity ID to search for.

        Returns:
            List of features with matching entity_id.
        """
        return [f for f in self.features if f.entity_id == entity_id]

    def find_by_role(self, feature_role: str) -> list[SpatialFeature]:
        """Find all features with a specific role.

        Args:
            feature_role: The feature role to search for.

        Returns:
            List of features with matching role.
        """
        return [f for f in self.features if f.feature_role == feature_role]

    def to_geojson(self) -> dict[str, Any]:
        """Serialize to GeoJSON FeatureCollection.

        Returns:
            GeoJSON FeatureCollection dictionary.
        """
        result: dict[str, Any] = {
            "type": "FeatureCollection",
            "features": [f.to_geojson_feature() for f in self.features],
        }

        props: dict[str, Any] = {
            "collection_id": self.id,
            "collection_name": self.name,
        }
        if self.coordinate_reference:
            props["coordinate_reference"] = self.coordinate_reference
        if self.metadata:
            props["metadata"] = self.metadata

        result["properties"] = props
        return result

    @classmethod
    def from_geojson(cls, data: dict[str, Any]) -> SpatialFeatureCollection:
        """Deserialize from GeoJSON FeatureCollection.

        Args:
            data: GeoJSON FeatureCollection dictionary.

        Returns:
            SpatialFeatureCollection instance.

        Raises:
            InvalidGeoJSONError: If data is invalid.
        """
        if not isinstance(data, dict):
            raise InvalidGeoJSONError(
                f"GeoJSON must be a dict, got {type(data).__name__}"
            )
        if data.get("type") != "FeatureCollection":
            raise InvalidGeoJSONError(
                f"GeoJSON type must be 'FeatureCollection', got '{data.get('type')}'"
            )

        features_data = data.get("features")
        if features_data is None:
            raise InvalidGeoJSONError("GeoJSON missing 'features' field")
        if not isinstance(features_data, list):
            raise InvalidGeoJSONError(
                f"GeoJSON 'features' must be a list, got {type(features_data).__name__}"
            )

        features = []
        for i, feat_data in enumerate(features_data):
            try:
                features.append(SpatialFeature.from_geojson_feature(feat_data))
            except InvalidGeometryError as e:
                raise InvalidGeoJSONError(f"Feature {i}: {e}") from e

        props = data.get("properties", {})
        collection_id = props.get("collection_id") or _generate_id()
        collection_name = props.get("collection_name", "")
        coordinate_reference = props.get("coordinate_reference")
        metadata = props.get("metadata", {})

        return cls(
            id=collection_id,
            name=collection_name,
            features=features,
            coordinate_reference=coordinate_reference,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "name": self.name,
            "features": [f.to_dict() for f in self.features],
            "coordinate_reference": self.coordinate_reference,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpatialFeatureCollection:
        """Deserialize from dictionary.

        Args:
            data: Dictionary representation.

        Returns:
            SpatialFeatureCollection instance.
        """
        return cls(
            id=data.get("id", _generate_id()),
            name=data.get("name", ""),
            features=[SpatialFeature.from_dict(f) for f in data.get("features", [])],
            coordinate_reference=data.get("coordinate_reference"),
            metadata=data.get("metadata", {}),
        )


def collection_bounds(
    collection: SpatialFeatureCollection,
) -> tuple[float, float, float, float] | None:
    """Calculate bounding box for a feature collection.

    Args:
        collection: The collection to calculate bounds for.

    Returns:
        Tuple of (min_x, min_y, max_x, max_y), or None if collection is empty.
    """
    if not collection.features:
        return None

    all_bounds = [geometry_bounds(f.geometry) for f in collection.features]
    min_x = min(b[0] for b in all_bounds)
    min_y = min(b[1] for b in all_bounds)
    max_x = max(b[2] for b in all_bounds)
    max_y = max(b[3] for b in all_bounds)

    return (min_x, min_y, max_x, max_y)
