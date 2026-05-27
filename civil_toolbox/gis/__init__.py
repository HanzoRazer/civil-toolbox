"""GIS workflow module for Civil Toolbox.

Provides spatial feature models, GeoJSON import/export, and entity linking
utilities for map-based drainage analysis workflows.

Supported geometry types:
- Point — infrastructure nodes, inlets, outlets
- LineString — pipes, flow paths, channels
- Polygon — drainage areas, project boundaries

Feature roles:
- drainage_area — polygon representing a contributing watershed
- flow_path — line representing water travel path
- infrastructure_node — point representing a network junction
- infrastructure_link — line representing a pipe or channel
- project_boundary — polygon defining project extents
- reference — supporting reference geometry
- other — general purpose features

Example:
    >>> from civil_toolbox.gis import (
    ...     Geometry,
    ...     SpatialFeature,
    ...     SpatialFeatureCollection,
    ...     save_geojson,
    ...     load_geojson,
    ... )
    >>> geometry = Geometry(
    ...     geometry_type="Point",
    ...     coordinates=[100.0, 50.0],
    ... )
    >>> feature = SpatialFeature(
    ...     id="node_001",
    ...     geometry=geometry,
    ...     feature_role="infrastructure_node",
    ... )
    >>> collection = SpatialFeatureCollection(
    ...     id="site_features",
    ...     name="Site Features",
    ...     features=[feature],
    ... )
    >>> save_geojson(collection, "site.geojson")
"""

# Public API will be exposed after implementation
__all__: list[str] = []
