"""Synthetic inlet capacity examples for demonstration and testing.

These build a synthetic ``Inlet`` and run a capacity check, returning the
:class:`InletCapacityResult`. They carry demo metadata and make no official
design claims.
"""

from __future__ import annotations

from civil_toolbox.inlets.analysis import analyze_inlet_capacity
from civil_toolbox.inlets.models import InletCapacityResult
from civil_toolbox.infrastructure import Inlet

_DEMO_METADATA = {"synthetic": True, "note": "Demonstration only; not a design."}


def _as_demo(result: InletCapacityResult) -> InletCapacityResult:
    """Stamp demo metadata on a result so examples are clearly non-design."""
    result.metadata.update(_DEMO_METADATA)
    return result


def run_example_grate_inlet_check() -> InletCapacityResult:
    """Grate inlet (24 in x 24 in) capturing 8 cfs at 0.5 ft head."""
    inlet = Inlet(
        id="inlet_grate_001",
        name="Example Grate Inlet",
        inlet_type="grate",
        grate_length_in=24.0,
        grate_width_in=24.0,
    )
    return _as_demo(analyze_inlet_capacity(inlet, design_flow_cfs=8.0, head_ft=0.5))


def run_example_curb_inlet_check() -> InletCapacityResult:
    """Curb-opening inlet (5 ft opening) capturing 4 cfs at 0.5 ft head."""
    inlet = Inlet(
        id="inlet_curb_001",
        name="Example Curb Inlet",
        inlet_type="curb_opening",
        opening_length_ft=5.0,
        opening_height_in=6.0,
    )
    return _as_demo(analyze_inlet_capacity(inlet, design_flow_cfs=4.0, head_ft=0.5))


def run_example_combination_inlet_check() -> InletCapacityResult:
    """Combination inlet (grate + 5 ft curb) capturing 15 cfs at 0.5 ft head."""
    inlet = Inlet(
        id="inlet_combo_001",
        name="Example Combination Inlet",
        inlet_type="combination",
        grate_length_in=24.0,
        grate_width_in=24.0,
        opening_length_ft=5.0,
        opening_height_in=6.0,
    )
    return _as_demo(analyze_inlet_capacity(inlet, design_flow_cfs=15.0, head_ft=0.5))
