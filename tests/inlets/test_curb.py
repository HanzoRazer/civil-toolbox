"""Tests for curb-opening inlet capacity.

Benchmark (hand-computed): 5 ft opening, H = 0.5 ft, Cw = 3.0, no clogging.
    Q = 3.0 * 5.0 * 0.5^1.5 = 15 * 0.353553 = 5.3033 cfs
"""

import pytest

from civil_toolbox.inlets.curb import (
    check_curb_inlet_capacity,
    estimate_curb_inlet_capacity_cfs,
)
from civil_toolbox.inlets.errors import InvalidInletInputError, MissingInletDataError
from civil_toolbox.infrastructure import Inlet


def _curb(**kw):
    defaults = dict(id="c", name="c", inlet_type="curb_opening", opening_length_ft=5.0)
    defaults.update(kw)
    return Inlet(**defaults)


class TestCurbCapacity:
    def test_benchmark(self):
        assert estimate_curb_inlet_capacity_cfs(_curb(), 0.5) == pytest.approx(5.3033, abs=1e-3)

    def test_missing_opening_length_raises(self):
        with pytest.raises(MissingInletDataError):
            estimate_curb_inlet_capacity_cfs(_curb(opening_length_ft=None), 0.5)

    def test_head_must_be_positive(self):
        with pytest.raises(InvalidInletInputError, match="must be positive"):
            estimate_curb_inlet_capacity_cfs(_curb(), 0.0)

    def test_clogging_applied(self):
        # effective 0.5 -> half capacity
        assert estimate_curb_inlet_capacity_cfs(_curb(clogging_factor=0.5), 0.5) == pytest.approx(5.3033 / 2, abs=1e-3)


class TestCurbCheck:
    def test_pass(self):
        r = check_curb_inlet_capacity(_curb(), design_flow_cfs=4.0, head_ft=0.5)
        assert r.status == "pass"
        assert any(w.code == "simplified_weir_assumption" for w in r.warnings)
        assert any(w.code == "roadway_spread_not_modeled" for w in r.warnings)

    def test_fail(self):
        r = check_curb_inlet_capacity(_curb(), design_flow_cfs=8.0, head_ft=0.5)
        assert r.status == "fail"
        assert r.bypass_flow_cfs == pytest.approx(8.0 - 5.3033, abs=1e-3)
