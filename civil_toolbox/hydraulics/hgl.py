"""HGL and EGL calculation utilities."""

from __future__ import annotations

from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError


GRAVITY_FTPS2 = 32.174


def velocity_fps(flow_cfs: float, area_sqft: float) -> float:
    """Calculate flow velocity from discharge and area.

    V = Q / A

    Args:
        flow_cfs: Flow rate in cubic feet per second.
        area_sqft: Cross-sectional area in square feet.

    Returns:
        Velocity in feet per second.

    Raises:
        InvalidHydraulicInputError: If area is zero or negative.
    """
    if flow_cfs == 0:
        return 0.0
    if area_sqft <= 0:
        raise InvalidHydraulicInputError(
            f"area_sqft must be positive for velocity calculation, got {area_sqft}"
        )
    return flow_cfs / area_sqft


def velocity_head_ft(velocity: float) -> float:
    """Calculate velocity head.

    hv = V² / (2g)

    Args:
        velocity: Velocity in feet per second.

    Returns:
        Velocity head in feet.
    """
    return (velocity ** 2) / (2 * GRAVITY_FTPS2)


def friction_loss_ft(friction_slope_ft_per_ft: float, length_ft: float) -> float:
    """Calculate friction head loss.

    hf = Sf × L

    Args:
        friction_slope_ft_per_ft: Friction slope (ft/ft).
        length_ft: Reach length in feet.

    Returns:
        Friction head loss in feet.
    """
    return friction_slope_ft_per_ft * length_ft


def friction_slope_from_manning(
    flow_cfs: float,
    area_sqft: float,
    hydraulic_radius_ft: float,
    mannings_n: float,
) -> float:
    """Calculate friction slope using Manning's equation rearranged.

    Sf = [Q × n / (1.486 × A × R^(2/3))]²

    Args:
        flow_cfs: Flow rate in cubic feet per second.
        area_sqft: Cross-sectional area in square feet.
        hydraulic_radius_ft: Hydraulic radius in feet.
        mannings_n: Manning's roughness coefficient.

    Returns:
        Friction slope in ft/ft.
    """
    if flow_cfs == 0:
        return 0.0
    if area_sqft <= 0:
        raise InvalidHydraulicInputError(
            f"area_sqft must be positive, got {area_sqft}"
        )
    if hydraulic_radius_ft <= 0:
        raise InvalidHydraulicInputError(
            f"hydraulic_radius_ft must be positive, got {hydraulic_radius_ft}"
        )
    if mannings_n <= 0:
        raise InvalidHydraulicInputError(
            f"mannings_n must be positive, got {mannings_n}"
        )

    conveyance_factor = 1.486 * area_sqft * (hydraulic_radius_ft ** (2 / 3))
    sf = ((flow_cfs * mannings_n) / conveyance_factor) ** 2
    return sf


def pipe_crown_elevation_ft(
    invert_elevation_ft: float | None,
    diameter_in: float | None = None,
    height_in: float | None = None,
) -> float | None:
    """Calculate pipe crown elevation.

    Crown = Invert + rise (diameter or height converted to feet)

    Args:
        invert_elevation_ft: Invert elevation in feet.
        diameter_in: Pipe diameter for circular pipes (inches).
        height_in: Pipe height for box pipes (inches).

    Returns:
        Crown elevation in feet, or None if cannot be calculated.
    """
    if invert_elevation_ft is None:
        return None

    rise_ft: float | None = None
    if diameter_in is not None:
        rise_ft = diameter_in / 12.0
    elif height_in is not None:
        rise_ft = height_in / 12.0

    if rise_ft is None:
        return None

    return invert_elevation_ft + rise_ft


def classify_surcharge_status(
    hgl_ft: float,
    crown_elevation_ft: float | None,
    rim_elevation_ft: float | None,
) -> str:
    """Classify surcharge status based on HGL relative to crown and rim.

    Classification logic:
    - If crown is missing: unknown
    - If HGL <= crown: free_surface
    - If rim exists and HGL > rim: surcharged_above_rim
    - If HGL > crown (but not above rim): surcharged_above_crown

    Args:
        hgl_ft: Hydraulic grade line elevation in feet.
        crown_elevation_ft: Pipe crown elevation in feet, or None.
        rim_elevation_ft: Rim/ground elevation in feet, or None.

    Returns:
        Surcharge status string.
    """
    if crown_elevation_ft is None:
        return "unknown"

    if hgl_ft <= crown_elevation_ft:
        return "free_surface"

    if rim_elevation_ft is not None and hgl_ft > rim_elevation_ft:
        return "surcharged_above_rim"

    return "surcharged_above_crown"


def freeboard_ft(
    rim_elevation_ft: float | None,
    hgl_ft: float,
) -> float | None:
    """Calculate freeboard from rim to HGL.

    Args:
        rim_elevation_ft: Rim elevation in feet, or None.
        hgl_ft: Hydraulic grade line elevation in feet.

    Returns:
        Freeboard in feet (positive if HGL below rim), or None.
    """
    if rim_elevation_ft is None:
        return None
    return rim_elevation_ft - hgl_ft
