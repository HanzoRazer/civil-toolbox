"""Infrastructure sizing for Civil Toolbox.

Provides simplified capacity checks for drainage infrastructure elements
using Manning's equation. These are screening-level estimates, not
detailed hydraulic analysis.

Example:
    >>> from civil_toolbox.infrastructure import Pipe
    >>> from civil_toolbox.infrastructure_sizing import check_pipe_capacity
    >>> pipe = Pipe(
    ...     id="P1", name="P-1",
    ...     diameter_in=18.0, length_ft=200.0,
    ...     slope_ft_per_ft=0.005, mannings_n=0.013,
    ... )
    >>> result = check_pipe_capacity(pipe, design_flow_cfs=10.0)
    >>> print(f"Capacity: {result.capacity_cfs:.1f} cfs, Passes: {result.passes}")

Note:
    These are simplified capacity checks using Manning's equation.
    They do not replace detailed hydraulic analysis for final design.

    Limitations:
    - Pipes/culverts: Full-flow capacity only, no inlet/outlet control
    - Channels: Uniform flow, no backwater effects
    - Detention: Volume comparison only, no routing
"""

from civil_toolbox.infrastructure_sizing.channels import (
    check_open_channel_capacity,
    estimate_open_channel_capacity_cfs,
)
from civil_toolbox.infrastructure_sizing.culverts import (
    check_culvert_capacity,
    estimate_culvert_barrel_capacity_cfs,
)
from civil_toolbox.infrastructure_sizing.detention import check_detention_storage
from civil_toolbox.infrastructure_sizing.errors import (
    CapacityCalculationError,
    InfrastructureSizingError,
    InvalidSizingInputError,
)
from civil_toolbox.infrastructure_sizing.examples import (
    create_example_channel_check,
    create_example_culvert_check,
    create_example_detention_check,
    create_example_pipe_check,
    create_example_swale_check,
)
from civil_toolbox.infrastructure_sizing.manning import (
    box_full_flow_area_sqft,
    box_full_flow_hydraulic_radius_ft,
    circular_pipe_full_flow_area_sqft,
    circular_pipe_full_flow_hydraulic_radius_ft,
    manning_capacity_cfs,
    manning_velocity_fps,
    rectangular_area_sqft,
    rectangular_hydraulic_radius_ft,
    rectangular_wetted_perimeter_ft,
    trapezoidal_area_sqft,
    trapezoidal_hydraulic_radius_ft,
    trapezoidal_wetted_perimeter_ft,
    triangular_area_sqft,
    triangular_hydraulic_radius_ft,
    triangular_wetted_perimeter_ft,
)
from civil_toolbox.infrastructure_sizing.models import (
    InfrastructureCheckResult,
    InfrastructureCheckWarning,
)
from civil_toolbox.infrastructure_sizing.pipes import (
    check_pipe_capacity,
    estimate_pipe_full_flow_capacity_cfs,
)
from civil_toolbox.infrastructure_sizing.swales import (
    check_swale_capacity,
    estimate_swale_capacity_cfs,
)
from civil_toolbox.infrastructure_sizing.validation import (
    validate_mannings_n,
    validate_positive_dimension,
    validate_positive_flow,
    validate_positive_slope,
    validate_positive_storage,
)

__all__ = [
    # Core result models
    "InfrastructureCheckResult",
    "InfrastructureCheckWarning",
    # Manning's equation
    "manning_capacity_cfs",
    "manning_velocity_fps",
    # Geometry helpers
    "circular_pipe_full_flow_area_sqft",
    "circular_pipe_full_flow_hydraulic_radius_ft",
    "box_full_flow_area_sqft",
    "box_full_flow_hydraulic_radius_ft",
    "rectangular_area_sqft",
    "rectangular_wetted_perimeter_ft",
    "rectangular_hydraulic_radius_ft",
    "trapezoidal_area_sqft",
    "trapezoidal_wetted_perimeter_ft",
    "trapezoidal_hydraulic_radius_ft",
    "triangular_area_sqft",
    "triangular_wetted_perimeter_ft",
    "triangular_hydraulic_radius_ft",
    # Pipe functions
    "estimate_pipe_full_flow_capacity_cfs",
    "check_pipe_capacity",
    # Culvert functions
    "estimate_culvert_barrel_capacity_cfs",
    "check_culvert_capacity",
    # Channel functions
    "estimate_open_channel_capacity_cfs",
    "check_open_channel_capacity",
    # Swale functions
    "estimate_swale_capacity_cfs",
    "check_swale_capacity",
    # Detention functions
    "check_detention_storage",
    # Validation
    "validate_positive_flow",
    "validate_positive_storage",
    "validate_mannings_n",
    "validate_positive_slope",
    "validate_positive_dimension",
    # Errors
    "InfrastructureSizingError",
    "InvalidSizingInputError",
    "CapacityCalculationError",
    # Examples
    "create_example_pipe_check",
    "create_example_culvert_check",
    "create_example_channel_check",
    "create_example_swale_check",
    "create_example_detention_check",
]
