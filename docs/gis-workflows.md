# GIS Workflows

The GIS module provides spatial feature models, GeoJSON import/export, and entity linking utilities for map-based drainage analysis workflows.

## Overview

Civil Toolbox supports GeoJSON-based spatial features for linking drainage areas, flow paths, and infrastructure assets to map-ready geometry. This foundation enables future map UI, plan review, and terrain integration workflows.

## Spatial Features

### Geometry Types

The module supports three GeoJSON geometry types:

| Type | Use Case | Example |
|------|----------|---------|
| Point | Infrastructure nodes, inlets, outlets | `[100.0, 50.0]` |
| LineString | Pipes, flow paths, channels | `[[0, 0], [10, 10]]` |
| Polygon | Drainage areas, project boundaries | `[[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]` |

### Feature Roles

Each spatial feature has a role indicating its purpose:

| Role | Description |
|------|-------------|
| `drainage_area` | Polygon representing a contributing watershed |
| `flow_path` | Line representing water travel path |
| `infrastructure_node` | Point representing a network junction |
| `infrastructure_link` | Line representing a pipe or channel |
| `project_boundary` | Polygon defining project extents |
| `reference` | Supporting reference geometry |
| `other` | General purpose features |

## Entity Linking

Spatial features link to domain and infrastructure entities via `entity_id` and `entity_type` fields:

```python
from civil_toolbox.gis import (
    feature_for_drainage_area,
    feature_for_infrastructure_node,
    feature_for_pipe,
    feature_for_flow_path,
)
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.infrastructure.nodes import InfrastructureNode

# Link a drainage area to polygon geometry
area = DrainageArea(id="da_001", name="Basin A", area_acres=10.5)
polygon_coords = [[[0, 0], [100, 0], [100, 100], [0, 100], [0, 0]]]
feature = feature_for_drainage_area(area, polygon_coords)

# Link an infrastructure node to point geometry
node = InfrastructureNode(id="mh_001", name="MH-1", node_type="manhole")
point_coords = [50.0, 50.0]
feature = feature_for_infrastructure_node(node, point_coords)
```

Feature IDs use the pattern `feature_{entity_id}` for deterministic linkage.

## GeoJSON Import and Export

### Export to GeoJSON

```python
from civil_toolbox.gis import (
    SpatialFeatureCollection,
    export_feature_collection_to_geojson,
    save_geojson,
)

collection = SpatialFeatureCollection(
    id="site_001",
    name="Site Features",
    features=[...],
    coordinate_reference="EPSG:4326",
)

# Export to dict
geojson = export_feature_collection_to_geojson(collection)

# Save to file
save_geojson(collection, "site.geojson")
```

### Import from GeoJSON

```python
from civil_toolbox.gis import (
    import_feature_collection_from_geojson,
    load_geojson,
)

# Import from dict
collection = import_feature_collection_from_geojson(geojson_data)

# Load from file
collection = load_geojson("site.geojson")
```

## Feature Collections

Collections group related features and support queries:

```python
from civil_toolbox.gis import SpatialFeatureCollection, collection_bounds

# Find features by entity
pipe_features = collection.find_by_entity("pipe_001")

# Find features by role
all_nodes = collection.find_by_role("infrastructure_node")

# Get specific feature
feature = collection.get_feature("feature_mh_001")

# Calculate bounding box
bounds = collection_bounds(collection)  # (min_x, min_y, max_x, max_y)
```

## Bounding Boxes

Calculate bounding boxes for geometry and collections:

```python
from civil_toolbox.gis import Geometry, geometry_bounds, collection_bounds

# Single geometry
geom = Geometry(geometry_type="Point", coordinates=[100.0, 50.0])
bounds = geometry_bounds(geom)  # (100.0, 50.0, 100.0, 50.0)

# Collection of features
bounds = collection_bounds(collection)  # (min_x, min_y, max_x, max_y)
```

## Example GeoJSON Workflow

```python
from civil_toolbox.gis import (
    Geometry,
    SpatialFeature,
    SpatialFeatureCollection,
    save_geojson,
    load_geojson,
    collection_bounds,
)

# Create features
inlet = SpatialFeature(
    id="inlet_001",
    geometry=Geometry(geometry_type="Point", coordinates=[100.0, 50.0]),
    feature_role="infrastructure_node",
    entity_id="in_001",
    entity_type="InfrastructureNode",
    properties={"name": "Inlet 1", "node_type": "inlet"},
)

pipe = SpatialFeature(
    id="pipe_001",
    geometry=Geometry(
        geometry_type="LineString",
        coordinates=[[100.0, 50.0], [150.0, 50.0]],
    ),
    feature_role="infrastructure_link",
    entity_id="p_001",
    entity_type="Pipe",
    properties={"name": "Pipe 1", "diameter_in": 18.0},
)

# Create collection
collection = SpatialFeatureCollection(
    id="network_001",
    name="Storm Network",
    features=[inlet, pipe],
    coordinate_reference="local_project_coordinates",
)

# Save to file
save_geojson(collection, "network.geojson")

# Load and query
loaded = load_geojson("network.geojson")
nodes = loaded.find_by_role("infrastructure_node")
bounds = collection_bounds(loaded)
```

## Limitations

The current GIS foundation does not include:

- Interactive map UI
- Shapely/GeoPandas spatial operations
- Coordinate reprojection
- Terrain processing or watershed delineation
- Raster analysis
- CAD/DWG import
- Geometry editing tools

These capabilities are planned for future series.

## Future Work

The GIS foundation enables future development of:

- Map-based project visualization
- Drainage area delineation workflows
- Infrastructure layout tools
- Plan review and annotation
- Terrain integration
- GIS data import/export pipelines
