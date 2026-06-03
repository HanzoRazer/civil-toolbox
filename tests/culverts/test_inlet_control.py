"""Tests for inlet-control headwater estimation.

Benchmark (hand-computed): 36-in circular barrel, Q = 50 cfs, Cd = 0.6.
    A = pi * 1.5^2 = 7.06858 sqft
    HW = (Q / (Cd*A))^2 / (2g) + D/2
       = (50 / (0.6*7.06858))^2 / 64.4 + 1.5
       = 3.6582 ft   (HW/D = 1.219 -> submerged)
"""

import pytest

from civil_toolbox.culverts.inlet_control import (
    DEFAULT_ORIFICE_DISCHARGE_COEFFICIENT,
    evaluate_inlet_control_status,
    inlet_control_headwater_depth_ft,
    is_inlet_submerged,
)
from civil_toolbox.culverts.errors import InvalidCulvertInputError
from civil_toolbox.infrastructure import Culvert


def _circular(diameter_in=36.0):
    return Culvert(
        id="c", name="c", shape="circular", diameter_in=diameter_in,
        length_ft=100.0, slope_ft_per_ft=0.01,
    )


class TestInletControlHeadwater:
    def test_benchmark_submerged(self):
        hw = inlet_control_headwater_depth_ft(_circular(), 50.0)
        assert hw == pytest.approx(3.6582, abs=1e-3)

    def test_increases_with_flow(self):
        low = inlet_control_headwater_depth_ft(_circular(), 20.0)
        high = inlet_control_headwater_depth_ft(_circular(), 60.0)
        assert high > low

    def test_default_coefficient(self):
        assert DEFAULT_ORIFICE_DISCHARGE_COEFFICIENT == pytest.approx(0.6)

    def test_zero_flow_rejected(self):
        with pytest.raises(InvalidCulvertInputError, match="must be positive"):
            inlet_control_headwater_depth_ft(_circular(), 0.0)


class TestSubmergence:
    def test_submerged_true(self):
        # benchmark HW/D = 1.219 >= 1.2
        assert is_inlet_submerged(3.6582, 3.0) is True

    def test_unsubmerged_low_flow(self):
        hw = inlet_control_headwater_depth_ft(_circular(), 10.0)
        assert is_inlet_submerged(hw, 3.0) is False

    def test_zero_rise_not_submerged(self):
        assert is_inlet_submerged(5.0, 0.0) is False


class TestInletControlStatus:
    def test_passes(self):
        assert evaluate_inlet_control_status(3.0, 6.0) == "passes"

    def test_exceeds(self):
        assert evaluate_inlet_control_status(7.0, 6.0) == "exceeds"

    def test_not_evaluated_without_allowable(self):
        assert evaluate_inlet_control_status(3.0, None) == "not_evaluated"
