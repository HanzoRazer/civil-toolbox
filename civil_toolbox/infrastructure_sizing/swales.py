"""Swale capacity estimation and checking.

Simplified capacity checks using Manning's equation.
These are screening-level estimates for vegetated channel conveyance.
"""

from __future__ import annotations

from civil_toolbox.infrastructure import Swale
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError
from civil_toolbox.infrastructure_sizing.models import InfrastructureCheckResult
from civil_toolbox.infrastructure_sizing.manning import (
    manning_capacity_cfs,
    manning_velocity_fps,
    trapezoidal_area_sqft,
    trapezoidal_hydraulic_radius_ft,
)


def estimate_swale_capacity_cfs(swale: Swale) -> tuple[float, float]:
    """Estimate swale capacity using Manning's equation.

    Swales are modeled as trapezoidal channels.

    Args:
        swale: The Swale object to analyze.

    Returns:
        Tuple of (capacity_cfs, velocity_fps).

    Raises:
        InvalidSizingInputError: If swale parameters are invalid for calculation.

    Note:
        This calculates conveyance capacity only.
        Water quality treatment capacity is not addressed.
    """
    if swale.slope_ft_per_ft <= 0:
        raise InvalidSizingInputError(
            f"Swale '{swale.name}' has zero or negative slope, "
            "cannot calculate capacity"
        )

    if swale.depth_ft <= 0:
        raise InvalidSizingInputError(
            f"Swale '{swale.name}' has zero or negative depth"
        )

    area = trapezoidal_area_sqft(
        swale.bottom_width_ft, swale.depth_ft, swale.side_slope
    )
    hydraulic_radius = trapezoidal_hydraulic_radius_ft(
        swale.bottom_width_ft, swale.depth_ft, swale.side_slope
    )

    capacity = manning_capacity_cfs(
        area_sqft=area,
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=swale.slope_ft_per_ft,
        mannings_n=swale.mannings_n,
    )

    velocity = manning_velocity_fps(
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=swale.slope_ft_per_ft,
        mannings_n=swale.mannings_n,
    )

    return capacity, velocity


def check_swale_capacity(
    swale: Swale,
    design_flow_cfs: float,
) -> InfrastructureCheckResult:
    """Check if swale can convey the design flow.

    Args:
        swale: The Swale object to check.
        design_flow_cfs: Required design flow in cfs.

    Returns:
        InfrastructureCheckResult with capacity, utilization, and pass/fail.

    Note:
        This checks conveyance capacity only.
        Swale performance for water quality treatment is not evaluated.
        Bioswale infiltration benefits are not included.
    """
    if design_flow_cfs < 0:
        raise InvalidSizingInputError(
            f"design_flow_cfs cannot be negative, got {design_flow_cfs}"
        )

    result = InfrastructureCheckResult(
        element_id=swale.id,
        element_name=swale.name,
        element_type="swale",
        passes=False,
        design_flow_cfs=design_flow_cfs,
        method="Manning's equation (trapezoidal section)",
    )

    result.add_assumption("Trapezoidal cross-section assumed")
    result.add_assumption("Uniform flow conditions")
    result.add_assumption("Conveyance capacity only (not water quality)")
    result.add_assumption("No infiltration losses considered")

    if swale.slope_ft_per_ft <= 0:
        result.add_warning(
            "ZERO_SLOPE",
            f"Swale has zero or negative slope ({swale.slope_ft_per_ft}), "
            "cannot calculate capacity",
            severity="error",
        )
        return result

    try:
        capacity, velocity = estimate_swale_capacity_cfs(swale)
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

    max_velocity = 4.0 if swale.swale_type == "grass" else 6.0
    if velocity > max_velocity:
        result.add_warning(
            "HIGH_VELOCITY",
            f"Velocity {velocity:.2f} fps exceeds recommended maximum for "
            f"{swale.swale_type} swale ({max_velocity:.1f} fps), may cause erosion",
        )

    if velocity < 1.0:
        result.add_warning(
            "LOW_VELOCITY",
            f"Velocity {velocity:.2f} fps is very low, may cause ponding",
        )

    if swale.swale_type == "bioswale" and swale.infiltration_rate_in_per_hr:
        result.add_warning(
            "INFILTRATION_NOT_CREDITED",
            f"Bioswale has infiltration rate {swale.infiltration_rate_in_per_hr} in/hr "
            "but infiltration losses are not credited in this capacity check",
            severity="info",
        )

    if swale.check_dam_spacing_ft:
        result.add_warning(
            "CHECK_DAMS_NOT_MODELED",
            f"Check dams at {swale.check_dam_spacing_ft} ft spacing not included "
            "in hydraulic analysis. Actual capacity may differ.",
            severity="info",
        )

    return result
