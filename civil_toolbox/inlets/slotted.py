"""Slotted inlet capacity estimation.

(This module covers the ``slotted`` inlet type. The original handoff named a
"drop" inlet, but the domain ``Inlet`` model validates only
{grate, curb_opening, combination, slotted}; ``slotted`` is the real supported
type, so the foundation models it rather than adding a new domain type.)

First-pass, intentionally simplified model. A slotted drain inlet behaves like a
long, narrow weir along the slot. Per HEC-22 slotted inlets are treated like
equivalent-length curb-opening inlets, so this uses the same weir form:

    Q = Cw · L · H^(3/2)

with:
    Cw = weir coefficient (default 3.0)
    L  = slot length (``inlet.opening_length_ft``), in ft
    H  = head over the slot, in ft

The result is multiplied by ``inlet.effective_clogging_factor``.

Limitations (documented, not hidden):
    - Modeled as an equivalent curb-opening weir; slot-width and longitudinal
      flow capture effects are not modeled.
    - Roadway gutter spread / cross-slope interception not modeled.

Reference:
    FHWA HEC-22 (3rd ed., 2009), Urban Drainage Design Manual — slotted drain
    inlets (equivalent curb-opening weir approximation).
"""

from __future__ import annotations

from civil_toolbox.inlets.errors import MissingInletDataError
from civil_toolbox.inlets.models import InletCapacityResult, apply_capture_outcome
from civil_toolbox.inlets.validation import require_non_negative, require_positive
from civil_toolbox.infrastructure import Inlet

DEFAULT_SLOTTED_WEIR_COEFFICIENT = 3.0

SLOTTED_REFERENCE = (
    "FHWA HEC-22 (2009), Urban Drainage Design Manual — slotted drain inlets "
    "(equivalent curb-opening weir approximation)."
)


def estimate_slotted_inlet_capacity_cfs(
    inlet: Inlet,
    head_ft: float,
    *,
    weir_coefficient: float = DEFAULT_SLOTTED_WEIR_COEFFICIENT,
) -> float:
    """Estimate slotted inlet interception capacity in cfs.

    Args:
        inlet: The inlet (must have an opening/slot length).
        head_ft: Head over the slot, in feet (> 0).
        weir_coefficient: Weir coefficient (default 3.0).

    Returns:
        Effective capacity in cfs (weir capacity × effective clogging factor).

    Raises:
        InvalidInletInputError: If head/coefficient are non-positive.
        MissingInletDataError: If opening_length_ft is missing.
    """
    head = require_positive(head_ft, "head_ft")
    cw = require_positive(weir_coefficient, "weir_coefficient")
    if inlet.opening_length_ft is None:
        raise MissingInletDataError(
            f"Inlet '{inlet.name}' is missing opening_length_ft (slot length)"
        )

    theoretical = cw * inlet.opening_length_ft * (head**1.5)
    return theoretical * inlet.effective_clogging_factor


def check_slotted_inlet_capacity(
    inlet: Inlet,
    design_flow_cfs: float,
    head_ft: float,
) -> InletCapacityResult:
    """Check whether a slotted inlet captures the design flow."""
    design = require_non_negative(design_flow_cfs, "design_flow_cfs")
    capacity = estimate_slotted_inlet_capacity_cfs(inlet, head_ft)

    result = InletCapacityResult(
        inlet_id=inlet.id,
        inlet_type=inlet.inlet_type,
        design_flow_cfs=design,
        references=[SLOTTED_REFERENCE],
        assumptions=[
            "Slotted inlet modeled as an equivalent curb-opening weir.",
            "Slot length taken from opening_length_ft.",
        ],
    )
    result.add_warning(
        "slotted_inlet_simplified",
        "Slotted inlet capacity uses a simplified equivalent-weir equation.",
        severity="info",
    )
    result.add_warning(
        "roadway_spread_not_modeled",
        "Roadway gutter spread / cross-slope interception is not modeled.",
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
