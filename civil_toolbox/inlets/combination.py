"""Combination inlet capacity estimation.

A combination inlet pairs a grate with a curb opening. This first-pass model
estimates each component that is geometrically present and sums them:

    Q_combination = Q_grate + Q_curb

Limitations (documented, not hidden):
    - Grate/curb interaction effects are not modeled (simple sum).
    - Inherits the grate (orifice) and curb (weir) simplifications.

Reference:
    FHWA HEC-22 (3rd ed., 2009), Urban Drainage Design Manual — combination
    inlet interception.
"""

from __future__ import annotations

from civil_toolbox.inlets.curb import (
    CURB_REFERENCE,
    estimate_curb_inlet_capacity_cfs,
)
from civil_toolbox.inlets.errors import MissingInletDataError
from civil_toolbox.inlets.grate import (
    GRATE_REFERENCE,
    estimate_grate_inlet_capacity_cfs,
)
from civil_toolbox.inlets.models import InletCapacityResult, apply_capture_outcome
from civil_toolbox.inlets.validation import require_non_negative
from civil_toolbox.infrastructure import Inlet


def _has_grate(inlet: Inlet) -> bool:
    return inlet.grate_length_in is not None and inlet.grate_width_in is not None


def _has_curb(inlet: Inlet) -> bool:
    return inlet.opening_length_ft is not None


def estimate_combination_inlet_capacity_cfs(inlet: Inlet, head_ft: float) -> float:
    """Estimate combination inlet capacity as grate + curb components.

    Args:
        inlet: The inlet (needs grate dims and/or an opening length).
        head_ft: Head over the inlet, in feet (> 0).

    Returns:
        Summed effective capacity in cfs.

    Raises:
        MissingInletDataError: If neither grate nor curb geometry is present.
        InvalidInletInputError: If head is non-positive.
    """
    if not _has_grate(inlet) and not _has_curb(inlet):
        raise MissingInletDataError(
            f"Inlet '{inlet.name}' has neither grate dimensions nor an opening length"
        )

    capacity = 0.0
    if _has_grate(inlet):
        capacity += estimate_grate_inlet_capacity_cfs(inlet, head_ft)
    if _has_curb(inlet):
        capacity += estimate_curb_inlet_capacity_cfs(inlet, head_ft)
    return capacity


def check_combination_inlet_capacity(
    inlet: Inlet,
    design_flow_cfs: float,
    head_ft: float,
) -> InletCapacityResult:
    """Check whether a combination inlet captures the design flow."""
    design = require_non_negative(design_flow_cfs, "design_flow_cfs")
    capacity = estimate_combination_inlet_capacity_cfs(inlet, head_ft)

    result = InletCapacityResult(
        inlet_id=inlet.id,
        inlet_type=inlet.inlet_type,
        design_flow_cfs=design,
        references=[GRATE_REFERENCE, CURB_REFERENCE],
        assumptions=[
            "Combination capacity = grate component + curb component.",
            "Grate uses gross opening area; curb uses opening_length_ft.",
        ],
    )
    result.add_warning(
        "interaction_effects_not_modeled",
        "Grate/curb interaction effects are not modeled; capacities are summed.",
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
