"""Tests for spatial feature model."""

import pytest

from civil_toolbox.gis.errors import InvalidGeometryError
from civil_toolbox.gis.geometry import Geometry
from civil_toolbox.gis.features import SpatialFeature


def make_point_geometry() -> Geometry:
    """Create a test point geometry."""
    return Geometry(geometry_type="Point", coordinates=[100.0, 50.0])


def make_polygon_geometry() -> Geometry:
    """Create a test polygon geometry."""
    return Geometry(
        geometry_type="Polygon",
        coordinates=[[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]],
    )


def make_line_geometry() -> Geometry:
    """Create a test line geometry."""
    return Geometry(
        geometry_type="LineString",
        coordinates=[[0.0, 0.0], [50.0, 50.0]],
    )


class TestSpatialFeatureCreation:
    """Tests for SpatialFeature creation."""

    def test_create_drainage_area_feature(self):
        """Creates drainage area feature."""
        feature = SpatialFeature(
            id="da_001",
            geometry=make_polygon_geometry(),
            feature_role="drainage_area",
            entity_id="drainage_area_001",
            entity_type="DrainageArea",
        )
        assert feature.id == "da_001"
        assert feature.feature_role == "drainage_area"
        assert feature.entity_id == "drainage_area_001"
        assert feature.entity_type == "DrainageArea"

    def test_create_infrastructure_node_feature(self):
        """Creates infrastructure node feature."""
        feature = SpatialFeature(
            id="node_001",
            geometry=make_point_geometry(),
            feature_role="infrastructure_node",
            entity_id="mh_001",
            entity_type="InfrastructureNode",
        )
        assert feature.feature_role == "infrastructure_node"
        assert feature.geometry.geometry_type == "Point"

    def test_create_infrastructure_link_feature(self):
        """Creates infrastructure link feature."""
        feature = SpatialFeature(
            id="link_001",
            geometry=make_line_geometry(),
            feature_role="infrastructure_link",
            entity_id="pipe_001",
            entity_type="Pipe",
        )
        assert feature.feature_role == "infrastructure_link"
        assert feature.geometry.geometry_type == "LineString"

    def test_create_flow_path_feature(self):
        """Creates flow path feature."""
        feature = SpatialFeature(
            id="fp_001",
            geometry=make_line_geometry(),
            feature_role="flow_path",
        )
        assert feature.feature_role == "flow_path"

    def test_default_feature_role_is_other(self):
        """Default feature role is 'other'."""
        feature = SpatialFeature(
            id="feat_001",
            geometry=make_point_geometry(),
        )
        assert feature.feature_role == "other"

    def test_custom_properties(self):
        """Custom properties are preserved."""
        feature = SpatialFeature(
            id="feat_001",
            geometry=make_point_geometry(),
            properties={"name": "Test Feature", "area_acres": 5.5},
        )
        assert feature.properties["name"] == "Test Feature"
        assert feature.properties["area_acres"] == 5.5

    def test_metadata_preserved(self):
        """Metadata is preserved."""
        feature = SpatialFeature(
            id="feat_001",
            geometry=make_point_geometry(),
            metadata={"source": "survey", "accuracy_ft": 0.5},
        )
        assert feature.metadata["source"] == "survey"

    def test_empty_id_fails(self):
        """Empty ID raises error."""
        with pytest.raises(InvalidGeometryError, match="cannot be empty"):
            SpatialFeature(id="", geometry=make_point_geometry())

    def test_whitespace_id_fails(self):
        """Whitespace-only ID raises error."""
        with pytest.raises(InvalidGeometryError, match="cannot be empty"):
            SpatialFeature(id="   ", geometry=make_point_geometry())

    def test_invalid_role_fails(self):
        """Invalid feature role raises error."""
        with pytest.raises(InvalidGeometryError, match="must be one of"):
            SpatialFeature(
                id="feat_001",
                geometry=make_point_geometry(),
                feature_role="invalid_role",
            )


class TestSpatialFeatureGeoJSON:
    """Tests for GeoJSON serialization."""

    def test_to_geojson_feature(self):
        """Serializes to GeoJSON Feature."""
        feature = SpatialFeature(
            id="node_001",
            geometry=make_point_geometry(),
            feature_role="infrastructure_node",
            entity_id="mh_001",
            entity_type="InfrastructureNode",
            properties={"name": "Manhole 1"},
        )
        result = feature.to_geojson_feature()

        assert result["type"] == "Feature"
        assert result["id"] == "node_001"
        assert result["geometry"]["type"] == "Point"
        assert result["properties"]["feature_id"] == "node_001"
        assert result["properties"]["feature_role"] == "infrastructure_node"
        assert result["properties"]["entity_id"] == "mh_001"
        assert result["properties"]["entity_type"] == "InfrastructureNode"
        assert result["properties"]["name"] == "Manhole 1"

    def test_to_geojson_without_entity_link(self):
        """Serializes without entity link fields if not set."""
        feature = SpatialFeature(
            id="ref_001",
            geometry=make_point_geometry(),
            feature_role="reference",
        )
        result = feature.to_geojson_feature()

        assert "entity_id" not in result["properties"]
        assert "entity_type" not in result["properties"]

    def test_from_geojson_feature(self):
        """Deserializes from GeoJSON Feature."""
        data = {
            "type": "Feature",
            "id": "node_001",
            "geometry": {"type": "Point", "coordinates": [100.0, 50.0]},
            "properties": {
                "feature_role": "infrastructure_node",
                "entity_id": "mh_001",
                "entity_type": "InfrastructureNode",
                "name": "Manhole 1",
            },
        }
        feature = SpatialFeature.from_geojson_feature(data)

        assert feature.id == "node_001"
        assert feature.feature_role == "infrastructure_node"
        assert feature.entity_id == "mh_001"
        assert feature.entity_type == "InfrastructureNode"
        assert feature.properties["name"] == "Manhole 1"
        assert "feature_role" not in feature.properties
        assert "entity_id" not in feature.properties

    def test_from_geojson_uses_feature_id_property(self):
        """Uses feature_id property if top-level id missing."""
        data = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [100.0, 50.0]},
            "properties": {"feature_id": "custom_id"},
        }
        feature = SpatialFeature.from_geojson_feature(data)
        assert feature.id == "custom_id"

    def test_from_geojson_generates_id_if_missing(self):
        """Generates ID if neither id nor feature_id present."""
        data = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [100.0, 50.0]},
            "properties": {},
        }
        feature = SpatialFeature.from_geojson_feature(data)
        assert feature.id  # Should have generated an ID

    def test_from_geojson_default_role(self):
        """Default feature role is 'other' if not specified."""
        data = {
            "type": "Feature",
            "id": "feat_001",
            "geometry": {"type": "Point", "coordinates": [100.0, 50.0]},
            "properties": {},
        }
        feature = SpatialFeature.from_geojson_feature(data)
        assert feature.feature_role == "other"

    def test_from_geojson_invalid_type_fails(self):
        """Invalid Feature type raises error."""
        data = {
            "type": "FeatureCollection",
            "features": [],
        }
        with pytest.raises(InvalidGeometryError, match="type must be 'Feature'"):
            SpatialFeature.from_geojson_feature(data)

    def test_from_geojson_missing_geometry_fails(self):
        """Missing geometry raises error."""
        data = {
            "type": "Feature",
            "id": "feat_001",
            "properties": {},
        }
        with pytest.raises(InvalidGeometryError, match="missing 'geometry'"):
            SpatialFeature.from_geojson_feature(data)

    def test_from_geojson_non_dict_fails(self):
        """Non-dict input raises error."""
        with pytest.raises(InvalidGeometryError, match="must be a dict"):
            SpatialFeature.from_geojson_feature("invalid")

    def test_geojson_round_trip(self):
        """Feature round-trips through GeoJSON."""
        original = SpatialFeature(
            id="da_001",
            geometry=make_polygon_geometry(),
            feature_role="drainage_area",
            entity_id="drainage_001",
            entity_type="DrainageArea",
            properties={"name": "Basin A", "area_acres": 10.5},
        )
        restored = SpatialFeature.from_geojson_feature(original.to_geojson_feature())

        assert restored.id == original.id
        assert restored.feature_role == original.feature_role
        assert restored.entity_id == original.entity_id
        assert restored.entity_type == original.entity_type
        assert restored.properties["name"] == original.properties["name"]


class TestSpatialFeatureDict:
    """Tests for dict serialization."""

    def test_to_dict(self):
        """Serializes to dict."""
        feature = SpatialFeature(
            id="feat_001",
            geometry=make_point_geometry(),
            feature_role="infrastructure_node",
            entity_id="node_001",
            entity_type="InfrastructureNode",
            properties={"name": "Node 1"},
            metadata={"source": "import"},
        )
        result = feature.to_dict()

        assert result["id"] == "feat_001"
        assert result["feature_role"] == "infrastructure_node"
        assert result["entity_id"] == "node_001"
        assert result["entity_type"] == "InfrastructureNode"
        assert result["properties"]["name"] == "Node 1"
        assert result["metadata"]["source"] == "import"
        assert "geometry" in result

    def test_from_dict(self):
        """Deserializes from dict."""
        data = {
            "id": "feat_001",
            "geometry": {"geometry_type": "Point", "coordinates": [100.0, 50.0]},
            "feature_role": "infrastructure_node",
            "entity_id": "node_001",
            "entity_type": "InfrastructureNode",
            "properties": {"name": "Node 1"},
            "metadata": {"source": "import"},
        }
        feature = SpatialFeature.from_dict(data)

        assert feature.id == "feat_001"
        assert feature.feature_role == "infrastructure_node"
        assert feature.entity_id == "node_001"

    def test_dict_round_trip(self):
        """Feature round-trips through dict."""
        original = SpatialFeature(
            id="link_001",
            geometry=make_line_geometry(),
            feature_role="infrastructure_link",
            entity_id="pipe_001",
            entity_type="Pipe",
            properties={"diameter_in": 18},
            metadata={"imported_at": "2024-01-15"},
        )
        restored = SpatialFeature.from_dict(original.to_dict())

        assert restored.id == original.id
        assert restored.feature_role == original.feature_role
        assert restored.entity_id == original.entity_id
        assert restored.entity_type == original.entity_type
        assert restored.properties == original.properties
        assert restored.metadata == original.metadata


class TestEntityLinkagePreservation:
    """Tests for entity linkage preservation."""

    def test_entity_linkage_preserved_through_geojson(self):
        """Entity linkage survives GeoJSON round-trip."""
        original = SpatialFeature(
            id="feature_pipe_001",
            geometry=make_line_geometry(),
            feature_role="infrastructure_link",
            entity_id="pipe_001",
            entity_type="Pipe",
        )
        geojson = original.to_geojson_feature()
        restored = SpatialFeature.from_geojson_feature(geojson)

        assert restored.entity_id == "pipe_001"
        assert restored.entity_type == "Pipe"

    def test_entity_linkage_in_geojson_properties(self):
        """Entity linkage fields appear in GeoJSON properties."""
        feature = SpatialFeature(
            id="feat_001",
            geometry=make_point_geometry(),
            entity_id="inlet_001",
            entity_type="Inlet",
        )
        geojson = feature.to_geojson_feature()

        assert geojson["properties"]["entity_id"] == "inlet_001"
        assert geojson["properties"]["entity_type"] == "Inlet"
