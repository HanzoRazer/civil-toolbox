"""Pipe capacity estimation and checking.

Simplified capacity checks using Manning's equation for full-flow conditions.
These are screening-level estimates, not detailed hydraulic analysis.
"""

from __future__ import annotations

from civil_toolbox.infrastructure import Pipe
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


def estimate_pipe_full_flow_capacity_cfs(pipe: Pipe) -> tuple[float, float]:
    """Estimate pipe capacity at full flow using Manning's equation.

    Args:
        pipe: The Pipe object to analyze.

    Returns:
        Tuple of (capacity_cfs, velocity_fps).

    Raises:
        InvalidSizingInputError: If pipe parameters are invalid for calculation.

    Note:
        This is a simplified full-flow capacity estimate. It does not account for:
        - Inlet/outlet losses
        - Partial flow conditions
        - Surcharge conditions
        - Tailwater effects
    """
    if pipe.slope_ft_per_ft <= 0:
        raise InvalidSizingInputError(
            f"Pipe '{pipe.name}' has zero or negative slope, cannot calculate capacity"
        )

    if pipe.shape == "circular":
        if pipe.diameter_in is None:
            raise InvalidSizingInputError(
                f"Pipe '{pipe.name}' is circular but has no diameter"
            )
        diameter_ft = pipe.diameter_in / 12.0
        area = circular_pipe_full_flow_area_sqft(diameter_ft)
        hydraulic_radius = circular_pipe_full_flow_hydraulic_radius_ft(diameter_ft)

    elif pipe.shape in ("box", "arch", "elliptical"):
        if pipe.width_in is None or pipe.height_in is None:
            raise InvalidSizingInputError(
                f"Pipe '{pipe.name}' is {pipe.shape} but missing width or height"
            )
        width_ft = pipe.width_in / 12.0
        height_ft = pipe.height_in / 12.0
        area = box_full_flow_area_sqft(width_ft, height_ft)
        hydraulic_radius = box_full_flow_hydraulic_radius_ft(width_ft, height_ft)

    else:
        raise InvalidSizingInputError(f"Unsupported pipe shape: {pipe.shape}")

    capacity = manning_capacity_cfs(
        area_sqft=area,
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=pipe.slope_ft_per_ft,
        mannings_n=pipe.mannings_n,
    )

    velocity = manning_velocity_fps(
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=pipe.slope_ft_per_ft,
        mannings_n=pipe.mannings_n,
    )

    return capacity, velocity


def check_pipe_capacity(
    pipe: Pipe,
    design_flow_cfs: float,
) -> InfrastructureCheckResult:
    """Check if pipe can convey the design flow.

    Args:
        pipe: The Pipe object to check.
        design_flow_cfs: Required design flow in cfs.

    Returns:
        InfrastructureCheckResult with capacity, utilization, and pass/fail.

    Note:
        This is a simplified screening check using full-flow Manning's equation.
        It does not replace detailed hydraulic analysis for final design.
    """
    if design_flow_cfs < 0:
        raise InvalidSizingInputError(
            f"design_flow_cfs cannot be negative, got {design_flow_cfs}"
        )

    result = InfrastructureCheckResult(
        element_id=pipe.id,
        element_name=pipe.name,
        element_type="pipe",
        passes=False,
        design_flow_cfs=design_flow_cfs,
        method="Manning's equation (full flow)",
    )

    result.add_assumption("Full-flow conditions assumed")
    result.add_assumption("No inlet/outlet losses considered")
    result.add_assumption("No tailwater effects considered")

    if pipe.slope_ft_per_ft <= 0:
        result.add_warning(
            "ZERO_SLOPE",
            f"Pipe has zero or negative slope ({pipe.slope_ft_per_ft}), cannot calculate capacity",
            severity="error",
        )
        return result

    try:
        capacity, velocity = estimate_pipe_full_flow_capacity_cfs(pipe)
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

    if velocity < 2.0:
        result.add_warning(
            "LOW_VELOCITY",
            f"Velocity {velocity:.2f} fps is below minimum (2.0 fps), may cause sediment deposition",
        )
    elif velocity > 15.0:
        result.add_warning(
            "HIGH_VELOCITY",
            f"Velocity {velocity:.2f} fps exceeds recommended maximum (15.0 fps)",
        )

    if result.utilization_ratio > 0.8 and result.passes:
        result.add_warning(
            "HIGH_UTILIZATION",
            f"Utilization {result.utilization_ratio:.1%} is above 80%, limited capacity margin",
        )

    return result
