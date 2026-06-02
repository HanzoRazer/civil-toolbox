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

from civil_toolbox.hydraulics.errors import (
    HydraulicAnalysisError,
    InvalidHydraulicInputError,
    MissingHydraulicDataError,
    UnsupportedHydraulicMethodError,
)
from civil_toolbox.hydraulics.models import (
    HydraulicWarning,
    PipeReachInput,
    PipeReachHydraulicResult,
    HydraulicProfileResult,
)
from civil_toolbox.hydraulics.hgl import (
    GRAVITY_FTPS2,
    velocity_fps,
    velocity_head_ft,
    friction_loss_ft,
    friction_slope_from_manning,
    pipe_crown_elevation_ft,
    classify_surcharge_status,
    freeboard_ft,
)
from civil_toolbox.hydraulics.compute import (
    compute_pipe_reach_hydraulics,
    compute_hgl_profile,
)
from civil_toolbox.hydraulics.builders import (
    build_pipe_reach_from_infrastructure,
    build_pipe_reaches_from_infrastructure,
)
from civil_toolbox.hydraulics.examples import (
    create_simple_trunk_reaches,
    create_surcharged_system_reaches,
    create_mixed_geometry_reaches,
    create_minimal_reach,
)

__all__ = [
    # Errors
    "HydraulicAnalysisError",
    "InvalidHydraulicInputError",
    "MissingHydraulicDataError",
    "UnsupportedHydraulicMethodError",
    # Models
    "HydraulicWarning",
    "PipeReachInput",
    "PipeReachHydraulicResult",
    "HydraulicProfileResult",
    # HGL calculations
    "GRAVITY_FTPS2",
    "velocity_fps",
    "velocity_head_ft",
    "friction_loss_ft",
    "friction_slope_from_manning",
    "pipe_crown_elevation_ft",
    "classify_surcharge_status",
    "freeboard_ft",
    # Compute functions
    "compute_pipe_reach_hydraulics",
    "compute_hgl_profile",
    # Builders
    "build_pipe_reach_from_infrastructure",
    "build_pipe_reaches_from_infrastructure",
    # Examples
    "create_simple_trunk_reaches",
    "create_surcharged_system_reaches",
    "create_mixed_geometry_reaches",
    "create_minimal_reach",
]
