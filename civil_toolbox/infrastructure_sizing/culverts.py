"""Culvert capacity estimation and checking.

Simplified capacity checks using Manning's equation for barrel capacity.
These are screening-level estimates, not detailed hydraulic analysis.

Note: This module calculates barrel capacity only. It does not perform:
- Inlet control analysis
- Outlet control analysis
- Headwater calculations
- Tailwater effects

For detailed culvert analysis, use HY-8, HEC-RAS, or similar software.
"""

from __future__ import annotations

from civil_toolbox.infrastructure import Culvert
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError
from civil_toolbox.infrastructure_sizing.models import InfrastructureCheckResult
from civil_toolbox.infrastructure_sizing.manning import (
    manning_capacity_cfs,
    manning_velocity_fps,
    circular_pipe_full_flow_area_sqft,
    circular_pipe_full_flow_hydraulic_radius_ft,
    box_full_flow_area_sqft,
    box_full_flow_hydraulic_radius_ft,
)


def estimate_culvert_barrel_capacity_cfs(culvert: Culvert) -> tuple[float, float]:
    """Estimate culvert barrel capacity using Manning's equation.

    This calculates the full-flow capacity of the culvert barrel,
    which may not be the controlling capacity (inlet or outlet control).

    Args:
        culvert: The Culvert object to analyze.

    Returns:
        Tuple of (capacity_cfs, velocity_fps).

    Raises:
        InvalidSizingInputError: If culvert parameters are invalid for calculation.

    Note:
        This is barrel capacity only. Actual culvert capacity depends on:
        - Inlet geometry and submergence
        - Outlet conditions and tailwater
        - Whether inlet or outlet control governs
    """
    if culvert.slope_ft_per_ft <= 0:
        raise InvalidSizingInputError(
            f"Culvert '{culvert.name}' has zero or negative slope, "
            "cannot calculate barrel capacity"
        )

    if culvert.shape == "circular":
        if culvert.diameter_in is None:
            raise InvalidSizingInputError(
                f"Culvert '{culvert.name}' is circular but has no diameter"
            )
        diameter_ft = culvert.diameter_in / 12.0
        area = circular_pipe_full_flow_area_sqft(diameter_ft)
        hydraulic_radius = circular_pipe_full_flow_hydraulic_radius_ft(diameter_ft)

    elif culvert.shape in ("box", "arch", "elliptical"):
        if culvert.width_in is None or culvert.height_in is None:
            raise InvalidSizingInputError(
                f"Culvert '{culvert.name}' is {culvert.shape} but missing width or height"
            )
        width_ft = culvert.width_in / 12.0
        height_ft = culvert.height_in / 12.0
        area = box_full_flow_area_sqft(width_ft, height_ft)
        hydraulic_radius = box_full_flow_hydraulic_radius_ft(width_ft, height_ft)

    else:
        raise InvalidSizingInputError(f"Unsupported culvert shape: {culvert.shape}")

    capacity = manning_capacity_cfs(
        area_sqft=area,
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=culvert.slope_ft_per_ft,
        mannings_n=culvert.mannings_n,
    )

    velocity = manning_velocity_fps(
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=culvert.slope_ft_per_ft,
        mannings_n=culvert.mannings_n,
    )

    return capacity, velocity


def check_culvert_capacity(
    culvert: Culvert,
    design_flow_cfs: float,
) -> InfrastructureCheckResult:
    """Check if culvert barrel can convey the design flow.

    Args:
        culvert: The Culvert object to check.
        design_flow_cfs: Required design flow in cfs.

    Returns:
        InfrastructureCheckResult with capacity, utilization, and pass/fail.

    Note:
        This is a simplified screening check using barrel capacity.
        Actual culvert performance depends on inlet/outlet control.
        Use detailed analysis (HY-8, HEC-RAS) for final design.
    """
    if design_flow_cfs < 0:
        raise InvalidSizingInputError(
            f"design_flow_cfs cannot be negative, got {design_flow_cfs}"
        )

    result = InfrastructureCheckResult(
        element_id=culvert.id,
        element_name=culvert.name,
        element_type="culvert",
        passes=False,
        design_flow_cfs=design_flow_cfs,
        method="Manning's equation (barrel capacity)",
    )

    result.add_assumption("Full-flow barrel capacity only")
    result.add_assumption("Inlet/outlet control analysis not performed")
    result.add_assumption("No headwater calculation")
    result.add_assumption("No tailwater effects considered")

    if culvert.slope_ft_per_ft <= 0:
        result.add_warning(
            "ZERO_SLOPE",
            f"Culvert has zero or negative slope ({culvert.slope_ft_per_ft}), "
            "cannot calculate barrel capacity",
            severity="error",
        )
        return result

    try:
        capacity, velocity = estimate_culvert_barrel_capacity_cfs(culvert)
    except InvalidSizingInputError as e:
        result.add_warning("CALCULATION_ERROR", str(e), severity="error")
        return result

    result.capacity_cfs = capacity
    result.velocity_fps = velocity

    if design_flow_cfs == 0:
        result.passes = True
        return result

    result.utilization_ratio = design_flow_cfs / capacity
    result.passes = design_flow_cfs <= capacity

    if velocity < 2.5:
        result.add_warning(
            "LOW_VELOCITY",
            f"Velocity {velocity:.2f} fps is below minimum (2.5 fps), "
            "may cause sediment deposition",
        )
    elif velocity > 20.0:
        result.add_warning(
            "HIGH_VELOCITY",
            f"Velocity {velocity:.2f} fps exceeds recommended maximum (20.0 fps), "
            "may cause outlet scour",
        )

    result.add_warning(
        "BARREL_CAPACITY_ONLY",
        "This is barrel capacity only. Inlet/outlet control may govern. "
        "Use HY-8 or HEC-RAS for detailed analysis.",
        severity="info",
    )

    return result
