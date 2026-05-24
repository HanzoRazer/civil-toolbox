"""Open channel capacity estimation and checking.

Simplified capacity checks using Manning's equation for normal depth.
These are screening-level estimates for uniform flow conditions.
"""

from __future__ import annotations

from civil_toolbox.infrastructure import OpenChannel
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError
from civil_toolbox.infrastructure_sizing.models import InfrastructureCheckResult
from civil_toolbox.infrastructure_sizing.manning import (
    manning_capacity_cfs,
    manning_velocity_fps,
    rectangular_area_sqft,
    rectangular_hydraulic_radius_ft,
    trapezoidal_area_sqft,
    trapezoidal_hydraulic_radius_ft,
    triangular_area_sqft,
    triangular_hydraulic_radius_ft,
)


def estimate_open_channel_capacity_cfs(channel: OpenChannel) -> tuple[float, float]:
    """Estimate open channel capacity using Manning's equation.

    Args:
        channel: The OpenChannel object to analyze.

    Returns:
        Tuple of (capacity_cfs, velocity_fps).

    Raises:
        InvalidSizingInputError: If channel parameters are invalid for calculation.

    Note:
        This calculates capacity at the specified channel depth.
        It assumes uniform flow and normal depth conditions.
    """
    if channel.slope_ft_per_ft <= 0:
        raise InvalidSizingInputError(
            f"Channel '{channel.name}' has zero or negative slope, "
            "cannot calculate capacity"
        )

    if channel.depth_ft <= 0:
        raise InvalidSizingInputError(
            f"Channel '{channel.name}' has zero or negative depth"
        )

    if channel.shape == "rectangular":
        if channel.bottom_width_ft is None:
            raise InvalidSizingInputError(
                f"Channel '{channel.name}' is rectangular but has no bottom width"
            )
        area = rectangular_area_sqft(channel.bottom_width_ft, channel.depth_ft)
        hydraulic_radius = rectangular_hydraulic_radius_ft(
            channel.bottom_width_ft, channel.depth_ft
        )

    elif channel.shape == "trapezoidal":
        if channel.bottom_width_ft is None:
            raise InvalidSizingInputError(
                f"Channel '{channel.name}' is trapezoidal but has no bottom width"
            )
        side_slope = channel.side_slope or 0.0
        if channel.side_slope_left is not None and channel.side_slope_right is not None:
            side_slope = (channel.side_slope_left + channel.side_slope_right) / 2.0
        area = trapezoidal_area_sqft(
            channel.bottom_width_ft, channel.depth_ft, side_slope
        )
        hydraulic_radius = trapezoidal_hydraulic_radius_ft(
            channel.bottom_width_ft, channel.depth_ft, side_slope
        )

    elif channel.shape == "triangular":
        side_slope = channel.side_slope or 0.0
        if channel.side_slope_left is not None and channel.side_slope_right is not None:
            side_slope = (channel.side_slope_left + channel.side_slope_right) / 2.0
        if side_slope <= 0:
            raise InvalidSizingInputError(
                f"Channel '{channel.name}' is triangular but has no side slope"
            )
        area = triangular_area_sqft(channel.depth_ft, side_slope)
        hydraulic_radius = triangular_hydraulic_radius_ft(channel.depth_ft, side_slope)

    elif channel.shape == "parabolic":
        raise InvalidSizingInputError(
            f"Parabolic channel capacity not yet implemented for '{channel.name}'"
        )

    else:
        raise InvalidSizingInputError(f"Unsupported channel shape: {channel.shape}")

    capacity = manning_capacity_cfs(
        area_sqft=area,
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=channel.slope_ft_per_ft,
        mannings_n=channel.mannings_n,
    )

    velocity = manning_velocity_fps(
        hydraulic_radius_ft=hydraulic_radius,
        slope_ft_per_ft=channel.slope_ft_per_ft,
        mannings_n=channel.mannings_n,
    )

    return capacity, velocity


def check_open_channel_capacity(
    channel: OpenChannel,
    design_flow_cfs: float,
) -> InfrastructureCheckResult:
    """Check if open channel can convey the design flow.

    Args:
        channel: The OpenChannel object to check.
        design_flow_cfs: Required design flow in cfs.

    Returns:
        InfrastructureCheckResult with capacity, utilization, and pass/fail.

    Note:
        This is a simplified check using uniform flow at channel depth.
        It does not consider:
        - Gradually varied flow
        - Backwater effects
        - Supercritical flow transitions
        - Freeboard requirements
    """
    if design_flow_cfs < 0:
        raise InvalidSizingInputError(
            f"design_flow_cfs cannot be negative, got {design_flow_cfs}"
        )

    result = InfrastructureCheckResult(
        element_id=channel.id,
        element_name=channel.name,
        element_type="channel",
        passes=False,
        design_flow_cfs=design_flow_cfs,
        method="Manning's equation (uniform flow)",
    )

    result.add_assumption("Uniform flow conditions assumed")
    result.add_assumption("Capacity calculated at specified channel depth")
    result.add_assumption("No backwater effects considered")
    result.add_assumption("Freeboard not included in capacity")

    if channel.slope_ft_per_ft <= 0:
        result.add_warning(
            "ZERO_SLOPE",
            f"Channel has zero or negative slope ({channel.slope_ft_per_ft}), "
            "cannot calculate capacity",
            severity="error",
        )
        return result

    try:
        capacity, velocity = estimate_open_channel_capacity_cfs(channel)
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

    if channel.lining and "grass" in channel.lining.lower():
        if velocity > 6.0:
            result.add_warning(
                "HIGH_VELOCITY_GRASS",
                f"Velocity {velocity:.2f} fps exceeds recommended maximum for grass "
                "(6.0 fps), may cause erosion",
            )
    elif velocity > 12.0:
        result.add_warning(
            "HIGH_VELOCITY",
            f"Velocity {velocity:.2f} fps exceeds typical maximum (12.0 fps)",
        )

    if velocity < 2.0:
        result.add_warning(
            "LOW_VELOCITY",
            f"Velocity {velocity:.2f} fps is below minimum (2.0 fps), "
            "may cause sediment deposition",
        )

    if channel.freeboard_ft is not None and channel.freeboard_ft > 0:
        result.add_warning(
            "FREEBOARD_NOT_CHECKED",
            f"Channel has {channel.freeboard_ft:.1f} ft freeboard specified but "
            "capacity was calculated at full depth. Effective capacity may be lower.",
            severity="info",
        )

    return result
