"""Tests for outlet-control headwater estimation.

Benchmark (hand-computed): 36-in circular barrel, Q = 50 cfs, L = 100 ft,
n = 0.024, inverts 101/100 (drop 1.0 ft), projecting inlet (Ke = 0.9),
tailwater unknown (ho = D = 3.0).
    A = 7.06858 sqft, R = 0.75 ft
    V = 50 / 7.06858 = 7.0735 fps ; V^2/2g = 0.7769 ft
    Sf = (n*V / (1.49*R^(2/3)))^2 = 0.019050 ; hf = Sf*L = 1.9050 ft
    H_L = (0.9 + 1.0)*0.7769 + 1.9050 = 3.3811 ft
    HW = ho + H_L - drop = 3.0 + 3.3811 - 1.0 = 5.3813 ft
"""

import pytest

from civil_toolbox.culverts.outlet_control import (
    DEFAULT_ENTRANCE_LOSS_COEFFICIENT,
    ENTRANCE_LOSS_COEFFICIENTS,
    entrance_loss_coefficient,
    evaluate_outlet_control_status,
    invert_drop_ft,
    outlet_control_headwater_depth_ft,
)
from civil_toolbox.culverts.errors import InvalidCulvertInputError
from civil_toolbox.infrastructure import Culvert


def _circular(**kw):
    defaults = dict(
        id="c", name="c", shape="circular", diameter_in=36.0, length_ft=100.0,
        slope_ft_per_ft=0.01, mannings_n=0.024, inlet_type="projecting",
        upstream_invert_ft=101.0, downstream_invert_ft=100.0,
    )
    defaults.update(kw)
    return Culvert(**defaults)


class TestOutletControlHeadwater:
    def test_benchmark(self):
        hw = outlet_control_headwater_depth_ft(_circular(), 50.0)
        assert hw == pytest.approx(5.3813, abs=1e-3)

    def test_higher_tailwater_raises_headwater(self):
        base = outlet_control_headwater_depth_ft(_circular(), 50.0)
        high_tw = outlet_control_headwater_depth_ft(_circular(), 50.0, tailwater_depth_ft=5.0)
        assert high_tw > base

    def test_zero_flow_rejected(self):
        with pytest.raises(InvalidCulvertInputError, match="must be positive"):
            outlet_control_headwater_depth_ft(_circular(), 0.0)


class TestEntranceLossCoefficient:
    def test_projecting(self):
        assert entrance_loss_coefficient(_circular(inlet_type="projecting")) == 0.9

    def test_headwall(self):
        assert entrance_loss_coefficient(_circular(inlet_type="headwall")) == 0.5

    def test_beveled(self):
        assert entrance_loss_coefficient(_circular(inlet_type="beveled")) == 0.2

    def test_explicit_override(self):
        assert entrance_loss_coefficient(_circular(inlet_coefficient=0.35)) == 0.35

    def test_table_and_default_present(self):
        assert ENTRANCE_LOSS_COEFFICIENTS["mitered"] == 0.7
        assert DEFAULT_ENTRANCE_LOSS_COEFFICIENT == 0.5


class TestInvertDrop:
    def test_from_inverts(self):
        assert invert_drop_ft(_circular()) == pytest.approx(1.0)

    def test_from_slope_when_inverts_missing(self):
        c = _circular(upstream_invert_ft=None, downstream_invert_ft=None)
        # slope 0.01 * length 100 = 1.0
        assert invert_drop_ft(c) == pytest.approx(1.0)


class TestOutletControlStatus:
    def test_passes(self):
        assert evaluate_outlet_control_status(4.0, 6.0) == "passes"

    def test_exceeds(self):
        assert evaluate_outlet_control_status(7.0, 6.0) == "exceeds"

    def test_not_evaluated_without_allowable(self):
        assert evaluate_outlet_control_status(4.0, None) == "not_evaluated"
