"""Culvert analysis orchestrator.

Combines the reused barrel-capacity screening, the inlet-control and
outlet-control headwater estimates, and the governing-headwater combiner into a
single auditable :class:`CulvertAnalysisResult`.

This is a first-pass screening analysis, not a substitute for FHWA HY-8 or
HEC-RAS. All simplifying assumptions are recorded on the result.
"""

from __future__ import annotations

from civil_toolbox.culverts.errors import (
    InvalidCulvertInputError,
    UnsupportedCulvertTypeError,
)
from civil_toolbox.culverts.headwater import (
    barrel_rise_ft,
    estimate_headwater_depth_ft,
    estimate_headwater_elevation_ft,
)
from civil_toolbox.culverts.inlet_control import (
    INLET_CONTROL_REFERENCE,
    evaluate_inlet_control_status,
    inlet_control_headwater_depth_ft,
    is_inlet_submerged,
)
from civil_toolbox.culverts.models import CulvertAnalysisResult
from civil_toolbox.culverts.outlet_control import (
    OUTLET_CONTROL_REFERENCE,
    evaluate_outlet_control_status,
    outlet_control_headwater_depth_ft,
)
from civil_toolbox.culverts.validation import require_non_negative
from civil_toolbox.infrastructure import Culvert
from civil_toolbox.infrastructure_sizing.culverts import (
    estimate_culvert_barrel_capacity_cfs,
)
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError

BARREL_CAPACITY_REFERENCE = (
    "Chow (1959), Open Channel Hydraulics — Manning's equation "
    "(full-barrel capacity)."
)

_STANDARD_ASSUMPTIONS = (
    "Single-barrel analysis; multiple-barrel interaction not modeled.",
    "Steady flow.",
    "Inlet control via submerged-orifice approximation.",
    "Outlet control via full-flow energy equation.",
    "Tailwater profile not computed (assumed at barrel crown unless supplied).",
    "Road overtopping not evaluated.",
)


def analyze_culvert(
    culvert: Culvert,
    design_flow_cfs: float,
    tailwater_depth_ft: float | None = None,
) -> CulvertAnalysisResult:
    """Run a first-pass culvert analysis.

    Args:
        culvert: The culvert to analyze.
        design_flow_cfs: Design flow rate in cfs (>= 0).
        tailwater_depth_ft: Optional tailwater depth above the outlet invert.

    Returns:
        A populated :class:`CulvertAnalysisResult`. Failures in sub-analyses are
        recorded as warnings and reflected in the control statuses rather than
        raised, so a result is always returned.

    Raises:
        InvalidCulvertInputError: If design_flow_cfs is negative.
    """
    flow = require_non_negative(design_flow_cfs, "design_flow_cfs")

    result = CulvertAnalysisResult(culvert_id=culvert.id, design_flow_cfs=flow)
    result.references.extend(
        [INLET_CONTROL_REFERENCE, OUTLET_CONTROL_REFERENCE, BARREL_CAPACITY_REFERENCE]
    )
    result.assumptions.extend(_STANDARD_ASSUMPTIONS)
    if culvert.shape in ("arch", "elliptical"):
        result.assumptions.append(
            f"{culvert.shape} barrel approximated as a rectangular (box) section."
        )

    # Barrel capacity — reuse the existing infrastructure sizing screening.
    try:
        capacity_cfs, velocity_fps = estimate_culvert_barrel_capacity_cfs(culvert)
        result.barrel_capacity_cfs = capacity_cfs
        result.barrel_velocity_fps = velocity_fps
    except InvalidSizingInputError as exc:
        result.add_warning("BARREL_CAPACITY_UNAVAILABLE", str(exc), severity="warning")

    if flow == 0:
        result.add_warning(
            "ZERO_FLOW",
            "Design flow is zero; headwater analysis not performed.",
            severity="info",
        )
        result.inlet_control_status = "not_evaluated"
        result.outlet_control_status = "not_evaluated"
        return result

    # Headwater (inlet and outlet control) — requires barrel geometry.
    try:
        inlet_hw_ft = inlet_control_headwater_depth_ft(culvert, flow)
        outlet_hw_ft = outlet_control_headwater_depth_ft(
            culvert, flow, tailwater_depth_ft=tailwater_depth_ft
        )
        rise_ft = barrel_rise_ft(culvert)
    except (InvalidCulvertInputError, UnsupportedCulvertTypeError) as exc:
        result.add_warning("HEADWATER_UNAVAILABLE", str(exc), severity="error")
        result.inlet_control_status = "not_evaluated"
        result.outlet_control_status = "not_evaluated"
        return result

    result.inlet_control_headwater_ft = inlet_hw_ft
    result.outlet_control_headwater_ft = outlet_hw_ft

    governing_depth_ft, governing_control = estimate_headwater_depth_ft(
        inlet_hw_ft, outlet_hw_ft
    )
    result.headwater_depth_ft = governing_depth_ft
    result.governing_control = governing_control
    result.headwater_elevation_ft = estimate_headwater_elevation_ft(
        governing_depth_ft, culvert.upstream_invert_ft
    )

    allowable = culvert.allowable_headwater_ft
    result.inlet_control_status = evaluate_inlet_control_status(inlet_hw_ft, allowable)
    result.outlet_control_status = evaluate_outlet_control_status(outlet_hw_ft, allowable)

    if not is_inlet_submerged(inlet_hw_ft, rise_ft):
        result.add_warning(
            "UNSUBMERGED_INLET",
            "Inlet is unsubmerged (HW/D < 1.2); the orifice inlet-control "
            "estimate is approximate in the weir-flow regime.",
            severity="info",
        )

    if allowable is not None and governing_depth_ft > allowable:
        result.add_warning(
            "HEADWATER_EXCEEDS_ALLOWABLE",
            f"Governing headwater {governing_depth_ft:.2f} ft exceeds allowable "
            f"{allowable:.2f} ft ({governing_control} control).",
            severity="warning",
        )

    return result
