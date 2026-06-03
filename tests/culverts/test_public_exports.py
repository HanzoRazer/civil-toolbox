"""Tests that the culverts package exposes its public API."""

import civil_toolbox.culverts as culverts


EXPECTED_EXPORTS = [
    "analyze_culvert",
    "CulvertAnalysisResult",
    "CulvertAnalysisWarning",
    "CulvertAnalysisError",
    "InvalidCulvertInputError",
    "UnsupportedCulvertTypeError",
    "barrel_rise_ft",
    "barrel_full_area_sqft",
    "barrel_full_hydraulic_radius_ft",
    "estimate_headwater_depth_ft",
    "estimate_headwater_elevation_ft",
    "inlet_control_headwater_depth_ft",
    "evaluate_inlet_control_status",
    "is_inlet_submerged",
    "outlet_control_headwater_depth_ft",
    "evaluate_outlet_control_status",
    "entrance_loss_coefficient",
]


def test_all_declared():
    assert set(EXPECTED_EXPORTS) == set(culverts.__all__)


def test_all_importable():
    for name in EXPECTED_EXPORTS:
        assert hasattr(culverts, name), f"missing export: {name}"


def test_analyze_culvert_callable():
    assert callable(culverts.analyze_culvert)
