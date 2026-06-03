"""Inlet capacity analysis orchestrator.

Dispatches to the appropriate capacity check by ``inlet.inlet_type`` and returns
an :class:`InletCapacityResult`. Supported types match the domain ``Inlet``
model: grate, curb_opening, combination, slotted.

This is first-pass screening, not a substitute for the full FHWA HEC-22
procedure (gutter spread, cross-slope, sag/grade distinction).
"""

from __future__ import annotations

from civil_toolbox.inlets.combination import check_combination_inlet_capacity
from civil_toolbox.inlets.curb import check_curb_inlet_capacity
from civil_toolbox.inlets.errors import UnsupportedInletTypeError
from civil_toolbox.inlets.grate import check_grate_inlet_capacity
from civil_toolbox.inlets.models import InletCapacityResult
from civil_toolbox.inlets.slotted import check_slotted_inlet_capacity
from civil_toolbox.infrastructure import Inlet

# Dispatch table: domain inlet_type -> capacity check function.
_DISPATCH = {
    "grate": check_grate_inlet_capacity,
    "curb_opening": check_curb_inlet_capacity,
    "combination": check_combination_inlet_capacity,
    "slotted": check_slotted_inlet_capacity,
}


def analyze_inlet_capacity(
    inlet: Inlet,
    design_flow_cfs: float,
    head_ft: float,
) -> InletCapacityResult:
    """Run a first-pass inlet capacity check, dispatching by inlet type.

    Args:
        inlet: The inlet to analyze.
        design_flow_cfs: Approaching design flow, in cfs (>= 0).
        head_ft: Head over the inlet, in feet (> 0).

    Returns:
        A populated :class:`InletCapacityResult`.

    Raises:
        UnsupportedInletTypeError: If the inlet type has no capacity method.
        InvalidInletInputError / MissingInletDataError: On invalid/missing data.
    """
    check = _DISPATCH.get(inlet.inlet_type)
    if check is None:
        raise UnsupportedInletTypeError(
            f"Unsupported inlet_type for capacity analysis: '{inlet.inlet_type}' "
            f"(supported: {sorted(_DISPATCH)})"
        )
    return check(inlet, design_flow_cfs, head_ft)
