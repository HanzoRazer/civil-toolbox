"""Tests for combination inlet capacity.

Benchmark (hand-computed): 24x24 grate + 5 ft curb, H = 0.5 ft, no clogging.
    grate = 13.6188 ; curb = 5.3033 ; combination = 18.9221 cfs
"""

import pytest

from civil_toolbox.inlets.combination import (
    check_combination_inlet_capacity,
    estimate_combination_inlet_capacity_cfs,
)
from civil_toolbox.inlets.errors import MissingInletDataError
from civil_toolbox.infrastructure import Inlet


def _combo(**kw):
    defaults = dict(
        id="co", name="co", inlet_type="combination",
        grate_length_in=24.0, grate_width_in=24.0, opening_length_ft=5.0,
    )
    defaults.update(kw)
    return Inlet(**defaults)


class TestCombinationCapacity:
    def test_benchmark_sum(self):
        assert estimate_combination_inlet_capacity_cfs(_combo(), 0.5) == pytest.approx(18.9221, abs=1e-3)

    def test_grate_only(self):
        # No curb opening -> grate component only
        c = _combo(opening_length_ft=None)
        assert estimate_combination_inlet_capacity_cfs(c, 0.5) == pytest.approx(13.6188, abs=1e-3)

    def test_curb_only(self):
        # No grate dims -> curb component only
        c = _combo(grate_length_in=None, grate_width_in=None)
        assert estimate_combination_inlet_capacity_cfs(c, 0.5) == pytest.approx(5.3033, abs=1e-3)

    def test_no_geometry_raises(self):
        c = _combo(grate_length_in=None, grate_width_in=None, opening_length_ft=None)
        with pytest.raises(MissingInletDataError):
            estimate_combination_inlet_capacity_cfs(c, 0.5)


class TestCombinationCheck:
    def test_pass_and_interaction_warning(self):
        r = check_combination_inlet_capacity(_combo(), design_flow_cfs=15.0, head_ft=0.5)
        assert r.status == "pass"
        assert any(w.code == "interaction_effects_not_modeled" for w in r.warnings)

    def test_fail(self):
        r = check_combination_inlet_capacity(_combo(), design_flow_cfs=25.0, head_ft=0.5)
        assert r.status == "fail"
