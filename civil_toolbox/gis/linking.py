"""Entity linking utilities for spatial features."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from civil_toolbox.gis.geometry import Geometry
from civil_toolbox.gis.features import SpatialFeature

if TYPE_CHECKING:
    from civil_toolbox.domain.drainage import DrainageArea
    from civil_toolbox.domain.flow_path import FlowPath
    from civil_toolbox.infrastructure.nodes import InfrastructureNode
    from civil_toolbox.infrastructure.pipes import Pipe


def feature_for_drainage_area(
    drainage_area: DrainageArea,
    polygon_coordinates: Any,
    properties: dict[str, Any] | None = None,
) -> SpatialFeature:
    """Create a spatial feature for a drainage area.

    Args:
        drainage_area: The drainage area entity.
        polygon_coordinates: Polygon coordinates in GeoJSON format.
        properties: Optional additional properties.

    Returns:
        SpatialFeature linked to the drainage area.
    """
    props = dict(properties) if properties else {}
    props.setdefault("name", drainage_area.name)
    if drainage_area.area_acres is not None:
        props.setdefault("area_acres", drainage_area.area_acres)

    return SpatialFeature(
        id=f"feature_{drainage_area.id}",
        geometry=Geometry(geometry_type="Polygon", coordinates=polygon_coordinates),
        properties=props,
        entity_id=drainage_area.id,
        entity_type="DrainageArea",
        feature_role="drainage_area",
    )


def feature_for_infrastructure_node(
    node: InfrastructureNode,
    point_coordinates: Any,
    properties: dict[str, Any] | None = None,
) -> SpatialFeature:
    """Create a spatial feature for an infrastructure node.

    Args:
        node: The infrastructure node entity.
        point_coordinates: Point coordinates in GeoJSON format [x, y] or [x, y, z].
        properties: Optional additional properties.

    Returns:
        SpatialFeature linked to the infrastructure node.
    """
    props = dict(properties) if properties else {}
    props.setdefault("name", node.name)
    props.setdefault("node_type", node.node_type)
    if node.invert_elevation_ft is not None:
        props.setdefault("invert_elevation_ft", node.invert_elevation_ft)
    if node.rim_elevation_ft is not None:
        props.setdefault("rim_elevation_ft", node.rim_elevation_ft)

    return SpatialFeature(
        id=f"feature_{node.id}",
        geometry=Geometry(geometry_type="Point", coordinates=point_coordinates),
        properties=props,
        entity_id=node.id,
        entity_type="InfrastructureNode",
        feature_role="infrastructure_node",
    )


def feature_for_pipe(
    pipe: Pipe,
    line_coordinates: Any,
    properties: dict[str, Any] | None = None,
) -> SpatialFeature:
    """Create a spatial feature for a pipe.

    Args:
        pipe: The pipe entity.
        line_coordinates: LineString coordinates in GeoJSON format.
        properties: Optional additional properties.

    Returns:
        SpatialFeature linked to the pipe.
    """
    props = dict(properties) if properties else {}
    props.setdefault("name", pipe.name)
    props.setdefault("shape", pipe.shape)
    if pipe.diameter_in is not None:
        props.setdefault("diameter_in", pipe.diameter_in)
    props.setdefault("length_ft", pipe.length_ft)
    if pipe.material:
        props.setdefault("material", pipe.material)

    return SpatialFeature(
        id=f"feature_{pipe.id}",
        geometry=Geometry(geometry_type="LineString", coordinates=line_coordinates),
        properties=props,
        entity_id=pipe.id,
        entity_type="Pipe",
        feature_role="infrastructure_link",
    )


def feature_for_flow_path(
    flow_path: FlowPath,
    line_coordinates: Any,
    properties: dict[str, Any] | None = None,
) -> SpatialFeature:
    """Create a spatial feature for a flow path.

    Args:
        flow_path: The flow path entity.
        line_coordinates: LineString coordinates in GeoJSON format.
        properties: Optional additional properties.

    Returns:
        SpatialFeature linked to the flow path.
    """
    props = dict(properties) if properties else {}
    props.setdefault("name", flow_path.name)
    props.setdefault("total_length_ft", flow_path.total_length_ft)
    props.setdefault("segment_count", len(flow_path.segments))

    return SpatialFeature(
        id=f"feature_{flow_path.id}",
        geometry=Geometry(geometry_type="LineString", coordinates=line_coordinates),
        properties=props,
        entity_id=flow_path.id,
        entity_type="FlowPath",
        feature_role="flow_path",
    )
