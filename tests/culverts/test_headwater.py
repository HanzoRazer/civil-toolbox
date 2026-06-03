"""Tests for culvert headwater geometry and combiner utilities."""

import math

import pytest

from civil_toolbox.culverts.errors import (
    InvalidCulvertInputError,
    UnsupportedCulvertTypeError,
)
from civil_toolbox.culverts.headwater import (
    barrel_full_area_sqft,
    barrel_full_hydraulic_radius_ft,
    barrel_rise_ft,
    estimate_headwater_depth_ft,
    estimate_headwater_elevation_ft,
)
from civil_toolbox.infrastructure import Culvert


def _circular(diameter_in=36.0):
    return Culvert(
        id="c", name="c", shape="circular", diameter_in=diameter_in,
        length_ft=100.0, slope_ft_per_ft=0.01,
    )


def _box(width_in=48.0, height_in=36.0):
    return Culvert(
        id="b", name="b", shape="box", width_in=width_in, height_in=height_in,
        length_ft=100.0, slope_ft_per_ft=0.01,
    )


class TestBarrelGeometry:
    def test_circular_rise(self):
        assert barrel_rise_ft(_circular()) == pytest.approx(3.0)

    def test_circular_area(self):
        assert barrel_full_area_sqft(_circular()) == pytest.approx(math.pi * 1.5**2)

    def test_circular_hydraulic_radius(self):
        # Full circular pipe: R = D/4
        assert barrel_full_hydraulic_radius_ft(_circular()) == pytest.approx(0.75)

    def test_box_rise(self):
        assert barrel_rise_ft(_box()) == pytest.approx(3.0)

    def test_box_area(self):
        # 4 ft x 3 ft = 12 sqft
        assert barrel_full_area_sqft(_box()) == pytest.approx(12.0)

    def test_box_hydraulic_radius(self):
        # R = A/P = 12 / (2*(4+3)) = 0.857...
        assert barrel_full_hydraulic_radius_ft(_box()) == pytest.approx(12.0 / 14.0)

    def test_arch_uses_box_approximation(self):
        arch = Culvert(
            id="a", name="a", shape="arch", width_in=48.0, height_in=36.0,
            length_ft=100.0, slope_ft_per_ft=0.01,
        )
        assert barrel_full_area_sqft(arch) == pytest.approx(12.0)


class TestGeometryErrors:
    def test_unsupported_shape_raises(self):
        # "elliptical" is box-approximated and supported; force an unknown via attr.
        c = _circular()
        c.shape = "triangular"
        with pytest.raises(UnsupportedCulvertTypeError):
            barrel_rise_ft(c)

    def test_missing_dimension_raises(self):
        c = _circular()
        c.diameter_in = None
        with pytest.raises(InvalidCulvertInputError):
            barrel_full_area_sqft(c)


class TestEstimateHeadwaterDepth:
    def test_outlet_governs(self):
        depth, control = estimate_headwater_depth_ft(3.0, 5.0)
        assert depth == 5.0
        assert control == "outlet"

    def test_inlet_governs(self):
        depth, control = estimate_headwater_depth_ft(6.0, 4.0)
        assert depth == 6.0
        assert control == "inlet"

    def test_tie_defaults_to_inlet(self):
        depth, control = estimate_headwater_depth_ft(4.0, 4.0)
        assert depth == 4.0
        assert control == "inlet"


class TestEstimateHeadwaterElevation:
    def test_with_invert(self):
        assert estimate_headwater_elevation_ft(5.0, 100.0) == pytest.approx(105.0)

    def test_without_invert_returns_none(self):
        assert estimate_headwater_elevation_ft(5.0, None) is None
