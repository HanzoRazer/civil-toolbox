"""Tests for the culvert analysis orchestrator."""

import pytest

from civil_toolbox.culverts.analysis import analyze_culvert
from civil_toolbox.culverts.errors import InvalidCulvertInputError
from civil_toolbox.culverts.models import CulvertAnalysisResult
from civil_toolbox.infrastructure import Culvert


def _circular(**kw):
    defaults = dict(
        id="c1", name="bench", shape="circular", diameter_in=36.0, length_ft=100.0,
        slope_ft_per_ft=0.01, mannings_n=0.024, inlet_type="projecting",
        upstream_invert_ft=101.0, downstream_invert_ft=100.0,
        allowable_headwater_ft=6.0,
    )
    defaults.update(kw)
    return Culvert(**defaults)


class TestAnalyzeCulvertBenchmark:
    def test_returns_result(self):
        assert isinstance(analyze_culvert(_circular(), 50.0), CulvertAnalysisResult)

    def test_governing_is_outlet(self):
        r = analyze_culvert(_circular(), 50.0)
        assert r.governing_control == "outlet"
        assert r.headwater_depth_ft == pytest.approx(5.3813, abs=1e-3)

    def test_headwater_elevation(self):
        r = analyze_culvert(_circular(), 50.0)
        # 101.0 inlet invert + 5.3813
        assert r.headwater_elevation_ft == pytest.approx(106.3813, abs=1e-3)

    def test_both_controls_recorded(self):
        r = analyze_culvert(_circular(), 50.0)
        assert r.inlet_control_headwater_ft == pytest.approx(3.6582, abs=1e-3)
        assert r.outlet_control_headwater_ft == pytest.approx(5.3813, abs=1e-3)

    def test_statuses_pass(self):
        r = analyze_culvert(_circular(), 50.0)
        assert r.inlet_control_status == "passes"
        assert r.outlet_control_status == "passes"

    def test_barrel_capacity_reused(self):
        r = analyze_culvert(_circular(), 50.0)
        assert r.barrel_capacity_cfs is not None
        assert r.barrel_velocity_fps is not None

    def test_has_references_and_assumptions(self):
        r = analyze_culvert(_circular(), 50.0)
        assert len(r.references) >= 3
        assert len(r.assumptions) >= 6

    def test_roundtrip(self):
        r = analyze_culvert(_circular(), 50.0)
        assert CulvertAnalysisResult.from_dict(r.to_dict()).to_dict() == r.to_dict()


class TestAnalyzeCulvertEdgeCases:
    def test_negative_flow_raises(self):
        with pytest.raises(InvalidCulvertInputError, match="cannot be negative"):
            analyze_culvert(_circular(), -1.0)

    def test_zero_flow_not_evaluated(self):
        r = analyze_culvert(_circular(), 0.0)
        assert r.inlet_control_status == "not_evaluated"
        assert r.outlet_control_status == "not_evaluated"
        assert any(w.code == "ZERO_FLOW" for w in r.warnings)
        assert r.headwater_depth_ft is None

    def test_exceeds_allowable_warns(self):
        r = analyze_culvert(_circular(allowable_headwater_ft=4.0), 50.0)
        assert r.outlet_control_status == "exceeds"
        assert any(w.code == "HEADWATER_EXCEEDS_ALLOWABLE" for w in r.warnings)

    def test_unsubmerged_inlet_warns_at_low_flow(self):
        r = analyze_culvert(_circular(), 8.0)
        assert any(w.code == "UNSUBMERGED_INLET" for w in r.warnings)

    def test_zero_slope_barrel_capacity_unavailable_but_headwater_ok(self):
        # Zero slope breaks Manning barrel capacity, but inverts still give a
        # drop so headwater is still computed.
        r = analyze_culvert(_circular(slope_ft_per_ft=0.0), 50.0)
        assert r.barrel_capacity_cfs is None
        assert any(w.code == "BARREL_CAPACITY_UNAVAILABLE" for w in r.warnings)
        assert r.headwater_depth_ft is not None

    def test_arch_records_approximation_assumption(self):
        arch = Culvert(
            id="a", name="arch", shape="arch", width_in=48.0, height_in=36.0,
            length_ft=100.0, slope_ft_per_ft=0.01, inlet_type="headwall",
            upstream_invert_ft=101.0, downstream_invert_ft=100.0,
        )
        r = analyze_culvert(arch, 50.0)
        assert any("approximated" in a for a in r.assumptions)

    def test_no_invert_elevation_gives_none_elevation(self):
        c = _circular(upstream_invert_ft=None, downstream_invert_ft=None)
        r = analyze_culvert(c, 50.0)
        assert r.headwater_depth_ft is not None
        assert r.headwater_elevation_ft is None
