"""Tests for synthetic inlet capacity examples."""

import pytest

from civil_toolbox.inlets.examples import (
    run_example_combination_inlet_check,
    run_example_curb_inlet_check,
    run_example_grate_inlet_check,
)
from civil_toolbox.inlets.models import InletCapacityResult


@pytest.mark.parametrize(
    "factory",
    [
        run_example_grate_inlet_check,
        run_example_curb_inlet_check,
        run_example_combination_inlet_check,
    ],
)
def test_example_returns_result(factory):
    result = factory()
    assert isinstance(result, InletCapacityResult)
    assert result.status in ("pass", "fail", "warning", "not_evaluated")
    assert result.metadata.get("synthetic") is True


def test_grate_example_passes():
    assert run_example_grate_inlet_check().status == "pass"


def test_combination_example_passes():
    assert run_example_combination_inlet_check().status == "pass"
