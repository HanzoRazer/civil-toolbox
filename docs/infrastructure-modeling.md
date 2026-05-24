# Infrastructure Modeling

The infrastructure module provides data models for drainage infrastructure elements including pipes, culverts, channels, inlets, detention facilities, outlet structures, and swales.

## Overview

The infrastructure module provides:

- **InfrastructureNode**: Connection points (manholes, junctions, outfalls)
- **Pipe**: Circular, box, arch, and elliptical pipes
- **Inlet**: Grate, curb opening, combination, and slotted inlets
- **Culvert**: Road crossings with inlet/outlet control
- **OpenChannel**: Rectangular, trapezoidal, triangular channels
- **DetentionFacility**: Detention/retention ponds with stage-storage
- **OutletStructure**: Orifices, weirs, risers, combined outlets
- **Swale**: Vegetated conveyance channels
- **InfrastructureNetwork**: Connected network of elements

## Core Element Models

### InfrastructureNode

Connection points in the network:

```python
from civil_toolbox.infrastructure import InfrastructureNode

node = InfrastructureNode(
    id="MH1",
    name="MH-1",
    node_type="manhole",  # junction, manhole, inlet, outfall, storage, divider
    invert_elevation_ft=95.0,
    rim_elevation_ft=100.0,
)

# Calculated property
print(node.depth_ft)  # 5.0
```

### Pipe

Conduits for conveying stormwater:

```python
from civil_toolbox.infrastructure import Pipe

# Circular pipe
pipe = Pipe(
    id="P1",
    name="P-1",
    shape="circular",
    diameter_in=18.0,
    length_ft=200.0,
    slope_ft_per_ft=0.005,
    mannings_n=0.013,
    material="RCP",
    upstream_node_id="MH1",
    downstream_node_id="MH2",
)

# Box pipe
box_pipe = Pipe(
    id="BP1",
    name="BP-1",
    shape="box",
    width_in=48.0,
    height_in=36.0,
    length_ft=100.0,
)

# Unit conversions
print(pipe.diameter_ft)  # 1.5 (18 / 12)
print(box_pipe.width_ft)  # 4.0
print(box_pipe.height_ft)  # 3.0
```

Supported shapes: `circular`, `box`, `arch`, `elliptical`

### Culvert

Road/embankment crossings:

```python
from civil_toolbox.infrastructure import Culvert

culvert = Culvert(
    id="C1",
    name="BC-1",
    shape="box",
    width_in=48.0,
    height_in=36.0,
    length_ft=80.0,
    slope_ft_per_ft=0.01,
    mannings_n=0.012,
    inlet_type="headwall",  # projecting, mitered, headwall, wingwall, beveled
    embankment_height_ft=12.0,
    allowable_headwater_ft=8.0,
)

print(culvert.rise_ft)  # 3.0
print(culvert.span_ft)  # 4.0
```

### Inlet

Surface runoff collection:

```python
from civil_toolbox.infrastructure import Inlet

inlet = Inlet(
    id="I1",
    name="I-1",
    inlet_type="grate",  # grate, curb_opening, combination, slotted
    grate_length_in=24.0,
    grate_width_in=24.0,
    clogging_factor=0.5,  # 0.0 = clean, 1.0 = fully clogged
    node_id="MH1",
)

# Effective capacity factor
print(inlet.effective_clogging_factor)  # 0.5
```

### OpenChannel

Natural or constructed channels:

```python
from civil_toolbox.infrastructure import OpenChannel

channel = OpenChannel(
    id="CH1",
    name="CH-1",
    shape="trapezoidal",  # rectangular, trapezoidal, triangular, parabolic
    bottom_width_ft=6.0,
    depth_ft=3.0,
    side_slope=2.0,  # horizontal:vertical
    length_ft=500.0,
    slope_ft_per_ft=0.002,
    mannings_n=0.030,
    lining="Grass",
)

# Calculated property
print(channel.top_width_ft)  # 18.0 (6 + 2*2*3)

# Asymmetric side slopes
channel2 = OpenChannel(
    id="CH2",
    name="CH-2",
    shape="trapezoidal",
    bottom_width_ft=6.0,
    depth_ft=3.0,
    side_slope_left=2.0,
    side_slope_right=3.0,
    length_ft=500.0,
)
```

### DetentionFacility

Stormwater storage facilities:

```python
from civil_toolbox.infrastructure import DetentionFacility, StageStoragePoint

facility = DetentionFacility(
    id="DP1",
    name="DP-1",
    facility_type="detention",  # detention, retention, infiltration, constructed_wetland
    pond_bottom_elevation_ft=90.0,
    pond_bottom_area_sqft=10000.0,
    side_slope=3.0,
    maximum_depth_ft=6.0,
    stage_storage=[
        StageStoragePoint(stage_ft=90.0, storage_cuft=0),
        StageStoragePoint(stage_ft=92.0, storage_cuft=25000),
        StageStoragePoint(stage_ft=94.0, storage_cuft=60000),
        StageStoragePoint(stage_ft=96.0, storage_cuft=110000),
    ],
    spillway_elevation_ft=95.5,
    spillway_width_ft=10.0,
)

# Interpolate storage at any stage
print(facility.storage_at_stage(93.0))  # 42500 (linear interpolation)
print(facility.total_storage_cuft)  # 110000
```

### OutletStructure

Discharge control structures:

```python
from civil_toolbox.infrastructure import OutletStructure

outlet = OutletStructure(
    id="OS1",
    name="OS-1",
    outlet_type="combined",  # orifice, weir, riser, culvert, combined
    invert_elevation_ft=90.0,
    orifice_diameter_in=6.0,
    orifice_coefficient=0.6,
    weir_length_ft=5.0,
    weir_coefficient=3.33,
    weir_crest_elevation_ft=94.0,
)

# Calculated property
print(outlet.orifice_area_sqft)  # ~0.196 sq ft
```

### Swale

Vegetated conveyance:

```python
from civil_toolbox.infrastructure import Swale

swale = Swale(
    id="SW1",
    name="SW-1",
    swale_type="grass",  # grass, bioswale, rock, concrete
    bottom_width_ft=2.0,
    depth_ft=1.0,
    side_slope=4.0,
    length_ft=300.0,
    slope_ft_per_ft=0.01,
    mannings_n=0.035,
    vegetation_type="Bermuda grass",
    check_dam_spacing_ft=50.0,
    infiltration_rate_in_per_hr=1.0,  # For bioswales
)

# Calculated properties
print(swale.top_width_ft)  # 10.0 (2 + 2*4*1)
print(swale.cross_sectional_area_sqft)  # 6.0
```

## Infrastructure Network

Networks manage connected elements with validation:

```python
from civil_toolbox.infrastructure import (
    InfrastructureNetwork,
    InfrastructureNode,
    Pipe,
    Inlet,
)

network = InfrastructureNetwork(
    id="net1",
    name="Main Storm System",
    description="Example drainage network",
)

# Add nodes
network.add_node(InfrastructureNode(id="MH1", name="MH-1", node_type="manhole"))
network.add_node(InfrastructureNode(id="MH2", name="MH-2", node_type="manhole"))
network.add_node(InfrastructureNode(id="OUT1", name="Outfall-1", node_type="outfall"))

# Add elements
network.add_element(Pipe(
    id="P1", name="P-1",
    diameter_in=18.0, length_ft=200.0,
    upstream_node_id="MH1", downstream_node_id="MH2",
))
network.add_element(Inlet(id="I1", name="I-1", node_id="MH1"))

# Query elements
pipe = network.get_element("P1")
node = network.get_node("MH1")

# Iterate by type
for pipe in network.iter_pipes():
    print(f"{pipe.name}: {pipe.diameter_in}\"")

# Validate connectivity
result = network.validate()
print(f"Valid: {result.is_valid}")
for warning in result.warnings:
    print(f"Warning: {warning.message}")
for error in result.errors:
    print(f"Error: {error}")
```

### Network Validation

The `validate()` method checks:

- All node references exist
- All element-to-node connections are valid
- Disconnected nodes generate warnings

```python
result = network.validate()

if not result.is_valid:
    for error in result.errors:
        print(f"ERROR: {error}")

for warning in result.warnings:
    print(f"WARNING [{warning.warning_code}]: {warning.message}")
```

## Infrastructure Schedules

Generate tabular schedules for reporting:

```python
from civil_toolbox.infrastructure import (
    InfrastructureSchedule,
    InfrastructureScheduleRow,
)

schedule = InfrastructureSchedule(
    name="Pipe Schedule",
    schedule_type="pipe",
)

schedule.add_row(InfrastructureScheduleRow(
    element_id="P1",
    element_name="P-1",
    element_type="pipe",
    station="10+00",
    size="18\" RCP",
    material="RCP",
    length_ft=200.0,
    slope_percent=0.5,
    invert_in_ft=95.0,
    invert_out_ft=94.0,
    capacity_cfs=15.5,
))

for row in schedule:
    print(f"{row.element_name}: {row.size}, {row.length_ft} LF")
```

## Validation Utilities

Validation functions for infrastructure properties:

```python
from civil_toolbox.infrastructure import (
    validate_positive,
    validate_non_negative,
    validate_mannings_n,
    validate_slope,
    validate_pipe_shape,
    validate_inlet_type,
    validate_channel_shape,
    validate_outlet_type,
)

# All raise InvalidInfrastructureError on failure
diameter = validate_positive(18.0, "diameter_in")
slope = validate_non_negative(0.0, "slope")
n = validate_mannings_n(0.013, "mannings_n")
shape = validate_pipe_shape("CIRCULAR")  # Returns "circular"
```

## Error Handling

```python
from civil_toolbox.infrastructure import (
    InfrastructureError,       # Base error
    InvalidInfrastructureError,  # Invalid data (extends ValueError)
    InfrastructureValidationError,  # Validation failures
    NodeNotFoundError,         # Missing node (extends KeyError)
    ElementNotFoundError,      # Missing element (extends KeyError)
    NetworkValidationError,    # Network-level validation
)

try:
    pipe = network.get_element("nonexistent")
except ElementNotFoundError as e:
    print(f"Element not found: {e}")
```

## Serialization

All models support `to_dict()` and `from_dict()` for JSON serialization:

```python
import json

# Serialize
data = network.to_dict()
json_str = json.dumps(data)

# Deserialize
data = json.loads(json_str)
restored = InfrastructureNetwork.from_dict(data)
```

## Example Data

Synthetic example data is available for testing:

```python
from civil_toolbox.infrastructure import (
    create_example_node,
    create_example_pipe,
    create_example_box_culvert,
    create_example_inlet,
    create_example_channel,
    create_example_detention,
    create_example_outlet,
    create_example_swale,
    create_example_network,
)

# Complete example network with multiple element types
network = create_example_network()

# Individual examples
pipe = create_example_pipe()
culvert = create_example_box_culvert()
detention = create_example_detention()
```

Note: Example data is synthetic and marked with `metadata["synthetic"] = True`. Do not use for engineering design or permitting.
