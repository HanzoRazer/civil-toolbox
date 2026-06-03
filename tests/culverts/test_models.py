"""Tests for culvert analysis result models."""

import pytest

from civil_toolbox.culverts.errors import (
    CulvertAnalysisError,
    InvalidCulvertInputError,
)
from civil_toolbox.culverts.models import (
    CulvertAnalysisResult,
    CulvertAnalysisWarning,
)


class TestCulvertAnalysisWarning:
    def test_create(self):
        w = CulvertAnalysisWarning(code="unsubmerged_inlet", message="HW/D < 1.2")
        assert w.code == "unsubmerged_inlet"
        assert w.severity == "warning"

    def test_custom_severity(self):
        w = CulvertAnalysisWarning(code="c", message="m", severity="error")
        assert w.severity == "error"

    def test_empty_code_fails(self):
        with pytest.raises(InvalidCulvertInputError, match="code cannot be empty"):
            CulvertAnalysisWarning(code="", message="m")

    def test_empty_message_fails(self):
        with pytest.raises(InvalidCulvertInputError, match="message cannot be empty"):
            CulvertAnalysisWarning(code="c", message="")

    def test_invalid_severity_fails(self):
        with pytest.raises(CulvertAnalysisError, match="severity must be one of"):
            CulvertAnalysisWarning(code="c", message="m", severity="fatal")

    def test_roundtrip(self):
        w = CulvertAnalysisWarning(
            code="c", message="m", severity="info", metadata={"k": 1}
        )
        assert CulvertAnalysisWarning.from_dict(w.to_dict()).to_dict() == w.to_dict()


class TestCulvertAnalysisResult:
    def test_defaults(self):
        r = CulvertAnalysisResult(culvert_id="c1", design_flow_cfs=10.0)
        assert r.culvert_id == "c1"
        assert r.governing_control == "unknown"
        assert r.inlet_control_status == "unknown"
        assert r.outlet_control_status == "unknown"
        assert r.id  # auto-generated

    def test_invalid_governing_control_fails(self):
        with pytest.raises(CulvertAnalysisError, match="governing control must be one of"):
            CulvertAnalysisResult(governing_control="sideways")

    def test_invalid_status_fails(self):
        with pytest.raises(CulvertAnalysisError, match="control status must be one of"):
            CulvertAnalysisResult(inlet_control_status="maybe")

    def test_add_warning(self):
        r = CulvertAnalysisResult()
        assert not r.has_warnings()
        w = r.add_warning("code", "message", severity="info")
        assert r.has_warnings()
        assert w in r.warnings
        assert r.warnings[0].severity == "info"

    def test_roundtrip(self):
        r = CulvertAnalysisResult(
            culvert_id="c1",
            design_flow_cfs=50.0,
            barrel_capacity_cfs=36.2,
            headwater_depth_ft=5.38,
            headwater_elevation_ft=106.38,
            inlet_control_headwater_ft=3.66,
            outlet_control_headwater_ft=5.38,
            governing_control="outlet",
            inlet_control_status="passes",
            outlet_control_status="passes",
            barrel_velocity_fps=5.1,
            assumptions=["steady flow"],
            references=["FHWA HDS-5"],
        )
        r.add_warning("w", "m")
        restored = CulvertAnalysisResult.from_dict(r.to_dict())
        assert restored.to_dict() == r.to_dict()

    def test_from_dict_minimal(self):
        r = CulvertAnalysisResult.from_dict({"culvert_id": "c2"})
        assert r.culvert_id == "c2"
        assert r.governing_control == "unknown"
