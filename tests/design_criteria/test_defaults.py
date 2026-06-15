"""Tests for the DefaultValue contract."""

from civil_toolbox.design_criteria.defaults import DefaultValue


def test_default_value_fields():
    dv = DefaultValue(
        parameter_id="project_freeboard_ft",
        value=1.0,
        source_jurisdiction_id="hcfcd",
        units="ft",
        citation="HCFCD manual",
    )
    assert dv.parameter_id == "project_freeboard_ft"
    assert dv.value == 1.0
    assert dv.source_jurisdiction_id == "hcfcd"
    assert dv.units == "ft"


def test_default_value_is_frozen():
    dv = DefaultValue("project_name", "x", "generic")
    import dataclasses
    import pytest

    with pytest.raises(dataclasses.FrozenInstanceError):
        dv.value = "y"  # type: ignore[misc]
