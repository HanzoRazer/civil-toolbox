"""Tests for HCFCDAuthority."""

from civil_toolbox.design_criteria.jurisdictions.hcfcd import HCFCDAuthority


def test_identity():
    a = HCFCDAuthority()
    assert a.jurisdiction_id == "hcfcd"
    assert "Harris County" in a.display_name


def test_design_storms():
    assert HCFCDAuthority().design_storms_required() == (2, 5, 10, 25, 100)


def test_default_for_design_storms():
    dv = HCFCDAuthority().default_for("project_design_storms_years")
    assert dv is not None
    assert dv.value == (2, 5, 10, 25, 100)
    assert dv.source_jurisdiction_id == "hcfcd"
    assert dv.citation


def test_default_for_freeboard():
    dv = HCFCDAuthority().default_for("project_freeboard_ft")
    assert dv is not None
    assert dv.value == 1.0
    assert dv.units == "ft"


def test_default_for_unknown_returns_none():
    assert HCFCDAuthority().default_for("project_name") is None


def test_parameters_required_includes_freeboard():
    req = HCFCDAuthority().parameters_required()
    assert "project_freeboard_ft" in req
    assert "project_design_storms_years" in req


def test_cross_jurisdiction_same_id_different_value():
    # Same parameter_id, different default value per jurisdiction (NAMESPACE §6).
    from civil_toolbox.design_criteria.jurisdictions.generic import GenericAuthority

    hcfcd = HCFCDAuthority().default_for("project_design_storms_years")
    generic = GenericAuthority().default_for("project_design_storms_years")
    assert hcfcd.parameter_id == generic.parameter_id
    assert hcfcd.value != generic.value
