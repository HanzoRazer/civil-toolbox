"""Tests for spatial feature collection model."""

import pytest

from civil_toolbox.gis.errors import InvalidGeometryError, InvalidGeoJSONError
from civil_toolbox.gis.geometry import Geometry
from civil_toolbox.gis.features import SpatialFeature
from civil_toolbox.gis.collections import SpatialFeatureCollection, collection_bounds


def make_point_feature(id: str, x: float, y: float, **kwargs) -> SpatialFeature:
    """Create a test point feature."""
    return SpatialFeature(
        id=id,
        geometry=Geometry(geometry_type="Point", coordinates=[x, y]),
        **kwargs,
    )


def make_polygon_feature(id: str, **kwargs) -> SpatialFeature:
    """Create a test polygon feature."""
    return SpatialFeature(
        id=id,
        geometry=Geometry(
            geometry_type="Polygon",
            coordinates=[[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]],
        ),
        **kwargs,
    )


class TestSpatialFeatureCollectionCreation:
    """Tests for SpatialFeatureCollection creation."""

    def test_create_empty_collection(self):
        """Creates empty collection."""
        collection = SpatialFeatureCollection(
            id="coll_001",
            name="Test Collection",
        )
        assert collection.id == "coll_001"
        assert collection.name == "Test Collection"
        assert collection.features == []

    def test_create_collection_with_features(self):
        """Creates collection with features."""
        features = [
            make_point_feature("feat_001", 0.0, 0.0),
            make_point_feature("feat_002", 10.0, 10.0),
        ]
        collection = SpatialFeatureCollection(
            id="coll_001",
            name="Test Collection",
            features=features,
        )
        assert len(collection.features) == 2

    def test_default_id_generated(self):
        """Default ID is generated."""
        collection = SpatialFeatureCollection(name="Test")
        assert collection.id  # Should have generated an ID

    def test_coordinate_reference_preserved(self):
        """Coordinate reference is preserved."""
        collection = SpatialFeatureCollection(
            name="Test",
            coordinate_reference="EPSG:4326",
        )
        assert collection.coordinate_reference == "EPSG:4326"

    def test_metadata_preserved(self):
        """Metadata is preserved."""
        collection = SpatialFeatureCollection(
            name="Test",
            metadata={"source": "survey", "date": "2024-01-15"},
        )
        assert collection.metadata["source"] == "survey"

    def test_duplicate_feature_ids_fail(self):
        """Duplicate feature IDs raise error."""
        features = [
            make_point_feature("feat_001", 0.0, 0.0),
            make_point_feature("feat_001", 10.0, 10.0),
        ]
        with pytest.raises(InvalidGeometryError, match="Duplicate feature ID"):
            SpatialFeatureCollection(features=features)


class TestGetFeature:
    """Tests for get_feature method."""

    def test_get_existing_feature(self):
        """Gets existing feature by ID."""
        feat = make_point_feature("feat_001", 0.0, 0.0)
        collection = SpatialFeatureCollection(features=[feat])

        result = collection.get_feature("feat_001")
        assert result is feat

    def test_get_nonexistent_feature(self):
        """Returns None for nonexistent feature."""
        collection = SpatialFeatureCollection(
            features=[make_point_feature("feat_001", 0.0, 0.0)]
        )

        result = collection.get_feature("nonexistent")
        assert result is None


class TestFindByEntity:
    """Tests for find_by_entity method."""

    def test_find_by_entity_id(self):
        """Finds features by entity ID."""
        features = [
            make_point_feature("feat_001", 0.0, 0.0, entity_id="pipe_001"),
            make_point_feature("feat_002", 10.0, 10.0, entity_id="pipe_002"),
            make_point_feature("feat_003", 20.0, 20.0, entity_id="pipe_001"),
        ]
        collection = SpatialFeatureCollection(features=features)

        results = collection.find_by_entity("pipe_001")
        assert len(results) == 2
        assert all(f.entity_id == "pipe_001" for f in results)

    def test_find_by_entity_no_matches(self):
        """Returns empty list when no matches."""
        collection = SpatialFeatureCollection(
            features=[make_point_feature("feat_001", 0.0, 0.0, entity_id="pipe_001")]
        )

        results = collection.find_by_entity("nonexistent")
        assert results == []


class TestFindByRole:
    """Tests for find_by_role method."""

    def test_find_by_role(self):
        """Finds features by role."""
        features = [
            make_point_feature("n1", 0.0, 0.0, feature_role="infrastructure_node"),
            make_point_feature("n2", 10.0, 10.0, feature_role="infrastructure_node"),
            make_polygon_feature("da1", feature_role="drainage_area"),
        ]
        collection = SpatialFeatureCollection(features=features)

        nodes = collection.find_by_role("infrastructure_node")
        assert len(nodes) == 2

        areas = collection.find_by_role("drainage_area")
        assert len(areas) == 1

    def test_find_by_role_no_matches(self):
        """Returns empty list when no matches."""
        collection = SpatialFeatureCollection(
            features=[make_point_feature("feat_001", 0.0, 0.0, feature_role="other")]
        )

        results = collection.find_by_role("infrastructure_node")
        assert results == []


class TestCollectionGeoJSON:
    """Tests for GeoJSON serialization."""

    def test_to_geojson(self):
        """Serializes to GeoJSON FeatureCollection."""
        collection = SpatialFeatureCollection(
            id="coll_001",
            name="Test Collection",
            features=[make_point_feature("feat_001", 100.0, 50.0)],
            coordinate_reference="EPSG:4326",
            metadata={"source": "test"},
        )
        result = collection.to_geojson()

        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1
        assert result["properties"]["collection_id"] == "coll_001"
        assert result["properties"]["collection_name"] == "Test Collection"
        assert result["properties"]["coordinate_reference"] == "EPSG:4326"
        assert result["properties"]["metadata"]["source"] == "test"

    def test_to_geojson_empty_collection(self):
        """Empty collection serializes correctly."""
        collection = SpatialFeatureCollection(id="empty", name="Empty")
        result = collection.to_geojson()

        assert result["type"] == "FeatureCollection"
        assert result["features"] == []

    def test_from_geojson(self):
        """Deserializes from GeoJSON FeatureCollection."""
        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "feat_001",
                    "geometry": {"type": "Point", "coordinates": [100.0, 50.0]},
                    "properties": {"feature_role": "infrastructure_node"},
                }
            ],
            "properties": {
                "collection_id": "coll_001",
                "collection_name": "Test Collection",
                "coordinate_reference": "EPSG:4326",
            },
        }
        collection = SpatialFeatureCollection.from_geojson(data)

        assert collection.id == "coll_001"
        assert collection.name == "Test Collection"
        assert len(collection.features) == 1
        assert collection.coordinate_reference == "EPSG:4326"

    def test_from_geojson_minimal(self):
        """Deserializes minimal GeoJSON."""
        data = {
            "type": "FeatureCollection",
            "features": [],
        }
        collection = SpatialFeatureCollection.from_geojson(data)

        assert collection.features == []
        assert collection.id  # Should have generated an ID

    def test_from_geojson_invalid_type_fails(self):
        """Invalid type raises error."""
        data = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": {},
        }
        with pytest.raises(InvalidGeoJSONError, match="must be 'FeatureCollection'"):
            SpatialFeatureCollection.from_geojson(data)

    def test_from_geojson_missing_features_fails(self):
        """Missing features field raises error."""
        data = {"type": "FeatureCollection"}
        with pytest.raises(InvalidGeoJSONError, match="missing 'features'"):
            SpatialFeatureCollection.from_geojson(data)

    def test_from_geojson_non_dict_fails(self):
        """Non-dict input raises error."""
        with pytest.raises(InvalidGeoJSONError, match="must be a dict"):
            SpatialFeatureCollection.from_geojson("invalid")

    def test_from_geojson_invalid_feature_fails(self):
        """Invalid feature in list raises error."""
        data = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature"}],  # Missing geometry
        }
        with pytest.raises(InvalidGeoJSONError, match="Feature 0"):
            SpatialFeatureCollection.from_geojson(data)

    def test_geojson_round_trip(self):
        """Collection round-trips through GeoJSON."""
        original = SpatialFeatureCollection(
            id="coll_001",
            name="Test Collection",
            features=[
                make_point_feature("n1", 0.0, 0.0, feature_role="infrastructure_node"),
                make_polygon_feature("da1", feature_role="drainage_area"),
            ],
            coordinate_reference="EPSG:4326",
            metadata={"version": 1},
        )
        restored = SpatialFeatureCollection.from_geojson(original.to_geojson())

        assert restored.id == original.id
        assert restored.name == original.name
        assert len(restored.features) == len(original.features)
        assert restored.coordinate_reference == original.coordinate_reference


class TestCollectionDict:
    """Tests for dict serialization."""

    def test_to_dict(self):
        """Serializes to dict."""
        collection = SpatialFeatureCollection(
            id="coll_001",
            name="Test",
            features=[make_point_feature("feat_001", 0.0, 0.0)],
            coordinate_reference="local",
            metadata={"key": "value"},
        )
        result = collection.to_dict()

        assert result["id"] == "coll_001"
        assert result["name"] == "Test"
        assert len(result["features"]) == 1
        assert result["coordinate_reference"] == "local"
        assert result["metadata"]["key"] == "value"

    def test_from_dict(self):
        """Deserializes from dict."""
        data = {
            "id": "coll_001",
            "name": "Test",
            "features": [
                {
                    "id": "feat_001",
                    "geometry": {"geometry_type": "Point", "coordinates": [0.0, 0.0]},
                    "feature_role": "other",
                }
            ],
        }
        collection = SpatialFeatureCollection.from_dict(data)

        assert collection.id == "coll_001"
        assert len(collection.features) == 1

    def test_dict_round_trip(self):
        """Collection round-trips through dict."""
        original = SpatialFeatureCollection(
            id="coll_001",
            name="Test",
            features=[make_point_feature("feat_001", 100.0, 50.0)],
            coordinate_reference="EPSG:4326",
            metadata={"version": 2},
        )
        restored = SpatialFeatureCollection.from_dict(original.to_dict())

        assert restored.id == original.id
        assert restored.name == original.name
        assert len(restored.features) == len(original.features)


class TestCollectionBounds:
    """Tests for collection_bounds function."""

    def test_single_point_bounds(self):
        """Single point collection bounds."""
        collection = SpatialFeatureCollection(
            features=[make_point_feature("p1", 100.0, 50.0)]
        )
        bounds = collection_bounds(collection)
        assert bounds == (100.0, 50.0, 100.0, 50.0)

    def test_multiple_points_bounds(self):
        """Multiple points collection bounds."""
        collection = SpatialFeatureCollection(
            features=[
                make_point_feature("p1", 0.0, 0.0),
                make_point_feature("p2", 100.0, 50.0),
                make_point_feature("p3", 50.0, 75.0),
            ]
        )
        bounds = collection_bounds(collection)
        assert bounds == (0.0, 0.0, 100.0, 75.0)

    def test_polygon_bounds(self):
        """Polygon collection bounds."""
        collection = SpatialFeatureCollection(features=[make_polygon_feature("poly1")])
        bounds = collection_bounds(collection)
        assert bounds == (0.0, 0.0, 10.0, 10.0)

    def test_mixed_geometry_bounds(self):
        """Mixed geometry collection bounds."""
        collection = SpatialFeatureCollection(
            features=[
                make_point_feature("p1", 50.0, 50.0),
                make_polygon_feature("poly1"),
            ]
        )
        bounds = collection_bounds(collection)
        assert bounds == (0.0, 0.0, 50.0, 50.0)

    def test_empty_collection_bounds(self):
        """Empty collection returns None."""
        collection = SpatialFeatureCollection()
        bounds = collection_bounds(collection)
        assert bounds is None
