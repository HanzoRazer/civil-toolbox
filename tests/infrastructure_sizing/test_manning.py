"""Tests for Manning's equation functions."""

import math
import pytest

from civil_toolbox.infrastructure_sizing import (
    manning_capacity_cfs,
    manning_velocity_fps,
    circular_pipe_full_flow_area_sqft,
    circular_pipe_full_flow_hydraulic_radius_ft,
    box_full_flow_area_sqft,
    box_full_flow_hydraulic_radius_ft,
    rectangular_area_sqft,
    rectangular_wetted_perimeter_ft,
    rectangular_hydraulic_radius_ft,
    trapezoidal_area_sqft,
    trapezoidal_wetted_perimeter_ft,
    trapezoidal_hydraulic_radius_ft,
    triangular_area_sqft,
    triangular_wetted_perimeter_ft,
    triangular_hydraulic_radius_ft,
)
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


class TestManningCapacity:
    """Tests for manning_capacity_cfs."""

    def test_basic_calculation(self):
        """Basic Manning capacity calculation."""
        area = 1.0
        hydraulic_radius = 0.25
        slope = 0.01
        n = 0.013

        q = manning_capacity_cfs(area, hydraulic_radius, slope, n)
        expected = (1.49 / n) * area * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
        assert q == pytest.approx(expected)

    def test_zero_slope_returns_zero(self):
        """Zero slope returns zero capacity."""
        q = manning_capacity_cfs(1.0, 0.25, 0.0, 0.013)
        assert q == 0.0

    def test_negative_area_raises(self):
        """Negative area raises error."""
        with pytest.raises(InvalidSizingInputError, match="area_sqft"):
            manning_capacity_cfs(-1.0, 0.25, 0.01, 0.013)

    def test_negative_slope_raises(self):
        """Negative slope raises error."""
        with pytest.raises(InvalidSizingInputError, match="slope"):
            manning_capacity_cfs(1.0, 0.25, -0.01, 0.013)

    def test_zero_mannings_n_raises(self):
        """Zero Manning's n raises error."""
        with pytest.raises(InvalidSizingInputError, match="mannings_n"):
            manning_capacity_cfs(1.0, 0.25, 0.01, 0.0)


class TestManningVelocity:
    """Tests for manning_velocity_fps."""

    def test_basic_calculation(self):
        """Basic Manning velocity calculation."""
        hydraulic_radius = 0.5
        slope = 0.01
        n = 0.013

        v = manning_velocity_fps(hydraulic_radius, slope, n)
        expected = (1.49 / n) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
        assert v == pytest.approx(expected)

    def test_zero_slope_returns_zero(self):
        """Zero slope returns zero velocity."""
        v = manning_velocity_fps(0.5, 0.0, 0.013)
        assert v == 0.0


class TestCircularPipeGeometry:
    """Tests for circular pipe geometry functions."""

    def test_area_1ft_diameter(self):
        """Area of 1 ft diameter pipe."""
        area = circular_pipe_full_flow_area_sqft(1.0)
        assert area == pytest.approx(math.pi * 0.25)

    def test_hydraulic_radius_1ft_diameter(self):
        """Hydraulic radius of 1 ft diameter pipe is D/4."""
        r = circular_pipe_full_flow_hydraulic_radius_ft(1.0)
        assert r == pytest.approx(0.25)

    def test_negative_diameter_raises(self):
        """Negative diameter raises error."""
        with pytest.raises(InvalidSizingInputError):
            circular_pipe_full_flow_area_sqft(-1.0)


class TestBoxGeometry:
    """Tests for box section geometry functions."""

    def test_area_4x3(self):
        """Area of 4x3 box is 12 sq ft."""
        area = box_full_flow_area_sqft(4.0, 3.0)
        assert area == pytest.approx(12.0)

    def test_hydraulic_radius_4x3(self):
        """Hydraulic radius of 4x3 box."""
        r = box_full_flow_hydraulic_radius_ft(4.0, 3.0)
        expected = 12.0 / 14.0
        assert r == pytest.approx(expected)


class TestRectangularGeometry:
    """Tests for rectangular channel geometry."""

    def test_area_6x3(self):
        """Area of 6 ft wide, 3 ft deep channel."""
        area = rectangular_area_sqft(6.0, 3.0)
        assert area == pytest.approx(18.0)

    def test_wetted_perimeter_6x3(self):
        """Wetted perimeter of 6 ft wide, 3 ft deep channel."""
        p = rectangular_wetted_perimeter_ft(6.0, 3.0)
        assert p == pytest.approx(12.0)

    def test_hydraulic_radius_6x3(self):
        """Hydraulic radius of 6 ft wide, 3 ft deep channel."""
        r = rectangular_hydraulic_radius_ft(6.0, 3.0)
        assert r == pytest.approx(18.0 / 12.0)


class TestTrapezoidalGeometry:
    """Tests for trapezoidal channel geometry."""

    def test_area_6x3_ss2(self):
        """Area of 6 ft bottom, 3 ft deep, 2:1 side slope."""
        area = trapezoidal_area_sqft(6.0, 3.0, 2.0)
        expected = (6.0 + 2.0 * 3.0) * 3.0
        assert area == pytest.approx(expected)

    def test_wetted_perimeter_6x3_ss2(self):
        """Wetted perimeter of 6 ft bottom, 3 ft deep, 2:1 side slope."""
        p = trapezoidal_wetted_perimeter_ft(6.0, 3.0, 2.0)
        side_length = 3.0 * math.sqrt(1 + 4)
        expected = 6.0 + 2 * side_length
        assert p == pytest.approx(expected)

    def test_zero_bottom_width_valid(self):
        """Zero bottom width is valid (becomes triangular)."""
        area = trapezoidal_area_sqft(0.0, 3.0, 2.0)
        assert area == pytest.approx(18.0)


class TestTriangularGeometry:
    """Tests for triangular channel geometry."""

    def test_area_3ft_ss2(self):
        """Area of 3 ft deep, 2:1 side slope triangular channel."""
        area = triangular_area_sqft(3.0, 2.0)
        expected = 2.0 * 3.0 ** 2
        assert area == pytest.approx(expected)

    def test_wetted_perimeter_3ft_ss2(self):
        """Wetted perimeter of 3 ft deep, 2:1 side slope triangular."""
        p = triangular_wetted_perimeter_ft(3.0, 2.0)
        side_length = 3.0 * math.sqrt(1 + 4)
        expected = 2 * side_length
        assert p == pytest.approx(expected)
