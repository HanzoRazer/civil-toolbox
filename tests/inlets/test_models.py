"""Tests for inlet capacity result models."""

import pytest

from civil_toolbox.inlets.errors import InletCapacityError, InvalidInletInputError
from civil_toolbox.inlets.models import (
    InletCapacityResult,
    InletCapacityWarning,
    apply_capture_outcome,
)


class TestInletCapacityWarning:
    def test_create(self):
        w = InletCapacityWarning(code="simplified_orifice_assumption", message="m")
        assert w.severity == "warning"

    def test_empty_code_fails(self):
        with pytest.raises(InvalidInletInputError, match="code cannot be empty"):
            InletCapacityWarning(code="", message="m")

    def test_empty_message_fails(self):
        with pytest.raises(InvalidInletInputError, match="message cannot be empty"):
            InletCapacityWarning(code="c", message="")

    def test_invalid_severity_fails(self):
        with pytest.raises(InvalidInletInputError, match="severity must be one of"):
            InletCapacityWarning(code="c", message="m", severity="critical")

    def test_roundtrip(self):
        w = InletCapacityWarning(code="c", message="m", severity="info", metadata={"k": 1})
        assert InletCapacityWarning.from_dict(w.to_dict()).to_dict() == w.to_dict()


class TestInletCapacityResult:
    def test_defaults(self):
        r = InletCapacityResult(inlet_id="i1")
        assert r.status == "not_evaluated"
        assert r.id

    def test_invalid_status_fails(self):
        with pytest.raises(InletCapacityError, match="status must be one of"):
            InletCapacityResult(status="passes")

    def test_add_warning(self):
        r = InletCapacityResult()
        assert not r.has_warnings()
        r.add_warning("c", "m")
        assert r.has_warnings()

    def test_roundtrip(self):
        r = InletCapacityResult(
            inlet_id="i1",
            inlet_type="grate",
            design_flow_cfs=8.0,
            captured_flow_cfs=8.0,
            bypass_flow_cfs=0.0,
            capture_efficiency=1.0,
            capacity_cfs=13.6,
            status="pass",
            assumptions=["gross area"],
            references=["HEC-22"],
        )
        r.add_warning("c", "m")
        assert InletCapacityResult.from_dict(r.to_dict()).to_dict() == r.to_dict()


class TestApplyCaptureOutcome:
    def test_pass_when_capacity_exceeds_design(self):
        r = apply_capture_outcome(InletCapacityResult(), capacity_cfs=13.6, design_flow_cfs=8.0)
        assert r.status == "pass"
        assert r.captured_flow_cfs == 8.0
        assert r.bypass_flow_cfs == 0.0
        assert r.capture_efficiency == pytest.approx(1.0)

    def test_fail_when_capacity_below_design(self):
        r = apply_capture_outcome(InletCapacityResult(), capacity_cfs=5.0, design_flow_cfs=8.0)
        assert r.status == "fail"
        assert r.captured_flow_cfs == 5.0
        assert r.bypass_flow_cfs == pytest.approx(3.0)
        assert r.capture_efficiency == pytest.approx(5.0 / 8.0)

    def test_zero_design_efficiency_none(self):
        r = apply_capture_outcome(InletCapacityResult(), capacity_cfs=5.0, design_flow_cfs=0.0)
        assert r.capture_efficiency is None
        assert r.bypass_flow_cfs == 0.0
