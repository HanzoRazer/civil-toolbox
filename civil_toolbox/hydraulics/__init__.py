"""Hydraulics module for Civil Toolbox.

Provides hydraulic grade line (HGL) and energy grade line (EGL) calculations
for ordered pipe reach profiles using simplified steady-flow assumptions.

This foundation supports:
- Pipe reach hydraulic inputs
- Downstream-to-upstream HGL profile calculation
- Velocity and friction loss computations
- Surcharge status classification
- Profile warnings and assumptions

Limitations:
- Steady uniform flow only (no dynamic routing)
- Ordered reaches only (no automatic network traversal)
- Minor losses not included
- No inlet/outlet control for culverts
- No tailwater rating curves

Example:
    >>> from civil_toolbox.hydraulics import (
    ...     PipeReachInput,
    ...     compute_hgl_profile,
    ... )
    >>> reach = PipeReachInput(
    ...     id="reach_001",
    ...     pipe_id="pipe_001",
    ...     name="Reach 1",
    ...     design_flow_cfs=10.0,
    ...     length_ft=200.0,
    ...     diameter_in=18.0,
    ...     roughness_n=0.013,
    ...     downstream_invert_elevation_ft=98.0,
    ...     upstream_invert_elevation_ft=99.0,
    ... )
    >>> profile = compute_hgl_profile(
    ...     reaches=[reach],
    ...     downstream_hgl_ft=100.5,
    ... )
"""

# Public API will be exposed after implementation
__all__: list[str] = []
