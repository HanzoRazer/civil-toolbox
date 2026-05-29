# Hydraulic Grade Line Foundation

Documentation for hydraulic grade line (HGL) and energy grade line (EGL) calculations in Civil Toolbox.

## Overview

The `civil_toolbox.hydraulics` module provides HGL/EGL calculations for ordered pipe reach profiles using simplified steady-flow assumptions. It enables engineers to:

- Calculate friction losses using Manning's equation
- Propagate HGL from downstream to upstream through pipe systems
- Classify surcharge status at pipe ends
- Detect and warn about surcharged conditions

## Key Concepts

### Hydraulic Grade Line (HGL)

The HGL represents the pressure head plus elevation head at any point in the system. For pressurized flow in pipes:

```
HGL = Pressure Head + Elevation
```

### Energy Grade Line (EGL)

The EGL equals the HGL plus velocity head:

```
EGL = HGL + V²/(2g)
```

### Friction Slope

Friction slope is computed from Manning's equation rearranged:

```
Sf = [Q × n / (1.486 × A × R^(2/3))]²
```

Where:
- Q = flow rate (cfs)
- n = Manning's roughness coefficient
- A = flow area (sq ft)
- R = hydraulic radius (ft)
- 1.486 = unit conversion constant (US customary units)

### HGL Propagation

HGL increases from downstream to upstream by the friction head loss:

```
HGL_upstream = HGL_downstream + (Sf × L)
```

Where L is the reach length.

## Module Structure

```
civil_toolbox/hydraulics/
├── __init__.py      # Public API exports
├── errors.py        # Custom exceptions
├── validation.py    # Input validation
├── models.py        # Data models (PipeReachInput, results)
├── hgl.py           # Core HGL calculations
├── compute.py       # Reach and profile computation
├── builders.py      # Infrastructure model adapters
└── examples.py      # Synthetic test data
```

## Usage

### Basic Profile Calculation

```python
from civil_toolbox.hydraulics import (
    PipeReachInput,
    compute_hgl_profile,
)

# Define reaches from downstream to upstream
reaches = [
    PipeReachInput(
        id="reach_001",
        pipe_id="pipe_001",
        name="Outlet Reach",
        design_flow_cfs=10.0,
        length_ft=200.0,
        roughness_n=0.013,
        diameter_in=18.0,
        upstream_invert_elevation_ft=99.0,
        downstream_invert_elevation_ft=98.0,
        upstream_rim_elevation_ft=105.0,
        downstream_rim_elevation_ft=104.0,
    ),
    PipeReachInput(
        id="reach_002",
        pipe_id="pipe_002",
        name="Middle Reach",
        design_flow_cfs=10.0,
        length_ft=250.0,
        roughness_n=0.013,
        diameter_in=18.0,
        upstream_invert_elevation_ft=100.0,
        downstream_invert_elevation_ft=99.0,
        upstream_rim_elevation_ft=106.0,
        downstream_rim_elevation_ft=105.0,
    ),
]

# Compute profile starting from known downstream HGL
profile = compute_hgl_profile(
    reaches=reaches,
    starting_downstream_hgl_ft=100.0,
    name="Main Storm Trunk",
)

# Access results
print(f"Starting HGL: {profile.starting_downstream_hgl_ft} ft")
print(f"Ending HGL: {profile.ending_upstream_hgl_ft} ft")

for reach in profile.reaches:
    print(f"{reach.reach_id}: {reach.downstream_hgl_ft:.2f} -> {reach.upstream_hgl_ft:.2f}")
    print(f"  Surcharge: {reach.upstream_surcharge_status}")
```

### Building from Infrastructure Elements

```python
from civil_toolbox.domain.infrastructure import InfrastructureElement
from civil_toolbox.hydraulics import (
    build_pipe_reach_from_infrastructure,
    compute_hgl_profile,
)

# Create infrastructure elements
pipe = InfrastructureElement(
    name="Storm Pipe 1",
    element_type="pipe",
    length_ft=200.0,
    diameter_in=18.0,
    mannings_n=0.013,
)

# Convert to hydraulic input
reach = build_pipe_reach_from_infrastructure(
    element=pipe,
    design_flow_cfs=10.0,
    upstream_invert_elevation_ft=99.0,
    downstream_invert_elevation_ft=98.0,
)

# Compute
profile = compute_hgl_profile([reach], starting_downstream_hgl_ft=100.0)
```

### Using Synthetic Examples

```python
from civil_toolbox.hydraulics import (
    create_simple_trunk_reaches,
    create_surcharged_system_reaches,
    compute_hgl_profile,
)

# Simple system
reaches = create_simple_trunk_reaches()
profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

# System with surcharge warnings
surcharged = create_surcharged_system_reaches()
profile = compute_hgl_profile(surcharged, starting_downstream_hgl_ft=100.0)
for warning in profile.all_warnings():
    print(f"[{warning.severity}] {warning.code}: {warning.message}")
```

## Data Models

### PipeReachInput

Input data for a single pipe reach:

| Field | Type | Description |
|-------|------|-------------|
| id | str | Unique reach identifier |
| pipe_id | str | ID of source pipe |
| name | str | Human-readable name |
| design_flow_cfs | float | Design flow rate |
| length_ft | float | Reach length |
| roughness_n | float | Manning's n |
| diameter_in | float | Pipe diameter (circular) |
| width_in | float | Pipe width (rectangular) |
| height_in | float | Pipe height (rectangular) |
| upstream_invert_elevation_ft | float | Upstream invert |
| downstream_invert_elevation_ft | float | Downstream invert |
| upstream_rim_elevation_ft | float | Upstream rim |
| downstream_rim_elevation_ft | float | Downstream rim |

### PipeReachHydraulicResult

Computed results for a single reach:

| Field | Type | Description |
|-------|------|-------------|
| reach_id | str | Reach identifier |
| design_flow_cfs | float | Design flow |
| flow_area_sqft | float | Flow area |
| velocity_fps | float | Flow velocity |
| velocity_head_ft | float | V²/(2g) |
| friction_slope_ft_per_ft | float | Sf |
| friction_loss_ft | float | Sf × L |
| downstream_hgl_ft | float | HGL at downstream |
| upstream_hgl_ft | float | HGL at upstream |
| downstream_egl_ft | float | EGL at downstream |
| upstream_egl_ft | float | EGL at upstream |
| downstream_surcharge_status | str | Status at downstream |
| upstream_surcharge_status | str | Status at upstream |
| downstream_freeboard_ft | float | Rim - HGL |
| upstream_freeboard_ft | float | Rim - HGL |
| warnings | list | Reach-level warnings |

### Surcharge Status Values

- `free_surface` — HGL at or below pipe crown
- `surcharged_above_crown` — HGL above crown but at or below rim
- `surcharged_above_rim` — HGL exceeds rim elevation (generates warning)
- `unknown` — Crown elevation not available

### HydraulicProfileResult

Complete profile with all reaches:

| Field | Type | Description |
|-------|------|-------------|
| id | str | Profile identifier |
| name | str | Profile name |
| reaches | list | List of reach results |
| starting_downstream_hgl_ft | float | Starting boundary HGL |
| ending_upstream_hgl_ft | float | Final HGL at upstream end |
| warnings | list | Profile-level warnings |
| assumptions | list | Analysis assumptions |
| references | list | Engineering references |

## Assumptions and Limitations

The current implementation assumes:

1. **Steady-state flow** — No time-varying hydrographs
2. **Full-flow conditions** — Pipes are flowing full (pressurized)
3. **Uniform flow within reaches** — Single friction slope per reach
4. **No local losses** — Entrance, exit, junction, and bend losses not included
5. **Ordered reaches** — User provides reaches in downstream-to-upstream order
6. **No tailwater rating curves** — Starting HGL is user-specified

## Future Extensions

Potential enhancements for future releases:

- Partial flow (open channel) conditions
- Local/minor loss coefficients (K-factors)
- Culvert inlet/outlet control analysis
- Automatic network traversal
- Tailwater rating curve integration
- Time-varying flow analysis

## API Reference

### Errors

- `HydraulicAnalysisError` — Base exception for hydraulics
- `InvalidHydraulicInputError` — Invalid input values
- `MissingHydraulicDataError` — Required data missing
- `UnsupportedHydraulicMethodError` — Method not supported

### Core Functions

- `velocity_fps(flow_cfs, area_sqft)` — V = Q/A
- `velocity_head_ft(velocity)` — hv = V²/(2g)
- `friction_loss_ft(friction_slope, length)` — hf = Sf × L
- `friction_slope_from_manning(...)` — Manning's Sf
- `pipe_crown_elevation_ft(...)` — Crown = Invert + rise
- `classify_surcharge_status(...)` — Status classification
- `freeboard_ft(rim, hgl)` — Rim - HGL

### Compute Functions

- `compute_pipe_reach_hydraulics(reach, downstream_hgl)` — Single reach
- `compute_hgl_profile(reaches, starting_hgl, name)` — Full profile

### Builders

- `build_pipe_reach_from_infrastructure(element, flow, ...)` — Convert domain model
- `build_pipe_reaches_from_infrastructure(elements, flows)` — Batch convert

### Examples

- `create_simple_trunk_reaches()` — 3-reach storm trunk
- `create_surcharged_system_reaches()` — Undersized system
- `create_mixed_geometry_reaches()` — Circular + box
- `create_minimal_reach()` — Minimal test reach
