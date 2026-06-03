"""Inlet-control headwater estimation for culverts.

First-pass, intentionally simplified model. Under inlet control the culvert
barrel can carry more flow than the inlet will admit, so the inlet geometry
governs. When the inlet is submerged it behaves like an orifice, and this module
uses the orifice relationship as a defensible first approximation:

    Q = Cd * A * sqrt(2 * g * h)

where h is the head on the inlet measured to the centroid of the opening
(h ~= HW - D/2). Solving for headwater depth above the inlet invert:

    HW = (Q / (Cd * A))^2 / (2 * g) + D / 2

Limitations (documented, not hidden):
    - Valid for the submerged regime (HW/D >= ~1.2). For lower headwater the
      inlet behaves as a weir and this estimate is approximate; a warning is
      emitted by the orchestrator in that case.
    - Does not use FHWA HDS-5 chart-specific inlet coefficients; a single
      orifice discharge coefficient is used for all inlet types.
    - No road overtopping, no multiple-barrel interaction.

Reference:
    FHWA HDS-5, "Hydraulic Design of Highway Culverts" (3rd ed., 2012) —
    inlet-control behavior; orifice approximation per standard open-channel
    hydraulics.
"""

from __future__ import annotations

from civil_toolbox.culverts.headwater import barrel_full_area_sqft, barrel_rise_ft
from civil_toolbox.culverts.validation import require_positive
from civil_toolbox.infrastructure import Culvert

# Gravitational acceleration, US customary units.
GRAVITY_FT_PER_S2 = 32.2

# Orifice discharge coefficient for a submerged culvert inlet (typical 0.5-0.6).
DEFAULT_ORIFICE_DISCHARGE_COEFFICIENT = 0.6

# HW/D ratio at or above which the inlet is treated as submerged (orifice flow).
SUBMERGENCE_RATIO_THRESHOLD = 1.2

INLET_CONTROL_REFERENCE = (
    "FHWA HDS-5 (2012), Hydraulic Design of Highway Culverts — inlet control "
    "(submerged orifice approximation)."
)


def inlet_control_headwater_depth_ft(
    culvert: Culvert,
    design_flow_cfs: float,
    *,
    discharge_coefficient: float = DEFAULT_ORIFICE_DISCHARGE_COEFFICIENT,
) -> float:
    """Estimate inlet-control headwater depth above the inlet invert.

    Args:
        culvert: The culvert being analyzed.
        design_flow_cfs: Design flow rate in cfs (> 0).
        discharge_coefficient: Orifice discharge coefficient (default 0.6).

    Returns:
        Headwater depth above the inlet invert, in feet.

    Raises:
        InvalidCulvertInputError: If inputs/geometry are invalid.
        UnsupportedCulvertTypeError: If the shape is unsupported.
    """
    flow = require_positive(design_flow_cfs, "design_flow_cfs")
    cd = require_positive(discharge_coefficient, "discharge_coefficient")

    area = barrel_full_area_sqft(culvert)
    rise = barrel_rise_ft(culvert)

    velocity_through_opening = flow / (cd * area)
    head_on_opening = velocity_through_opening**2 / (2.0 * GRAVITY_FT_PER_S2)
    return head_on_opening + rise / 2.0


def is_inlet_submerged(headwater_depth_ft: float, barrel_rise_ft_value: float) -> bool:
    """Return True if the inlet is submerged (HW/D >= threshold)."""
    if barrel_rise_ft_value <= 0:
        return False
    return (headwater_depth_ft / barrel_rise_ft_value) >= SUBMERGENCE_RATIO_THRESHOLD


def evaluate_inlet_control_status(
    headwater_depth_ft: float,
    allowable_headwater_ft: float | None,
) -> str:
    """Classify inlet-control headwater against the allowable limit.

    Args:
        headwater_depth_ft: Computed inlet-control headwater depth.
        allowable_headwater_ft: Allowable headwater, or None if not specified.

    Returns:
        One of 'passes', 'exceeds', or 'not_evaluated' (when no allowable
        headwater is provided to compare against).
    """
    if allowable_headwater_ft is None:
        return "not_evaluated"
    return "passes" if headwater_depth_ft <= allowable_headwater_ft else "exceeds"
