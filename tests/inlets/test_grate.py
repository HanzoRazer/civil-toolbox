"""Tests for grate inlet capacity.

Benchmark (hand-computed): 24 in x 24 in grate, H = 0.5 ft, C = 0.6, no clogging.
    A = 24*24/144 = 4.0 sqft
    Q = 0.6 * 4.0 * sqrt(2*32.2*0.5) = 2.4 * sqrt(32.2) = 13.6188 cfs
With clogging_factor = 0.25 (effective 0.75): 13.6188 * 0.75 = 10.2141 cfs
"""

import pytest

from civil_toolbox.inlets.errors import InvalidInletInputError, MissingInletDataError
from civil_toolbox.inlets.grate import (
    check_grate_inlet_capacity,
    estimate_grate_inlet_capacity_cfs,
    grate_gross_area_sqft,
)
from civil_toolbox.infrastructure import Inlet


def _grate(**kw):
    defaults = dict(
        id="g", name="g", inlet_type="grate",
        grate_length_in=24.0, grate_width_in=24.0,
    )
    defaults.update(kw)
    return Inlet(**defaults)


class TestGrateGeometry:
    def test_gross_area(self):
        assert grate_gross_area_sqft(_grate()) == pytest.approx(4.0)

    def test_missing_dims_raises(self):
        with pytest.raises(MissingInletDataError):
            grate_gross_area_sqft(_grate(grate_width_in=None))


class TestGrateCapacity:
    def test_benchmark(self):
        assert estimate_grate_inlet_capacity_cfs(_grate(), 0.5) == pytest.approx(13.6188, abs=1e-3)

    def test_clogging_applied(self):
        assert estimate_grate_inlet_capacity_cfs(_grate(clogging_factor=0.25), 0.5) == pytest.approx(10.2141, abs=1e-3)

    def test_head_must_be_positive(self):
        with pytest.raises(InvalidInletInputError, match="must be positive"):
            estimate_grate_inlet_capacity_cfs(_grate(), 0.0)


class TestGrateCheck:
    def test_pass(self):
        r = check_grate_inlet_capacity(_grate(), design_flow_cfs=8.0, head_ft=0.5)
        assert r.status == "pass"
        assert r.capacity_cfs == pytest.approx(13.6188, abs=1e-3)
        assert any(w.code == "simplified_orifice_assumption" for w in r.warnings)

    def test_fail_and_bypass(self):
        r = check_grate_inlet_capacity(_grate(), design_flow_cfs=20.0, head_ft=0.5)
        assert r.status == "fail"
        assert r.bypass_flow_cfs == pytest.approx(20.0 - 13.6188, abs=1e-3)

    def test_clogging_warning(self):
        r = check_grate_inlet_capacity(_grate(clogging_factor=0.25), design_flow_cfs=5.0, head_ft=0.5)
        assert any(w.code == "capacity_reduced_by_clogging_factor" for w in r.warnings)

    def test_no_clogging_warning_when_clean(self):
        r = check_grate_inlet_capacity(_grate(), design_flow_cfs=5.0, head_ft=0.5)
        assert not any(w.code == "capacity_reduced_by_clogging_factor" for w in r.warnings)
