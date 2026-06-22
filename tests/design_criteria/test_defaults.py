"""Tests for the DefaultValue contract and the default_for dispatch."""

from civil_toolbox.design_criteria.defaults import DefaultValue, default_for


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


def test_applicability_notes_default_empty_and_settable():
    assert DefaultValue("project_name", "x", "generic").applicability_notes == ()
    dv = DefaultValue(
        "project_freeboard_ft", 1.0, "hcfcd",
        applicability_notes=("riverine only",),
    )
    assert dv.applicability_notes == ("riverine only",)


class TestDefaultForDispatch:
    def test_resolves_hcfcd(self):
        dv = default_for("hcfcd", "project_design_storms_years")
        assert dv is not None
        assert dv.value == (2, 5, 10, 25, 100)
        assert dv.source_jurisdiction_id == "hcfcd"

    def test_resolves_generic(self):
        dv = default_for("generic", "project_design_storms_years")
        assert dv is not None
        assert dv.value == (10, 100)

    def test_unknown_jurisdiction_returns_none(self):
        assert default_for("nope", "project_name") is None

    def test_unknown_parameter_returns_none(self):
        assert default_for("hcfcd", "project_name") is None
