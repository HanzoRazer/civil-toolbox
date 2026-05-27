"""Tests for rainfall interpolation utilities."""

import pytest

from civil_toolbox.rainfall.interpolation import (
    linear_interpolate,
    interpolate_from_points,
)
from civil_toolbox.rainfall.errors import IDFInterpolationError


class TestLinearInterpolate:
    """Tests for linear_interpolate."""

    def test_midpoint_interpolation(self):
        """Interpolates correctly at midpoint."""
        result = linear_interpolate(5.0, 0.0, 10.0, 10.0, 20.0)
        assert result == 15.0

    def test_interpolation_at_lower_bound(self):
        """Returns y0 at x0."""
        result = linear_interpolate(0.0, 0.0, 10.0, 10.0, 20.0)
        assert result == 10.0

    def test_interpolation_at_upper_bound(self):
        """Returns y1 at x1."""
        result = linear_interpolate(10.0, 0.0, 10.0, 10.0, 20.0)
        assert result == 20.0

    def test_uneven_interval(self):
        """Works with uneven intervals."""
        result = linear_interpolate(3.0, 0.0, 0.0, 4.0, 8.0)
        assert result == 6.0

    def test_decreasing_y_values(self):
        """Works when y1 < y0."""
        result = linear_interpolate(5.0, 0.0, 20.0, 10.0, 10.0)
        assert result == 15.0

    def test_equal_x_values_with_matching_x(self):
        """Returns y0 when x0 == x1 and x == x0."""
        result = linear_interpolate(5.0, 5.0, 10.0, 5.0, 20.0)
        assert result == 10.0

    def test_equal_x_values_with_different_x_fails(self):
        """Raises when x0 == x1 but x is different."""
        with pytest.raises(IDFInterpolationError, match="Cannot interpolate"):
            linear_interpolate(3.0, 5.0, 10.0, 5.0, 20.0)


class TestInterpolateFromPoints:
    """Tests for interpolate_from_points."""

    def test_exact_value_returns_exact(self):
        """Exact x match returns stored value."""
        points = {10.0: 100.0, 20.0: 200.0, 30.0: 300.0}
        result = interpolate_from_points(20.0, points)
        assert result == 200.0

    def test_midpoint_interpolation(self):
        """Midpoint between two values interpolates."""
        points = {10.0: 100.0, 30.0: 300.0}
        result = interpolate_from_points(20.0, points)
        assert result == 200.0

    def test_uneven_interval_interpolation(self):
        """Works with uneven point spacing."""
        points = {0.0: 0.0, 10.0: 20.0, 100.0: 200.0}
        result = interpolate_from_points(5.0, points)
        assert result == 10.0

    def test_multiple_intervals(self):
        """Selects correct interval for interpolation."""
        points = {10.0: 100.0, 20.0: 200.0, 30.0: 400.0}
        result = interpolate_from_points(25.0, points)
        assert result == 300.0

    def test_below_range_fails(self):
        """Raises when x is below minimum."""
        points = {10.0: 100.0, 20.0: 200.0}
        with pytest.raises(IDFInterpolationError, match="below available range"):
            interpolate_from_points(5.0, points)

    def test_above_range_fails(self):
        """Raises when x is above maximum."""
        points = {10.0: 100.0, 20.0: 200.0}
        with pytest.raises(IDFInterpolationError, match="above available range"):
            interpolate_from_points(25.0, points)

    def test_empty_points_fails(self):
        """Raises when points is empty."""
        with pytest.raises(IDFInterpolationError, match="no points provided"):
            interpolate_from_points(10.0, {})

    def test_single_exact_point_works(self):
        """Single point works for exact match."""
        points = {15.0: 150.0}
        result = interpolate_from_points(15.0, points)
        assert result == 150.0

    def test_single_non_exact_point_fails(self):
        """Single point fails for non-exact match."""
        points = {15.0: 150.0}
        with pytest.raises(IDFInterpolationError, match="only one point available"):
            interpolate_from_points(20.0, points)
