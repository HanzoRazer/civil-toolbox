"""Tests that the inlets package exposes its public API."""

import civil_toolbox.inlets as inlets


EXPECTED_EXPORTS = [
    "InletCapacityWarning",
    "InletCapacityResult",
    "InletCapacityError",
    "InvalidInletInputError",
    "MissingInletDataError",
    "UnsupportedInletTypeError",
    "estimate_grate_inlet_capacity_cfs",
    "check_grate_inlet_capacity",
    "estimate_curb_inlet_capacity_cfs",
    "check_curb_inlet_capacity",
    "estimate_combination_inlet_capacity_cfs",
    "check_combination_inlet_capacity",
    "estimate_slotted_inlet_capacity_cfs",
    "check_slotted_inlet_capacity",
    "analyze_inlet_capacity",
    "run_example_grate_inlet_check",
    "run_example_curb_inlet_check",
    "run_example_combination_inlet_check",
]


def test_all_declared():
    assert set(EXPECTED_EXPORTS) == set(inlets.__all__)


def test_all_importable():
    for name in EXPECTED_EXPORTS:
        assert hasattr(inlets, name), f"missing export: {name}"


def test_analyze_callable():
    assert callable(inlets.analyze_inlet_capacity)
