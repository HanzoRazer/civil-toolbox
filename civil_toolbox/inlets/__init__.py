"""Inlet capacity module for Civil Toolbox.

First-pass inlet capture and capacity analysis: given an ``Inlet``, a design
flow, and a head, estimate the interception capacity, captured flow, bypass
flow, and capture efficiency using simplified, benchmark-tested equations.

Supported inlet types (matching the domain ``Inlet`` model):
- grate         — submerged orifice on gross opening area
- curb_opening  — weir on the opening length
- combination   — grate + curb components, summed
- slotted       — equivalent curb-opening weir

This foundation supports:
- Per-type capacity estimation (orifice / weir first-pass equations)
- Capture / bypass flow and capture efficiency
- Pass/fail status vs. the supplied design flow
- Clogging applied via the inlet's effective_clogging_factor
- Warnings and assumptions on an auditable result

Limitations (screening-level, not final design):
- Not the full FHWA HEC-22 procedure (no gutter spread / cross-slope)
- No sag vs. grade inlet distinction beyond metadata
- No HGL integration or dynamic routing
- Design flow is explicit (runoff is not derived here)

Example:
    >>> from civil_toolbox.inlets import analyze_inlet_capacity
    >>> from civil_toolbox.inlets.examples import run_example_grate_inlet_check
    >>> result = run_example_grate_inlet_check()
    >>> result.status in ("pass", "fail", "warning", "not_evaluated")
    True
"""

from civil_toolbox.inlets.analysis import analyze_inlet_capacity
from civil_toolbox.inlets.combination import (
    check_combination_inlet_capacity,
    estimate_combination_inlet_capacity_cfs,
)
from civil_toolbox.inlets.curb import (
    check_curb_inlet_capacity,
    estimate_curb_inlet_capacity_cfs,
)
from civil_toolbox.inlets.errors import (
    InletCapacityError,
    InvalidInletInputError,
    MissingInletDataError,
    UnsupportedInletTypeError,
)
from civil_toolbox.inlets.examples import (
    run_example_combination_inlet_check,
    run_example_curb_inlet_check,
    run_example_grate_inlet_check,
)
from civil_toolbox.inlets.grate import (
    check_grate_inlet_capacity,
    estimate_grate_inlet_capacity_cfs,
)
from civil_toolbox.inlets.models import (
    InletCapacityResult,
    InletCapacityWarning,
)
from civil_toolbox.inlets.slotted import (
    check_slotted_inlet_capacity,
    estimate_slotted_inlet_capacity_cfs,
)

__all__ = [
    # Models
    "InletCapacityWarning",
    "InletCapacityResult",
    # Errors
    "InletCapacityError",
    "InvalidInletInputError",
    "MissingInletDataError",
    "UnsupportedInletTypeError",
    # Grate
    "estimate_grate_inlet_capacity_cfs",
    "check_grate_inlet_capacity",
    # Curb
    "estimate_curb_inlet_capacity_cfs",
    "check_curb_inlet_capacity",
    # Combination
    "estimate_combination_inlet_capacity_cfs",
    "check_combination_inlet_capacity",
    # Slotted
    "estimate_slotted_inlet_capacity_cfs",
    "check_slotted_inlet_capacity",
    # Orchestrator
    "analyze_inlet_capacity",
    # Examples
    "run_example_grate_inlet_check",
    "run_example_curb_inlet_check",
    "run_example_combination_inlet_check",
]
