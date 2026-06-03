"""Outlet-control headwater estimation for culverts.

First-pass, intentionally simplified model. Under outlet control the barrel and
the tailwater govern; headwater is found from an energy balance across a barrel
flowing full:

    HW = ho + H_L - dZ

where:
    ho   = hydraulic-grade elevation at the outlet above the outlet invert.
           Tailwater profiles are out of scope, so ho is taken as the larger of
           the supplied tailwater depth and the barrel rise D (i.e. the HGL is
           assumed at the crown when tailwater is unknown/below the crown).
    H_L  = total head loss = (Ke + Kexit) * V^2/2g + friction loss,
           with friction loss = Sf * L and Sf the Manning full-flow friction
           slope, Sf = (n * V / (1.49 * R^(2/3)))^2.
    dZ   = drop in invert from inlet to outlet (upstream_invert - downstream_invert),
           or slope * length when inverts are not provided.

Limitations (documented, not hidden):
    - Full-barrel flow assumed; partially-full outlet control is not modeled.
    - Tailwater is not computed (assumed at crown unless supplied).
    - Exit loss uses the full velocity head (discharge into still water).
    - No multiple-barrel interaction, no road overtopping.

Reference:
    FHWA HDS-5, "Hydraulic Design of Highway Culverts" (3rd ed., 2012) —
    outlet-control full-flow energy equation; entrance-loss coefficients Ke.
"""

from __future__ import annotations

from civil_toolbox.culverts.headwater import (
    barrel_full_area_sqft,
    barrel_full_hydraulic_radius_ft,
    barrel_rise_ft,
)
from civil_toolbox.culverts.validation import require_non_negative, require_positive
from civil_toolbox.infrastructure import Culvert

# Gravitational acceleration, US customary units.
GRAVITY_FT_PER_S2 = 32.2

# Manning constant for US customary units (Sf uses the same 1.49 as the
# infrastructure sizing Manning helpers, for internal consistency).
MANNING_CONSTANT_US = 1.49

# Exit loss coefficient (full velocity head into still water).
EXIT_LOSS_COEFFICIENT = 1.0

# Entrance loss coefficients Ke by inlet type (FHWA HDS-5, Table of entrance
# loss coefficients). Keyed to the inlet types the Culvert model allows.
ENTRANCE_LOSS_COEFFICIENTS = {
    "projecting": 0.9,
    "mitered": 0.7,
    "headwall": 0.5,
    "wingwall": 0.5,
    "beveled": 0.2,
}
DEFAULT_ENTRANCE_LOSS_COEFFICIENT = 0.5

OUTLET_CONTROL_REFERENCE = (
    "FHWA HDS-5 (2012), Hydraulic Design of Highway Culverts — outlet control "
    "full-flow energy equation; entrance loss coefficients Ke."
)


def entrance_loss_coefficient(culvert: Culvert) -> float:
    """Return the entrance loss coefficient Ke for the culvert.

    Uses ``culvert.inlet_coefficient`` when provided (treated as an explicit Ke
    override); otherwise maps ``culvert.inlet_type`` to a standard HDS-5 value,
    falling back to a square-edge default.
    """
    if culvert.inlet_coefficient is not None:
        return require_non_negative(culvert.inlet_coefficient, "inlet_coefficient")
    return ENTRANCE_LOSS_COEFFICIENTS.get(
        culvert.inlet_type, DEFAULT_ENTRANCE_LOSS_COEFFICIENT
    )


def invert_drop_ft(culvert: Culvert) -> float:
    """Return the inlet-to-outlet invert drop (dZ) in feet.

    Uses explicit inverts when both are present, otherwise slope * length.
    """
    if culvert.upstream_invert_ft is not None and culvert.downstream_invert_ft is not None:
        return culvert.upstream_invert_ft - culvert.downstream_invert_ft
    return culvert.slope_ft_per_ft * culvert.length_ft


def outlet_control_headwater_depth_ft(
    culvert: Culvert,
    design_flow_cfs: float,
    tailwater_depth_ft: float | None = None,
) -> float:
    """Estimate outlet-control headwater depth above the inlet invert.

    Args:
        culvert: The culvert being analyzed.
        design_flow_cfs: Design flow rate in cfs (> 0).
        tailwater_depth_ft: Tailwater depth above the outlet invert, if known.
            When None, the outlet HGL is assumed at the barrel crown.

    Returns:
        Headwater depth above the inlet invert, in feet.

    Raises:
        InvalidCulvertInputError: If inputs/geometry are invalid.
        UnsupportedCulvertTypeError: If the shape is unsupported.
    """
    flow = require_positive(design_flow_cfs, "design_flow_cfs")
    length = require_positive(culvert.length_ft, "length_ft")
    area = barrel_full_area_sqft(culvert)
    hydraulic_radius = barrel_full_hydraulic_radius_ft(culvert)
    rise = barrel_rise_ft(culvert)

    velocity_fps = flow / area
    velocity_head_ft = velocity_fps**2 / (2.0 * GRAVITY_FT_PER_S2)

    friction_slope = (
        culvert.mannings_n
        * velocity_fps
        / (MANNING_CONSTANT_US * hydraulic_radius ** (2.0 / 3.0))
    ) ** 2
    friction_loss_ft = friction_slope * length

    ke = entrance_loss_coefficient(culvert)
    head_loss_ft = (ke + EXIT_LOSS_COEFFICIENT) * velocity_head_ft + friction_loss_ft

    tailwater = 0.0 if tailwater_depth_ft is None else require_non_negative(
        tailwater_depth_ft, "tailwater_depth_ft"
    )
    outlet_hydraulic_grade_ft = max(tailwater, rise)

    return outlet_hydraulic_grade_ft + head_loss_ft - invert_drop_ft(culvert)


def evaluate_outlet_control_status(
    headwater_depth_ft: float,
    allowable_headwater_ft: float | None,
) -> str:
    """Classify outlet-control headwater against the allowable limit.

    Args:
        headwater_depth_ft: Computed outlet-control headwater depth.
        allowable_headwater_ft: Allowable headwater, or None if not specified.

    Returns:
        One of 'passes', 'exceeds', or 'not_evaluated' (when no allowable
        headwater is provided to compare against).
    """
    if allowable_headwater_ft is None:
        return "not_evaluated"
    return "passes" if headwater_depth_ft <= allowable_headwater_ft else "exceeds"
