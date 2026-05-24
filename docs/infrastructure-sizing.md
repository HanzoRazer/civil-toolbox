# Infrastructure Sizing

The infrastructure sizing module provides simplified capacity checks for drainage infrastructure elements using Manning's equation.

## Overview

**Important**: These are screening-level capacity estimates, not detailed hydraulic analysis. They do not replace HEC-RAS, HY-8, or other detailed analysis software for final design.

The module provides:

- **Manning's equation** functions for open channel flow
- **Pipe capacity** checks (full flow)
- **Culvert barrel capacity** checks (not inlet/outlet control)
- **Open channel capacity** checks (uniform flow)
- **Swale capacity** checks
- **Detention storage** checks (volume comparison only)

## Core Concepts

### InfrastructureCheckResult

All capacity checks return a structured result:

```python
from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult

result = InfrastructureCheckResult(
    element_id="p1",
    element_name="P-1",
    element_type="pipe",
    passes=True,
    capacity_cfs=15.5,
    design_flow_cfs=10.0,
    velocity_fps=5.2,
    utilization_ratio=0.645,  # Auto-calculated
    method="Manning's equation (full flow)",
    warnings=[...],
    assumptions=[...],
)

print(f"Passes: {result.passes}")
print(f"Utilization: {result.utilization_ratio:.1%}")
print(f"Overcapacity: {result.is_overcapacity}")
```

### InfrastructureCheckWarning

Warnings capture non-fatal issues:

```python
from civil_toolbox.infrastructure_sizing import InfrastructureCheckWarning

warning = InfrastructureCheckWarning(
    warning_code="LOW_VELOCITY",
    message="Velocity 1.5 fps is below minimum (2.0 fps)",
    element_id="p1",
    element_name="P-1",
    severity="warning",  # "warning", "error", or "info"
)
```

## Manning's Equation

The foundation for capacity calculations:

```python
from civil_toolbox.infrastructure_sizing import (
    manning_capacity_cfs,
    manning_velocity_fps,
)

# Q = (1.49/n) * A * R^(2/3) * S^(1/2)
capacity = manning_capacity_cfs(
    area_sqft=7.07,
    hydraulic_radius_ft=0.5,
    slope_ft_per_ft=0.005,
    mannings_n=0.013,
)

velocity = manning_velocity_fps(
    hydraulic_radius_ft=0.5,
    slope_ft_per_ft=0.005,
    mannings_n=0.013,
)
```

### Geometry Helpers

```python
from civil_toolbox.infrastructure_sizing import (
    circular_pipe_full_flow_area_sqft,
    circular_pipe_full_flow_hydraulic_radius_ft,
    box_full_flow_area_sqft,
    box_full_flow_hydraulic_radius_ft,
    trapezoidal_area_sqft,
    trapezoidal_hydraulic_radius_ft,
    rectangular_area_sqft,
    rectangular_hydraulic_radius_ft,
    triangular_area_sqft,
    triangular_hydraulic_radius_ft,
)

# Circular pipe: R = D/4
area = circular_pipe_full_flow_area_sqft(diameter_ft=1.5)
radius = circular_pipe_full_flow_hydraulic_radius_ft(diameter_ft=1.5)

# Trapezoidal channel
area = trapezoidal_area_sqft(bottom_width_ft=6.0, depth_ft=3.0, side_slope=2.0)
radius = trapezoidal_hydraulic_radius_ft(bottom_width_ft=6.0, depth_ft=3.0, side_slope=2.0)
```

## Pipe Capacity

```python
from civil_toolbox.infrastructure import Pipe
from civil_toolbox.infrastructure_sizing import (
    estimate_pipe_full_flow_capacity_cfs,
    check_pipe_capacity,
)

pipe = Pipe(
    id="P1",
    name="P-1",
    shape="circular",
    diameter_in=18.0,
    length_ft=200.0,
    slope_ft_per_ft=0.005,
    mannings_n=0.013,
)

# Get capacity and velocity
capacity_cfs, velocity_fps = estimate_pipe_full_flow_capacity_cfs(pipe)
print(f"Capacity: {capacity_cfs:.1f} cfs, Velocity: {velocity_fps:.1f} fps")

# Check against design flow
result = check_pipe_capacity(pipe, design_flow_cfs=10.0)
print(f"Passes: {result.passes}")
print(f"Utilization: {result.utilization_ratio:.1%}")

for warning in result.warnings:
    print(f"Warning: {warning.message}")
```

**Limitations:**
- Full-flow capacity only
- No inlet/outlet losses
- No tailwater effects
- No surcharge analysis

**Warnings generated:**
- `LOW_VELOCITY`: Below 2.0 fps (sediment deposition risk)
- `HIGH_VELOCITY`: Above 15.0 fps
- `HIGH_UTILIZATION`: Above 80% capacity
- `ZERO_SLOPE`: Cannot calculate capacity

## Culvert Capacity

```python
from civil_toolbox.infrastructure import Culvert
from civil_toolbox.infrastructure_sizing import (
    estimate_culvert_barrel_capacity_cfs,
    check_culvert_capacity,
)

culvert = Culvert(
    id="BC1",
    name="BC-1",
    shape="box",
    width_in=48.0,
    height_in=36.0,
    length_ft=80.0,
    slope_ft_per_ft=0.01,
    mannings_n=0.012,
    inlet_type="headwall",
)

# Get barrel capacity (not inlet/outlet controlled)
capacity_cfs, velocity_fps = estimate_culvert_barrel_capacity_cfs(culvert)

# Check against design flow
result = check_culvert_capacity(culvert, design_flow_cfs=100.0)
```

**Limitations:**
- Barrel capacity only (Manning's equation)
- No inlet control analysis
- No outlet control analysis
- No headwater calculation
- Use HY-8 or HEC-RAS for detailed analysis

**Warnings generated:**
- `BARREL_CAPACITY_ONLY`: Always included as informational
- `LOW_VELOCITY`: Below 2.5 fps
- `HIGH_VELOCITY`: Above 20.0 fps

## Open Channel Capacity

```python
from civil_toolbox.infrastructure import OpenChannel
from civil_toolbox.infrastructure_sizing import (
    estimate_open_channel_capacity_cfs,
    check_open_channel_capacity,
)

channel = OpenChannel(
    id="CH1",
    name="CH-1",
    shape="trapezoidal",
    bottom_width_ft=6.0,
    depth_ft=3.0,
    side_slope=2.0,
    length_ft=500.0,
    slope_ft_per_ft=0.002,
    mannings_n=0.030,
    lining="Grass",
)

# Get capacity at full depth
capacity_cfs, velocity_fps = estimate_open_channel_capacity_cfs(channel)

# Check against design flow
result = check_open_channel_capacity(channel, design_flow_cfs=50.0)
```

**Supported shapes:**
- Rectangular
- Trapezoidal
- Triangular
- Parabolic (not yet implemented)

**Limitations:**
- Uniform flow assumed
- No backwater effects
- Freeboard not included in capacity

**Warnings generated:**
- `HIGH_VELOCITY_GRASS`: Above 6.0 fps for grass-lined channels
- `HIGH_VELOCITY`: Above 12.0 fps for other channels
- `LOW_VELOCITY`: Below 2.0 fps
- `FREEBOARD_NOT_CHECKED`: When freeboard is specified

## Swale Capacity

```python
from civil_toolbox.infrastructure import Swale
from civil_toolbox.infrastructure_sizing import (
    estimate_swale_capacity_cfs,
    check_swale_capacity,
)

swale = Swale(
    id="SW1",
    name="SW-1",
    swale_type="grass",
    bottom_width_ft=2.0,
    depth_ft=1.0,
    side_slope=4.0,
    length_ft=300.0,
    slope_ft_per_ft=0.01,
    mannings_n=0.035,
)

# Get conveyance capacity
capacity_cfs, velocity_fps = estimate_swale_capacity_cfs(swale)

# Check against design flow
result = check_swale_capacity(swale, design_flow_cfs=5.0)
```

**Limitations:**
- Conveyance capacity only (not water quality)
- Infiltration losses not credited
- Check dams not modeled

**Warnings generated:**
- `HIGH_VELOCITY`: Above 4.0 fps (grass) or 6.0 fps (other)
- `LOW_VELOCITY`: Below 1.0 fps
- `INFILTRATION_NOT_CREDITED`: For bioswales with infiltration rate
- `CHECK_DAMS_NOT_MODELED`: When check dam spacing specified

## Detention Storage

```python
from civil_toolbox.infrastructure import DetentionFacility, StageStoragePoint
from civil_toolbox.infrastructure_sizing import check_detention_storage

facility = DetentionFacility(
    id="DP1",
    name="DP-1",
    stage_storage=[
        StageStoragePoint(stage_ft=90.0, storage_cuft=0),
        StageStoragePoint(stage_ft=92.0, storage_cuft=25000),
        StageStoragePoint(stage_ft=94.0, storage_cuft=60000),
        StageStoragePoint(stage_ft=96.0, storage_cuft=110000),
    ],
    spillway_elevation_ft=95.5,
)

# Check storage adequacy
result = check_detention_storage(facility, required_storage_cuft=80000.0)
print(f"Available: {result.storage_cuft:,.0f} cu ft")
print(f"Required: {result.required_storage_cuft:,.0f} cu ft")
print(f"Passes: {result.passes}")
```

**Limitations:**
- Volume comparison only
- No inflow/outflow routing
- No peak reduction analysis
- No outlet sizing evaluation

**Warnings generated:**
- `ROUTING_REQUIRED`: Always included as informational
- `HIGH_UTILIZATION`: Above 90% storage used
- `SPILLWAY_LIMITS_STORAGE`: When spillway limits usable volume
- `PERMANENT_POOL`: When permanent pool depth specified
- `NO_STORAGE_DATA`: When no stage-storage or geometry available

## Error Handling

```python
from civil_toolbox.infrastructure_sizing import (
    InfrastructureSizingError,  # Base error
    InvalidSizingInputError,     # Invalid input (extends ValueError)
    CapacityCalculationError,    # Calculation failure
)

try:
    result = check_pipe_capacity(pipe, design_flow_cfs=-5.0)
except InvalidSizingInputError as e:
    print(f"Invalid input: {e}")
```

## Validation Utilities

```python
from civil_toolbox.infrastructure_sizing import (
    validate_positive_flow,
    validate_positive_storage,
    validate_mannings_n,
    validate_positive_slope,
    validate_positive_dimension,
)

flow = validate_positive_flow(10.0, "design_flow")
storage = validate_positive_storage(50000.0, "required_storage")
n = validate_mannings_n(0.013, "mannings_n")
slope = validate_positive_slope(0.01, "slope")
diameter = validate_positive_dimension(18.0, "diameter_in")
```

## Example Checks

Example results are available for testing:

```python
from civil_toolbox.infrastructure_sizing import (
    create_example_pipe_check,
    create_example_culvert_check,
    create_example_channel_check,
    create_example_swale_check,
    create_example_detention_check,
)

# Get example results
pipe_result = create_example_pipe_check()
culvert_result = create_example_culvert_check()
channel_result = create_example_channel_check()
swale_result = create_example_swale_check()
detention_result = create_example_detention_check()
```

## Design Principles

1. **Design flow is explicit** — Design flow must be passed as a parameter, never derived automatically
2. **No mutations** — Infrastructure objects are not modified by check functions
3. **Simplified checks** — These are screening estimates, not detailed hydraulic analysis
4. **Warnings and assumptions** — Results include warnings and assumptions for transparency
5. **Structured output** — All checks return InfrastructureCheckResult for consistent handling
