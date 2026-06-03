"""Grate inlet capacity estimation.

First-pass, intentionally simplified model. A grate inlet intercepting ponded
flow is treated as a submerged orifice:

    Q = C · A · sqrt(2 · g · H)

with:
    C = orifice discharge coefficient (default 0.6)
    A = gross grate opening area (length × width), in sq ft
    H = head over the grate, in ft

The result is multiplied by ``inlet.effective_clogging_factor`` so a non-zero
clogging factor reduces the capacity.

Limitations (documented, not hidden):
    - Gross opening area is used; bar blockage / open-area ratio not modeled.
    - Orifice (submerged) behavior assumed; weir behavior at very shallow head
      is not modeled.
    - No gutter spread / roadway cross-slope interception modeling.

Reference:
    FHWA HEC-22 (3rd ed., 2009), Urban Drainage Design Manual — grate inlet
    interception; orifice approximation per standard hydraulics.
"""

from __future__ import annotations

from civil_toolbox.inlets.errors import MissingInletDataError
from civil_toolbox.inlets.models import InletCapacityResult, apply_capture_outcome
from civil_toolbox.inlets.validation import require_non_negative, require_positive
from civil_toolbox.infrastructure import Inlet

GRAVITY_FT_PER_S2 = 32.2
DEFAULT_GRATE_DISCHARGE_COEFFICIENT = 0.6

GRATE_REFERENCE = (
    "FHWA HEC-22 (2009), Urban Drainage Design Manual — grate inlet interception "
    "(orifice approximation)."
)


def grate_gross_area_sqft(inlet: Inlet) -> float:
    """Return the gross grate opening area in square feet.

    Raises:
        MissingInletDataError: If grate dimensions are missing.
    """
    if inlet.grate_length_in is None or inlet.grate_width_in is None:
        raise MissingInletDataError(
            f"Inlet '{inlet.name}' is missing grate_length_in/grate_width_in"
        )
    return (inlet.grate_length_in * inlet.grate_width_in) / 144.0


def estimate_grate_inlet_capacity_cfs(
    inlet: Inlet,
    head_ft: float,
    *,
    discharge_coefficient: float = DEFAULT_GRATE_DISCHARGE_COEFFICIENT,
) -> float:
    """Estimate grate inlet interception capacity in cfs.

    Args:
        inlet: The inlet (must have grate dimensions).
        head_ft: Head over the grate, in feet (> 0).
        discharge_coefficient: Orifice discharge coefficient (default 0.6).

    Returns:
        Effective capacity in cfs (gross orifice capacity × effective clogging
        factor).

    Raises:
        InvalidInletInputError: If head/coefficient are non-positive.
        MissingInletDataError: If grate dimensions are missing.
    """
    head = require_positive(head_ft, "head_ft")
    cd = require_positive(discharge_coefficient, "discharge_coefficient")
    area = grate_gross_area_sqft(inlet)

    theoretical = cd * area * (2.0 * GRAVITY_FT_PER_S2 * head) ** 0.5
    return theoretical * inlet.effective_clogging_factor


def check_grate_inlet_capacity(
    inlet: Inlet,
    design_flow_cfs: float,
    head_ft: float,
) -> InletCapacityResult:
    """Check whether a grate inlet captures the design flow."""
    design = require_non_negative(design_flow_cfs, "design_flow_cfs")
    capacity = estimate_grate_inlet_capacity_cfs(inlet, head_ft)

    result = InletCapacityResult(
        inlet_id=inlet.id,
        inlet_type=inlet.inlet_type,
        design_flow_cfs=design,
        references=[GRATE_REFERENCE],
        assumptions=[
            "Gross grate opening area used; bar blockage and open-area ratio not modeled.",
            "Simplified orifice equation Q = C*A*sqrt(2gH).",
        ],
    )
    result.add_warning(
        "simplified_orifice_assumption",
        "Grate capacity uses a simplified submerged-orifice equation.",
        severity="info",
    )
    if inlet.effective_clogging_factor < 1.0:
        result.add_warning(
            "capacity_reduced_by_clogging_factor",
            f"Capacity reduced by clogging factor "
            f"(effective factor {inlet.effective_clogging_factor:.2f}).",
            severity="warning",
        )

    return apply_capture_outcome(result, capacity, design)
