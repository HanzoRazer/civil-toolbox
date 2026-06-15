"""Tests for GenericAuthority."""

from civil_toolbox.design_criteria.jurisdictions.generic import GenericAuthority


def test_identity():
    a = GenericAuthority()
    assert a.jurisdiction_id == "generic"
    assert a.display_name


def test_design_storms():
    assert GenericAuthority().design_storms_required() == (10, 100)


def test_default_for_design_storms():
    dv = GenericAuthority().default_for("project_design_storms_years")
    assert dv is not None
    assert dv.value == (10, 100)
    assert dv.source_jurisdiction_id == "generic"


def test_default_for_unknown_returns_none():
    assert GenericAuthority().default_for("project_freeboard_ft") is None
    assert GenericAuthority().default_for("project_name") is None


def test_parameters_required():
    req = GenericAuthority().parameters_required()
    assert "project_name" in req
    assert "project_jurisdiction_id" in req
    assert "project_design_storms_years" in req
    # Generic does not require freeboard.
    assert "project_freeboard_ft" not in req


def test_default_parameter_ids():
    assert GenericAuthority().default_parameter_ids() == ("project_design_storms_years",)
