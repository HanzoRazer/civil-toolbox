"""Curb-opening inlet capacity estimation.

First-pass, intentionally simplified model. A curb-opening inlet intercepting
ponded flow is treated as a horizontal weir along the opening length:

    Q = Cw · L · H^(3/2)

with:
    Cw = weir coefficient (default 3.0)
    L  = curb opening length (``inlet.opening_length_ft``), in ft
    H  = head at the opening, in ft

The result is multiplied by ``inlet.effective_clogging_factor``.

Limitations (documented, not hidden):
    - Weir behavior assumed; orifice behavior under deep submergence not modeled.
    - Roadway gutter spread / cross-slope interception not modeled.

Reference:
    FHWA HEC-22 (3rd ed., 2009), Urban Drainage Design Manual — curb-opening
    inlet interception; weir approximation.
"""

from __future__ import annotations

from civil_toolbox.inlets.errors import MissingInletDataError
from civil_toolbox.inlets.models import InletCapacityResult, apply_capture_outcome
from civil_toolbox.inlets.validation import require_non_negative, require_positive
from civil_toolbox.infrastructure import Inlet

DEFAULT_CURB_WEIR_COEFFICIENT = 3.0

CURB_REFERENCE = (
    "FHWA HEC-22 (2009), Urban Drainage Design Manual — curb-opening inlet "
    "interception (weir approximation)."
)


def estimate_curb_inlet_capacity_cfs(
    inlet: Inlet,
    head_ft: float,
    *,
    weir_coefficient: float = DEFAULT_CURB_WEIR_COEFFICIENT,
) -> float:
    """Estimate curb-opening inlet interception capacity in cfs.

    Args:
        inlet: The inlet (must have an opening length).
        head_ft: Head at the opening, in feet (> 0).
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
            f"Inlet '{inlet.name}' is missing opening_length_ft"
        )

    theoretical = cw * inlet.opening_length_ft * (head**1.5)
    return theoretical * inlet.effective_clogging_factor


def check_curb_inlet_capacity(
    inlet: Inlet,
    design_flow_cfs: float,
    head_ft: float,
) -> InletCapacityResult:
    """Check whether a curb-opening inlet captures the design flow."""
    design = require_non_negative(design_flow_cfs, "design_flow_cfs")
    capacity = estimate_curb_inlet_capacity_cfs(inlet, head_ft)

    result = InletCapacityResult(
        inlet_id=inlet.id,
        inlet_type=inlet.inlet_type,
        design_flow_cfs=design,
        references=[CURB_REFERENCE],
        assumptions=[
            "Simplified weir equation Q = Cw*L*H^1.5.",
            "Curb opening length taken from opening_length_ft.",
        ],
    )
    result.add_warning(
        "simplified_weir_assumption",
        "Curb capacity uses a simplified weir equation.",
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
