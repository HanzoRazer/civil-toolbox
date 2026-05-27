"""Synthetic GIS example data."""

from __future__ import annotations

from civil_toolbox.gis.geometry import Geometry
from civil_toolbox.gis.features import SpatialFeature
from civil_toolbox.gis.collections import SpatialFeatureCollection


def create_example_spatial_feature_collection() -> SpatialFeatureCollection:
    """Create a synthetic example spatial feature collection.

    This collection contains demo features representing a simple drainage
    site with one drainage area, one flow path, one infrastructure node,
    and one pipe.

    Metadata marks this data as synthetic and for testing only.

    Returns:
        SpatialFeatureCollection with example features.
    """
    drainage_area = SpatialFeature(
        id="feature_drainage_001",
        geometry=Geometry(
            geometry_type="Polygon",
            coordinates=[[
                [0.0, 0.0],
                [200.0, 0.0],
                [200.0, 150.0],
                [0.0, 150.0],
                [0.0, 0.0],
            ]],
        ),
        properties={
            "name": "Example Basin A",
            "area_acres": 6.89,
            "runoff_coefficient": 0.65,
        },
        entity_id="drainage_001",
        entity_type="DrainageArea",
        feature_role="drainage_area",
    )

    flow_path = SpatialFeature(
        id="feature_flowpath_001",
        geometry=Geometry(
            geometry_type="LineString",
            coordinates=[
                [180.0, 140.0],
                [150.0, 100.0],
                [100.0, 75.0],
                [50.0, 50.0],
                [10.0, 10.0],
            ],
        ),
        properties={
            "name": "Example Flow Path",
            "total_length_ft": 250.0,
            "segment_count": 3,
        },
        entity_id="flowpath_001",
        entity_type="FlowPath",
        feature_role="flow_path",
    )

    inlet_node = SpatialFeature(
        id="feature_inlet_001",
        geometry=Geometry(
            geometry_type="Point",
            coordinates=[10.0, 10.0],
        ),
        properties={
            "name": "Inlet 1",
            "node_type": "inlet",
            "rim_elevation_ft": 102.5,
            "invert_elevation_ft": 98.0,
        },
        entity_id="inlet_001",
        entity_type="InfrastructureNode",
        feature_role="infrastructure_node",
    )

    pipe = SpatialFeature(
        id="feature_pipe_001",
        geometry=Geometry(
            geometry_type="LineString",
            coordinates=[
                [10.0, 10.0],
                [-50.0, -20.0],
            ],
        ),
        properties={
            "name": "Storm Pipe 1",
            "shape": "circular",
            "diameter_in": 18.0,
            "length_ft": 67.1,
            "material": "RCP",
        },
        entity_id="pipe_001",
        entity_type="Pipe",
        feature_role="infrastructure_link",
    )

    return SpatialFeatureCollection(
        id="example_site_collection",
        name="Example Site Features",
        features=[drainage_area, flow_path, inlet_node, pipe],
        coordinate_reference="local_project_coordinates",
        metadata={
            "synthetic": True,
            "for_testing_only": True,
            "description": "Demo spatial features for Civil Toolbox GIS workflows",
            "version": 1,
        },
    )
