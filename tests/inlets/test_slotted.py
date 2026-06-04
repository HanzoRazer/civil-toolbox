"""Tests for slotted inlet capacity (the model's real 4th inlet type, in place
of the handoff's non-existent "drop" type).

Benchmark (hand-computed): 10 ft slot, H = 0.4 ft, Cw = 3.0, no clogging.
    Q = 3.0 * 10.0 * 0.4^1.5 = 30 * 0.252982 = 7.5895 cfs
"""

import pytest

from civil_toolbox.inlets.errors import InvalidInletInputError, MissingInletDataError
from civil_toolbox.inlets.slotted import (
    check_slotted_inlet_capacity,
    estimate_slotted_inlet_capacity_cfs,
)
from civil_toolbox.infrastructure import Inlet


def _slotted(**kw):
    defaults = dict(id="s", name="s", inlet_type="slotted", opening_length_ft=10.0)
    defaults.update(kw)
    return Inlet(**defaults)


class TestSlottedCapacity:
    def test_benchmark(self):
        assert estimate_slotted_inlet_capacity_cfs(_slotted(), 0.4) == pytest.approx(7.5895, abs=1e-3)

    def test_missing_length_raises(self):
        with pytest.raises(MissingInletDataError):
            estimate_slotted_inlet_capacity_cfs(_slotted(opening_length_ft=None), 0.4)

    def test_head_must_be_positive(self):
        with pytest.raises(InvalidInletInputError, match="must be positive"):
            estimate_slotted_inlet_capacity_cfs(_slotted(), 0.0)


class TestSlottedCheck:
    def test_pass_and_warnings(self):
        r = check_slotted_inlet_capacity(_slotted(), design_flow_cfs=5.0, head_ft=0.4)
        assert r.status == "pass"
        assert any(w.code == "slotted_inlet_simplified" for w in r.warnings)

    def test_fail(self):
        r = check_slotted_inlet_capacity(_slotted(), design_flow_cfs=10.0, head_ft=0.4)
        assert r.status == "fail"
