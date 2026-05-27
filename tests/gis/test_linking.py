"""Tests for GIS entity linking utilities."""

import pytest

from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment
from civil_toolbox.infrastructure.nodes import InfrastructureNode
from civil_toolbox.infrastructure.pipes import Pipe

from civil_toolbox.gis.linking import (
    feature_for_drainage_area,
    feature_for_infrastructure_node,
    feature_for_pipe,
    feature_for_flow_path,
)


class TestFeatureForDrainageArea:
    """Tests for feature_for_drainage_area."""

    def test_creates_polygon_feature(self):
        """Creates polygon feature for drainage area."""
        area = DrainageArea(
            id="da_001",
            name="Basin A",
            area_acres=10.5,
        )
        coords = [[[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0], [0.0, 0.0]]]

        feature = feature_for_drainage_area(area, coords)

        assert feature.id == "feature_da_001"
        assert feature.geometry.geometry_type == "Polygon"
        assert feature.entity_id == "da_001"
        assert feature.entity_type == "DrainageArea"
        assert feature.feature_role == "drainage_area"

    def test_includes_name_and_area(self):
        """Includes name and area in properties."""
        area = DrainageArea(
            id="da_001",
            name="Basin A",
            area_acres=10.5,
        )
        coords = [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]

        feature = feature_for_drainage_area(area, coords)

        assert feature.properties["name"] == "Basin A"
        assert feature.properties["area_acres"] == 10.5

    def test_custom_properties_preserved(self):
        """Custom properties are preserved."""
        area = DrainageArea(id="da_001", name="Basin A")
        coords = [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]

        feature = feature_for_drainage_area(
            area, coords, properties={"soil_group": "B", "land_use": "residential"}
        )

        assert feature.properties["soil_group"] == "B"
        assert feature.properties["land_use"] == "residential"

    def test_does_not_mutate_source_entity(self):
        """Does not mutate source drainage area."""
        area = DrainageArea(id="da_001", name="Basin A", area_acres=10.0)
        original_dict = area.to_dict()
        coords = [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]

        feature_for_drainage_area(area, coords)

        assert area.to_dict() == original_dict


class TestFeatureForInfrastructureNode:
    """Tests for feature_for_infrastructure_node."""

    def test_creates_point_feature(self):
        """Creates point feature for infrastructure node."""
        node = InfrastructureNode(
            id="mh_001",
            name="MH-1",
            node_type="manhole",
            invert_elevation_ft=95.5,
            rim_elevation_ft=100.0,
        )
        coords = [100.0, 50.0]

        feature = feature_for_infrastructure_node(node, coords)

        assert feature.id == "feature_mh_001"
        assert feature.geometry.geometry_type == "Point"
        assert feature.entity_id == "mh_001"
        assert feature.entity_type == "InfrastructureNode"
        assert feature.feature_role == "infrastructure_node"

    def test_includes_node_properties(self):
        """Includes node properties."""
        node = InfrastructureNode(
            id="mh_001",
            name="MH-1",
            node_type="manhole",
            invert_elevation_ft=95.5,
            rim_elevation_ft=100.0,
        )
        coords = [100.0, 50.0]

        feature = feature_for_infrastructure_node(node, coords)

        assert feature.properties["name"] == "MH-1"
        assert feature.properties["node_type"] == "manhole"
        assert feature.properties["invert_elevation_ft"] == 95.5
        assert feature.properties["rim_elevation_ft"] == 100.0

    def test_custom_properties_preserved(self):
        """Custom properties are preserved."""
        node = InfrastructureNode(id="in_001", name="IN-1", node_type="inlet")
        coords = [50.0, 50.0]

        feature = feature_for_infrastructure_node(
            node, coords, properties={"grate_type": "Type A"}
        )

        assert feature.properties["grate_type"] == "Type A"

    def test_does_not_mutate_source_entity(self):
        """Does not mutate source node."""
        node = InfrastructureNode(id="mh_001", name="MH-1", node_type="manhole")
        original_dict = node.to_dict()
        coords = [100.0, 50.0]

        feature_for_infrastructure_node(node, coords)

        assert node.to_dict() == original_dict


class TestFeatureForPipe:
    """Tests for feature_for_pipe."""

    def test_creates_line_feature(self):
        """Creates line feature for pipe."""
        pipe = Pipe(
            id="pipe_001",
            name="P-1",
            shape="circular",
            diameter_in=18.0,
            length_ft=100.0,
            slope_ft_per_ft=0.01,
            material="RCP",
        )
        coords = [[0.0, 0.0], [100.0, 0.0]]

        feature = feature_for_pipe(pipe, coords)

        assert feature.id == "feature_pipe_001"
        assert feature.geometry.geometry_type == "LineString"
        assert feature.entity_id == "pipe_001"
        assert feature.entity_type == "Pipe"
        assert feature.feature_role == "infrastructure_link"

    def test_includes_pipe_properties(self):
        """Includes pipe properties."""
        pipe = Pipe(
            id="pipe_001",
            name="P-1",
            shape="circular",
            diameter_in=18.0,
            length_ft=100.0,
            slope_ft_per_ft=0.01,
            material="RCP",
        )
        coords = [[0.0, 0.0], [100.0, 0.0]]

        feature = feature_for_pipe(pipe, coords)

        assert feature.properties["name"] == "P-1"
        assert feature.properties["shape"] == "circular"
        assert feature.properties["diameter_in"] == 18.0
        assert feature.properties["length_ft"] == 100.0
        assert feature.properties["material"] == "RCP"

    def test_custom_properties_preserved(self):
        """Custom properties are preserved."""
        pipe = Pipe(
            id="pipe_001",
            name="P-1",
            shape="circular",
            diameter_in=18.0,
            length_ft=100.0,
        )
        coords = [[0.0, 0.0], [100.0, 0.0]]

        feature = feature_for_pipe(pipe, coords, properties={"install_year": 2020})

        assert feature.properties["install_year"] == 2020

    def test_does_not_mutate_source_entity(self):
        """Does not mutate source pipe."""
        pipe = Pipe(
            id="pipe_001",
            name="P-1",
            shape="circular",
            diameter_in=18.0,
            length_ft=100.0,
        )
        original_dict = pipe.to_dict()
        coords = [[0.0, 0.0], [100.0, 0.0]]

        feature_for_pipe(pipe, coords)

        assert pipe.to_dict() == original_dict


class TestFeatureForFlowPath:
    """Tests for feature_for_flow_path."""

    def test_creates_line_feature(self):
        """Creates line feature for flow path."""
        flow_path = FlowPath(
            id="fp_001",
            name="FP-1",
            segments=[
                FlowPathSegment(segment_type="sheet", length_ft=100.0, slope_ft_per_ft=0.02),
                FlowPathSegment(segment_type="channel", length_ft=200.0, slope_ft_per_ft=0.01),
            ],
        )
        coords = [[0.0, 0.0], [50.0, 50.0], [100.0, 100.0]]

        feature = feature_for_flow_path(flow_path, coords)

        assert feature.id == "feature_fp_001"
        assert feature.geometry.geometry_type == "LineString"
        assert feature.entity_id == "fp_001"
        assert feature.entity_type == "FlowPath"
        assert feature.feature_role == "flow_path"

    def test_includes_flow_path_properties(self):
        """Includes flow path properties."""
        flow_path = FlowPath(
            id="fp_001",
            name="FP-1",
            segments=[
                FlowPathSegment(segment_type="sheet", length_ft=100.0, slope_ft_per_ft=0.02),
                FlowPathSegment(segment_type="channel", length_ft=200.0, slope_ft_per_ft=0.01),
            ],
        )
        coords = [[0.0, 0.0], [100.0, 100.0]]

        feature = feature_for_flow_path(flow_path, coords)

        assert feature.properties["name"] == "FP-1"
        assert feature.properties["total_length_ft"] == 300.0
        assert feature.properties["segment_count"] == 2

    def test_custom_properties_preserved(self):
        """Custom properties are preserved."""
        flow_path = FlowPath(id="fp_001", name="FP-1")
        coords = [[0.0, 0.0], [100.0, 100.0]]

        feature = feature_for_flow_path(flow_path, coords, properties={"tc_min": 15.5})

        assert feature.properties["tc_min"] == 15.5

    def test_does_not_mutate_source_entity(self):
        """Does not mutate source flow path."""
        flow_path = FlowPath(id="fp_001", name="FP-1")
        original_dict = flow_path.to_dict()
        coords = [[0.0, 0.0], [100.0, 100.0]]

        feature_for_flow_path(flow_path, coords)

        assert flow_path.to_dict() == original_dict


class TestEntityLinkageIntegration:
    """Integration tests for entity linking."""

    def test_linked_features_round_trip_through_geojson(self):
        """Linked features survive GeoJSON round-trip."""
        from civil_toolbox.gis.collections import SpatialFeatureCollection

        node = InfrastructureNode(id="mh_001", name="MH-1", node_type="manhole")
        pipe = Pipe(
            id="pipe_001", name="P-1", shape="circular", diameter_in=18.0, length_ft=50.0
        )

        features = [
            feature_for_infrastructure_node(node, [0.0, 0.0]),
            feature_for_pipe(pipe, [[0.0, 0.0], [50.0, 0.0]]),
        ]

        collection = SpatialFeatureCollection(
            id="network",
            name="Network",
            features=features,
        )

        geojson = collection.to_geojson()
        restored = SpatialFeatureCollection.from_geojson(geojson)

        node_feature = restored.find_by_entity("mh_001")
        assert len(node_feature) == 1
        assert node_feature[0].entity_type == "InfrastructureNode"

        pipe_feature = restored.find_by_entity("pipe_001")
        assert len(pipe_feature) == 1
        assert pipe_feature[0].entity_type == "Pipe"
