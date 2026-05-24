"""Manning's equation for open channel and pipe flow.

Manning's equation: Q = (1.49/n) * A * R^(2/3) * S^(1/2)

Where:
- Q = discharge (cfs)
- n = Manning's roughness coefficient
- A = cross-sectional area (sq ft)
- R = hydraulic radius = A/P (ft)
- P = wetted perimeter (ft)
- S = slope (ft/ft)

Note: The 1.49 constant is for US customary units (ft, sec).
For SI units (m, sec), the constant is 1.0.
"""

from __future__ import annotations

import math

from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


def manning_capacity_cfs(
    area_sqft: float,
    hydraulic_radius_ft: float,
    slope_ft_per_ft: float,
    mannings_n: float,
) -> float:
    """Calculate flow capacity using Manning's equation.

    Args:
        area_sqft: Cross-sectional flow area in square feet.
        hydraulic_radius_ft: Hydraulic radius (A/P) in feet.
        slope_ft_per_ft: Channel/pipe slope in ft/ft.
        mannings_n: Manning's roughness coefficient.

    Returns:
        Flow capacity in cubic feet per second (cfs).

    Raises:
        InvalidSizingInputError: If inputs are invalid.
    """
    if area_sqft <= 0:
        raise InvalidSizingInputError(f"area_sqft must be positive, got {area_sqft}")
    if hydraulic_radius_ft <= 0:
        raise InvalidSizingInputError(
            f"hydraulic_radius_ft must be positive, got {hydraulic_radius_ft}"
        )
    if slope_ft_per_ft < 0:
        raise InvalidSizingInputError(
            f"slope_ft_per_ft cannot be negative, got {slope_ft_per_ft}"
        )
    if mannings_n <= 0:
        raise InvalidSizingInputError(f"mannings_n must be positive, got {mannings_n}")

    if slope_ft_per_ft == 0:
        return 0.0

    return (1.49 / mannings_n) * area_sqft * (hydraulic_radius_ft ** (2 / 3)) * (slope_ft_per_ft ** 0.5)


def manning_velocity_fps(
    hydraulic_radius_ft: float,
    slope_ft_per_ft: float,
    mannings_n: float,
) -> float:
    """Calculate flow velocity using Manning's equation.

    Args:
        hydraulic_radius_ft: Hydraulic radius (A/P) in feet.
        slope_ft_per_ft: Channel/pipe slope in ft/ft.
        mannings_n: Manning's roughness coefficient.

    Returns:
        Flow velocity in feet per second (fps).

    Raises:
        InvalidSizingInputError: If inputs are invalid.
    """
    if hydraulic_radius_ft <= 0:
        raise InvalidSizingInputError(
            f"hydraulic_radius_ft must be positive, got {hydraulic_radius_ft}"
        )
    if slope_ft_per_ft < 0:
        raise InvalidSizingInputError(
            f"slope_ft_per_ft cannot be negative, got {slope_ft_per_ft}"
        )
    if mannings_n <= 0:
        raise InvalidSizingInputError(f"mannings_n must be positive, got {mannings_n}")

    if slope_ft_per_ft == 0:
        return 0.0

    return (1.49 / mannings_n) * (hydraulic_radius_ft ** (2 / 3)) * (slope_ft_per_ft ** 0.5)


def circular_pipe_full_flow_area_sqft(diameter_ft: float) -> float:
    """Calculate full-flow cross-sectional area for circular pipe.

    Args:
        diameter_ft: Pipe diameter in feet.

    Returns:
        Cross-sectional area in square feet.
    """
    if diameter_ft <= 0:
        raise InvalidSizingInputError(
            f"diameter_ft must be positive, got {diameter_ft}"
        )
    return math.pi * (diameter_ft / 2) ** 2


def circular_pipe_full_flow_hydraulic_radius_ft(diameter_ft: float) -> float:
    """Calculate full-flow hydraulic radius for circular pipe.

    For a full circular pipe, R = D/4.

    Args:
        diameter_ft: Pipe diameter in feet.

    Returns:
        Hydraulic radius in feet.
    """
    if diameter_ft <= 0:
        raise InvalidSizingInputError(
            f"diameter_ft must be positive, got {diameter_ft}"
        )
    return diameter_ft / 4


def box_full_flow_area_sqft(width_ft: float, height_ft: float) -> float:
    """Calculate full-flow cross-sectional area for box section.

    Args:
        width_ft: Box width in feet.
        height_ft: Box height in feet.

    Returns:
        Cross-sectional area in square feet.
    """
    if width_ft <= 0:
        raise InvalidSizingInputError(f"width_ft must be positive, got {width_ft}")
    if height_ft <= 0:
        raise InvalidSizingInputError(f"height_ft must be positive, got {height_ft}")
    return width_ft * height_ft


def box_full_flow_hydraulic_radius_ft(width_ft: float, height_ft: float) -> float:
    """Calculate full-flow hydraulic radius for box section.

    R = A / P = (W * H) / (2W + 2H)

    Args:
        width_ft: Box width in feet.
        height_ft: Box height in feet.

    Returns:
        Hydraulic radius in feet.
    """
    if width_ft <= 0:
        raise InvalidSizingInputError(f"width_ft must be positive, got {width_ft}")
    if height_ft <= 0:
        raise InvalidSizingInputError(f"height_ft must be positive, got {height_ft}")
    area = width_ft * height_ft
    perimeter = 2 * width_ft + 2 * height_ft
    return area / perimeter


def trapezoidal_area_sqft(
    bottom_width_ft: float,
    depth_ft: float,
    side_slope: float,
) -> float:
    """Calculate cross-sectional area for trapezoidal section.

    Args:
        bottom_width_ft: Bottom width in feet.
        depth_ft: Flow depth in feet.
        side_slope: Side slope (horizontal:vertical).

    Returns:
        Cross-sectional area in square feet.
    """
    if bottom_width_ft < 0:
        raise InvalidSizingInputError(
            f"bottom_width_ft cannot be negative, got {bottom_width_ft}"
        )
    if depth_ft <= 0:
        raise InvalidSizingInputError(f"depth_ft must be positive, got {depth_ft}")
    if side_slope < 0:
        raise InvalidSizingInputError(
            f"side_slope cannot be negative, got {side_slope}"
        )
    return (bottom_width_ft + side_slope * depth_ft) * depth_ft


def trapezoidal_wetted_perimeter_ft(
    bottom_width_ft: float,
    depth_ft: float,
    side_slope: float,
) -> float:
    """Calculate wetted perimeter for trapezoidal section.

    P = B + 2 * d * sqrt(1 + z^2)

    Args:
        bottom_width_ft: Bottom width in feet.
        depth_ft: Flow depth in feet.
        side_slope: Side slope (horizontal:vertical).

    Returns:
        Wetted perimeter in feet.
    """
    if bottom_width_ft < 0:
        raise InvalidSizingInputError(
            f"bottom_width_ft cannot be negative, got {bottom_width_ft}"
        )
    if depth_ft <= 0:
        raise InvalidSizingInputError(f"depth_ft must be positive, got {depth_ft}")
    if side_slope < 0:
        raise InvalidSizingInputError(
            f"side_slope cannot be negative, got {side_slope}"
        )
    return bottom_width_ft + 2 * depth_ft * math.sqrt(1 + side_slope**2)


def trapezoidal_hydraulic_radius_ft(
    bottom_width_ft: float,
    depth_ft: float,
    side_slope: float,
) -> float:
    """Calculate hydraulic radius for trapezoidal section.

    Args:
        bottom_width_ft: Bottom width in feet.
        depth_ft: Flow depth in feet.
        side_slope: Side slope (horizontal:vertical).

    Returns:
        Hydraulic radius in feet.
    """
    area = trapezoidal_area_sqft(bottom_width_ft, depth_ft, side_slope)
    perimeter = trapezoidal_wetted_perimeter_ft(bottom_width_ft, depth_ft, side_slope)
    return area / perimeter


def rectangular_area_sqft(width_ft: float, depth_ft: float) -> float:
    """Calculate cross-sectional area for rectangular section.

    Args:
        width_ft: Channel width in feet.
        depth_ft: Flow depth in feet.

    Returns:
        Cross-sectional area in square feet.
    """
    if width_ft <= 0:
        raise InvalidSizingInputError(f"width_ft must be positive, got {width_ft}")
    if depth_ft <= 0:
        raise InvalidSizingInputError(f"depth_ft must be positive, got {depth_ft}")
    return width_ft * depth_ft


def rectangular_wetted_perimeter_ft(width_ft: float, depth_ft: float) -> float:
    """Calculate wetted perimeter for rectangular section.

    P = B + 2 * d

    Args:
        width_ft: Channel width in feet.
        depth_ft: Flow depth in feet.

    Returns:
        Wetted perimeter in feet.
    """
    if width_ft <= 0:
        raise InvalidSizingInputError(f"width_ft must be positive, got {width_ft}")
    if depth_ft <= 0:
        raise InvalidSizingInputError(f"depth_ft must be positive, got {depth_ft}")
    return width_ft + 2 * depth_ft


def rectangular_hydraulic_radius_ft(width_ft: float, depth_ft: float) -> float:
    """Calculate hydraulic radius for rectangular section.

    Args:
        width_ft: Channel width in feet.
        depth_ft: Flow depth in feet.

    Returns:
        Hydraulic radius in feet.
    """
    area = rectangular_area_sqft(width_ft, depth_ft)
    perimeter = rectangular_wetted_perimeter_ft(width_ft, depth_ft)
    return area / perimeter


def triangular_area_sqft(depth_ft: float, side_slope: float) -> float:
    """Calculate cross-sectional area for triangular section.

    A = z * d^2 (for symmetric V-channel)

    Args:
        depth_ft: Flow depth in feet.
        side_slope: Side slope (horizontal:vertical).

    Returns:
        Cross-sectional area in square feet.
    """
    if depth_ft <= 0:
        raise InvalidSizingInputError(f"depth_ft must be positive, got {depth_ft}")
    if side_slope <= 0:
        raise InvalidSizingInputError(
            f"side_slope must be positive, got {side_slope}"
        )
    return side_slope * depth_ft**2


def triangular_wetted_perimeter_ft(depth_ft: float, side_slope: float) -> float:
    """Calculate wetted perimeter for triangular section.

    P = 2 * d * sqrt(1 + z^2)

    Args:
        depth_ft: Flow depth in feet.
        side_slope: Side slope (horizontal:vertical).

    Returns:
        Wetted perimeter in feet.
    """
    if depth_ft <= 0:
        raise InvalidSizingInputError(f"depth_ft must be positive, got {depth_ft}")
    if side_slope <= 0:
        raise InvalidSizingInputError(
            f"side_slope must be positive, got {side_slope}"
        )
    return 2 * depth_ft * math.sqrt(1 + side_slope**2)


def triangular_hydraulic_radius_ft(depth_ft: float, side_slope: float) -> float:
    """Calculate hydraulic radius for triangular section.

    Args:
        depth_ft: Flow depth in feet.
        side_slope: Side slope (horizontal:vertical).

    Returns:
        Hydraulic radius in feet.
    """
    area = triangular_area_sqft(depth_ft, side_slope)
    perimeter = triangular_wetted_perimeter_ft(depth_ft, side_slope)
    return area / perimeter
