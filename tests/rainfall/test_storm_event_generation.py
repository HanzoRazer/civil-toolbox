"""Tests for StormEvent generation from IDF curves."""

import pytest

from civil_toolbox.rainfall.idf import IDFCurve, IDFPoint
from civil_toolbox.rainfall.examples import create_example_idf_curve
from civil_toolbox.domain.storm import StormEvent


class TestStormEventGeneration:
    """Tests for IDFCurve.to_storm_event."""

    @pytest.fixture
    def curve(self):
        """Create a curve for storm generation tests."""
        return IDFCurve(
            id="test-curve",
            name="Test IDF Curve",
            source="Test Source",
            points=[
                IDFPoint(10, 15.0, 4.5),
                IDFPoint(10, 30.0, 3.0),
                IDFPoint(10, 60.0, 2.0),
                IDFPoint(100, 15.0, 7.0),
                IDFPoint(100, 30.0, 4.5),
                IDFPoint(100, 60.0, 3.0),
            ],
        )

    def test_generates_storm_event(self, curve):
        """Generates a StormEvent object."""
        storm = curve.to_storm_event(100, 15.0)
        assert isinstance(storm, StormEvent)

    def test_storm_has_return_period(self, curve):
        """Generated storm has return period."""
        storm = curve.to_storm_event(100, 15.0)
        assert storm.return_period_years == 100

    def test_storm_has_duration_hours(self, curve):
        """Generated storm has duration in hours."""
        storm = curve.to_storm_event(100, 15.0)
        assert storm.duration_hours == 0.25

    def test_storm_has_intensity(self, curve):
        """Generated storm has rainfall intensity."""
        storm = curve.to_storm_event(100, 15.0)
        assert storm.rainfall_intensity_in_per_hr == 7.0

    def test_storm_has_depth(self, curve):
        """Generated storm has rainfall depth."""
        storm = curve.to_storm_event(100, 15.0)
        expected_depth = 7.0 * 15.0 / 60.0
        assert abs(storm.rainfall_depth_in - expected_depth) < 0.001

    def test_storm_has_default_name(self, curve):
        """Generated storm has default name format."""
        storm = curve.to_storm_event(100, 15.0)
        assert storm.name == "100-year 15-minute storm"

    def test_storm_custom_name(self, curve):
        """Generated storm uses custom name."""
        storm = curve.to_storm_event(100, 15.0, name="My Storm")
        assert storm.name == "My Storm"

    def test_storm_has_description(self, curve):
        """Generated storm has description with curve name."""
        storm = curve.to_storm_event(100, 15.0)
        assert "Test IDF Curve" in storm.description

    def test_storm_with_fractional_duration(self, curve):
        """Storm name formats fractional duration."""
        storm = curve.to_storm_event(10, 22.5)
        assert storm.name == "10-year 22.5-minute storm"

    def test_storm_with_whole_duration_no_decimal(self, curve):
        """Storm name omits decimal for whole duration."""
        storm = curve.to_storm_event(10, 30.0)
        assert storm.name == "10-year 30-minute storm"

    def test_storm_with_interpolated_duration(self, curve):
        """Generates storm with interpolated duration."""
        storm = curve.to_storm_event(10, 22.5)
        expected_intensity = 3.75
        assert abs(storm.rainfall_intensity_in_per_hr - expected_intensity) < 0.001

    def test_storm_without_interpolation(self, curve):
        """Generates storm with interpolation disabled."""
        storm = curve.to_storm_event(10, 15.0, interpolate_duration=False)
        assert storm.rainfall_intensity_in_per_hr == 4.5

    def test_storm_serializes(self, curve):
        """Generated storm can be serialized."""
        storm = curve.to_storm_event(100, 15.0)
        data = storm.to_dict()
        assert data["return_period_years"] == 100
        assert data["rainfall_intensity_in_per_hr"] == 7.0

    def test_example_curve_storm_generation(self):
        """Example curve can generate storms."""
        curve = create_example_idf_curve()
        storm = curve.to_storm_event(100, 60.0)
        assert storm.return_period_years == 100
        assert storm.duration_hours == 1.0
        assert storm.rainfall_intensity_in_per_hr > 0


class TestStormEventGenerationErrors:
    """Tests for error handling in storm generation."""

    @pytest.fixture
    def curve(self):
        """Create a minimal curve."""
        return IDFCurve(
            id="test",
            name="Test",
            points=[
                IDFPoint(10, 15.0, 4.5),
                IDFPoint(10, 60.0, 2.0),
            ],
        )

    def test_missing_return_period_fails(self, curve):
        """Missing return period raises error."""
        from civil_toolbox.rainfall.errors import IDFLookupError
        with pytest.raises(IDFLookupError):
            curve.to_storm_event(100, 15.0)

    def test_duration_out_of_range_fails(self, curve):
        """Duration out of range raises error."""
        from civil_toolbox.rainfall.errors import IDFInterpolationError
        with pytest.raises(IDFInterpolationError):
            curve.to_storm_event(10, 120.0)
