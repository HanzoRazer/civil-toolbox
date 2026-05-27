"""Tests for synthetic GIS example data."""

import pytest

from civil_toolbox.gis.examples import create_example_spatial_feature_collection
from civil_toolbox.gis.collections import SpatialFeatureCollection


class TestCreateExampleSpatialFeatureCollection:
    """Tests for create_example_spatial_feature_collection."""

    def test_creates_collection(self):
        """Creates a valid collection."""
        collection = create_example_spatial_feature_collection()

        assert isinstance(collection, SpatialFeatureCollection)
        assert collection.id == "example_site_collection"
        assert collection.name == "Example Site Features"

    def test_contains_expected_feature_roles(self):
        """Contains all expected feature roles."""
        collection = create_example_spatial_feature_collection()

        roles = {f.feature_role for f in collection.features}

        assert "drainage_area" in roles
        assert "flow_path" in roles
        assert "infrastructure_node" in roles
        assert "infrastructure_link" in roles

    def test_contains_drainage_area(self):
        """Contains a drainage area polygon."""
        collection = create_example_spatial_feature_collection()

        areas = collection.find_by_role("drainage_area")
        assert len(areas) == 1
        assert areas[0].geometry.geometry_type == "Polygon"
        assert areas[0].entity_type == "DrainageArea"

    def test_contains_flow_path(self):
        """Contains a flow path line."""
        collection = create_example_spatial_feature_collection()

        paths = collection.find_by_role("flow_path")
        assert len(paths) == 1
        assert paths[0].geometry.geometry_type == "LineString"
        assert paths[0].entity_type == "FlowPath"

    def test_contains_infrastructure_node(self):
        """Contains an infrastructure node point."""
        collection = create_example_spatial_feature_collection()

        nodes = collection.find_by_role("infrastructure_node")
        assert len(nodes) == 1
        assert nodes[0].geometry.geometry_type == "Point"
        assert nodes[0].entity_type == "InfrastructureNode"

    def test_contains_infrastructure_link(self):
        """Contains an infrastructure link line."""
        collection = create_example_spatial_feature_collection()

        links = collection.find_by_role("infrastructure_link")
        assert len(links) == 1
        assert links[0].geometry.geometry_type == "LineString"
        assert links[0].entity_type == "Pipe"

    def test_metadata_marks_synthetic(self):
        """Metadata marks collection as synthetic."""
        collection = create_example_spatial_feature_collection()

        assert collection.metadata["synthetic"] is True
        assert collection.metadata["for_testing_only"] is True

    def test_has_coordinate_reference(self):
        """Has coordinate reference set."""
        collection = create_example_spatial_feature_collection()

        assert collection.coordinate_reference == "local_project_coordinates"

    def test_exports_to_geojson(self):
        """Exports to valid GeoJSON."""
        collection = create_example_spatial_feature_collection()

        geojson = collection.to_geojson()

        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == 4

    def test_round_trips_through_geojson(self):
        """Round-trips through GeoJSON serialization."""
        original = create_example_spatial_feature_collection()

        geojson = original.to_geojson()
        restored = SpatialFeatureCollection.from_geojson(geojson)

        assert restored.id == original.id
        assert restored.name == original.name
        assert len(restored.features) == len(original.features)

        original_roles = {f.feature_role for f in original.features}
        restored_roles = {f.feature_role for f in restored.features}
        assert original_roles == restored_roles

    def test_features_have_entity_links(self):
        """All features have entity linkage."""
        collection = create_example_spatial_feature_collection()

        for feature in collection.features:
            assert feature.entity_id is not None
            assert feature.entity_type is not None

    def test_features_have_properties(self):
        """All features have meaningful properties."""
        collection = create_example_spatial_feature_collection()

        for feature in collection.features:
            assert "name" in feature.properties
            assert len(feature.properties) > 1


class TestExampleDataIntegration:
    """Integration tests for example data."""

    def test_save_and_load_example(self, tmp_path):
        """Example collection saves and loads correctly."""
        from civil_toolbox.gis.geojson import save_geojson, load_geojson

        collection = create_example_spatial_feature_collection()
        file_path = tmp_path / "example.geojson"

        save_geojson(collection, file_path)
        loaded = load_geojson(file_path)

        assert loaded.id == collection.id
        assert len(loaded.features) == 4

    def test_example_bounds_calculation(self):
        """Bounds calculation works on example data."""
        from civil_toolbox.gis.collections import collection_bounds

        collection = create_example_spatial_feature_collection()

        bounds = collection_bounds(collection)

        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        assert min_x < max_x
        assert min_y < max_y
