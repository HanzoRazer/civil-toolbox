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

from civil_toolbox.gis.geometry import (
    Geometry,
    geometry_bounds,
)

from civil_toolbox.gis.features import (
    SpatialFeature,
)

from civil_toolbox.gis.collections import (
    SpatialFeatureCollection,
    collection_bounds,
)

from civil_toolbox.gis.geojson import (
    export_feature_collection_to_geojson,
    import_feature_collection_from_geojson,
    save_geojson,
    load_geojson,
)

from civil_toolbox.gis.linking import (
    feature_for_drainage_area,
    feature_for_infrastructure_node,
    feature_for_pipe,
    feature_for_flow_path,
)

from civil_toolbox.gis.examples import (
    create_example_spatial_feature_collection,
)

from civil_toolbox.gis.errors import (
    GISError,
    InvalidGeometryError,
    InvalidGeoJSONError,
    SpatialLinkError,
)

__all__ = [
    # Geometry
    "Geometry",
    "geometry_bounds",
    # Features
    "SpatialFeature",
    # Collections
    "SpatialFeatureCollection",
    "collection_bounds",
    # GeoJSON I/O
    "export_feature_collection_to_geojson",
    "import_feature_collection_from_geojson",
    "save_geojson",
    "load_geojson",
    # Entity linking
    "feature_for_drainage_area",
    "feature_for_infrastructure_node",
    "feature_for_pipe",
    "feature_for_flow_path",
    # Examples
    "create_example_spatial_feature_collection",
    # Errors
    "GISError",
    "InvalidGeometryError",
    "InvalidGeoJSONError",
    "SpatialLinkError",
]
