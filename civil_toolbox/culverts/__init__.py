"""Culvert analysis module for Civil Toolbox.

First-pass culvert hydraulic analysis: given a ``Culvert`` and a design flow,
estimate the controlling headwater by comparing a simplified inlet-control
(submerged orifice) headwater against a simplified outlet-control (full-flow
energy) headwater, reusing the barrel-capacity screening from the infrastructure
sizing layer.

This foundation supports:
- Full-barrel Manning capacity (reused from infrastructure sizing)
- Inlet-control headwater (submerged orifice approximation)
- Outlet-control headwater (full-flow energy equation)
- Governing headwater (the larger of inlet/outlet control) and elevation
- Per-control status vs. allowable headwater
- Warnings and assumptions on an auditable result

Limitations (this is screening-level, not final design):
- No FHWA HDS-5 chart-specific inlet coefficients
- No tailwater rating curves / tailwater profiles (assumed at crown)
- No multiple-barrel interaction
- No road overtopping, sediment, debris, or fish passage
- Use FHWA HY-8 or HEC-RAS for detailed design

Example:
    >>> from civil_toolbox.culverts import analyze_culvert
    >>> from civil_toolbox.culverts.examples import create_single_circular_culvert
    >>> culvert = create_single_circular_culvert()
    >>> result = analyze_culvert(culvert, design_flow_cfs=50.0)
    >>> result.governing_control in ("inlet", "outlet")
    True
"""

from civil_toolbox.culverts.analysis import analyze_culvert
from civil_toolbox.culverts.errors import (
    CulvertAnalysisError,
    InvalidCulvertInputError,
    UnsupportedCulvertTypeError,
)
from civil_toolbox.culverts.headwater import (
    barrel_full_area_sqft,
    barrel_full_hydraulic_radius_ft,
    barrel_rise_ft,
    estimate_headwater_depth_ft,
    estimate_headwater_elevation_ft,
)
from civil_toolbox.culverts.inlet_control import (
    evaluate_inlet_control_status,
    inlet_control_headwater_depth_ft,
    is_inlet_submerged,
)
from civil_toolbox.culverts.models import (
    CulvertAnalysisResult,
    CulvertAnalysisWarning,
)
from civil_toolbox.culverts.outlet_control import (
    entrance_loss_coefficient,
    evaluate_outlet_control_status,
    outlet_control_headwater_depth_ft,
)

__all__ = [
    # Orchestrator
    "analyze_culvert",
    # Models
    "CulvertAnalysisResult",
    "CulvertAnalysisWarning",
    # Errors
    "CulvertAnalysisError",
    "InvalidCulvertInputError",
    "UnsupportedCulvertTypeError",
    # Headwater / geometry
    "barrel_rise_ft",
    "barrel_full_area_sqft",
    "barrel_full_hydraulic_radius_ft",
    "estimate_headwater_depth_ft",
    "estimate_headwater_elevation_ft",
    # Inlet control
    "inlet_control_headwater_depth_ft",
    "evaluate_inlet_control_status",
    "is_inlet_submerged",
    # Outlet control
    "outlet_control_headwater_depth_ft",
    "evaluate_outlet_control_status",
    "entrance_loss_coefficient",
]
