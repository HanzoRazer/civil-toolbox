"""Tests for IDF curve data models."""

import pytest

from civil_toolbox.rainfall.idf import IDFPoint, IDFCurve
from civil_toolbox.rainfall.errors import (
    InvalidIDFDataError,
    IDFLookupError,
    IDFInterpolationError,
)
from civil_toolbox.rainfall.examples import create_example_idf_curve


class TestIDFPoint:
    """Tests for IDFPoint dataclass."""

    def test_creates_valid_point(self):
        """Creates point with required fields."""
        point = IDFPoint(
            return_period_years=100,
            duration_minutes=15.0,
            rainfall_intensity_in_per_hr=6.5,
        )
        assert point.return_period_years == 100
        assert point.duration_minutes == 15.0
        assert point.rainfall_intensity_in_per_hr == 6.5

    def test_creates_point_with_depth(self):
        """Creates point with optional depth."""
        point = IDFPoint(
            return_period_years=100,
            duration_minutes=60.0,
            rainfall_intensity_in_per_hr=3.0,
            rainfall_depth_in=3.0,
        )
        assert point.rainfall_depth_in == 3.0

    def test_creates_point_with_metadata(self):
        """Creates point with metadata."""
        point = IDFPoint(
            return_period_years=100,
            duration_minutes=15.0,
            rainfall_intensity_in_per_hr=6.5,
            metadata={"source": "test"},
        )
        assert point.metadata["source"] == "test"

    def test_negative_return_period_fails(self):
        """Negative return period raises error."""
        with pytest.raises(InvalidIDFDataError):
            IDFPoint(
                return_period_years=-10,
                duration_minutes=15.0,
                rainfall_intensity_in_per_hr=6.5,
            )

    def test_zero_duration_fails(self):
        """Zero duration raises error."""
        with pytest.raises(InvalidIDFDataError):
            IDFPoint(
                return_period_years=100,
                duration_minutes=0.0,
                rainfall_intensity_in_per_hr=6.5,
            )

    def test_negative_intensity_fails(self):
        """Negative intensity raises error."""
        with pytest.raises(InvalidIDFDataError):
            IDFPoint(
                return_period_years=100,
                duration_minutes=15.0,
                rainfall_intensity_in_per_hr=-1.0,
            )

    def test_negative_depth_fails(self):
        """Negative depth raises error."""
        with pytest.raises(InvalidIDFDataError):
            IDFPoint(
                return_period_years=100,
                duration_minutes=15.0,
                rainfall_intensity_in_per_hr=6.5,
                rainfall_depth_in=-0.5,
            )

    def test_serializes_to_dict(self):
        """Point serializes to dictionary."""
        point = IDFPoint(
            return_period_years=100,
            duration_minutes=15.0,
            rainfall_intensity_in_per_hr=6.5,
            rainfall_depth_in=1.625,
        )
        data = point.to_dict()
        assert data["return_period_years"] == 100
        assert data["duration_minutes"] == 15.0
        assert data["rainfall_intensity_in_per_hr"] == 6.5
        assert data["rainfall_depth_in"] == 1.625

    def test_deserializes_from_dict(self):
        """Point deserializes from dictionary."""
        data = {
            "return_period_years": 100,
            "duration_minutes": 15.0,
            "rainfall_intensity_in_per_hr": 6.5,
            "rainfall_depth_in": 1.625,
            "metadata": {"source": "test"},
        }
        point = IDFPoint.from_dict(data)
        assert point.return_period_years == 100
        assert point.rainfall_depth_in == 1.625
        assert point.metadata["source"] == "test"

    def test_round_trip_serialization(self):
        """Point round-trips through serialization."""
        original = IDFPoint(
            return_period_years=100,
            duration_minutes=15.0,
            rainfall_intensity_in_per_hr=6.5,
            rainfall_depth_in=1.625,
        )
        restored = IDFPoint.from_dict(original.to_dict())
        assert restored.return_period_years == original.return_period_years
        assert restored.duration_minutes == original.duration_minutes
        assert restored.rainfall_intensity_in_per_hr == original.rainfall_intensity_in_per_hr
        assert restored.rainfall_depth_in == original.rainfall_depth_in


class TestIDFCurve:
    """Tests for IDFCurve dataclass."""

    @pytest.fixture
    def simple_curve(self):
        """Create a simple curve with two return periods."""
        return IDFCurve(
            id="test-curve",
            name="Test Curve",
            points=[
                IDFPoint(10, 15.0, 4.5),
                IDFPoint(10, 30.0, 3.0),
                IDFPoint(10, 60.0, 2.0),
                IDFPoint(100, 15.0, 7.0),
                IDFPoint(100, 30.0, 4.5),
                IDFPoint(100, 60.0, 3.0),
            ],
        )

    def test_creates_valid_curve(self, simple_curve):
        """Creates curve with valid data."""
        assert simple_curve.id == "test-curve"
        assert simple_curve.name == "Test Curve"
        assert len(simple_curve.points) == 6

    def test_creates_curve_with_optional_fields(self):
        """Creates curve with optional fields."""
        curve = IDFCurve(
            id="test",
            name="Test",
            source="NOAA Atlas 14",
            location="Houston, TX",
            station_id="GHCND:USW00012918",
            points=[IDFPoint(10, 15.0, 4.5)],
        )
        assert curve.source == "NOAA Atlas 14"
        assert curve.location == "Houston, TX"
        assert curve.station_id == "GHCND:USW00012918"

    def test_empty_id_fails(self):
        """Empty curve ID fails."""
        with pytest.raises(InvalidIDFDataError, match="id is required"):
            IDFCurve(id="", name="Test", points=[IDFPoint(10, 15.0, 4.5)])

    def test_empty_name_fails(self):
        """Empty curve name fails."""
        with pytest.raises(InvalidIDFDataError, match="name is required"):
            IDFCurve(id="test", name="", points=[IDFPoint(10, 15.0, 4.5)])

    def test_empty_points_fails(self):
        """Empty points list fails."""
        with pytest.raises(InvalidIDFDataError, match="at least one point"):
            IDFCurve(id="test", name="Test", points=[])

    def test_duplicate_point_fails(self):
        """Duplicate return period + duration fails."""
        with pytest.raises(InvalidIDFDataError, match="Duplicate point"):
            IDFCurve(
                id="test",
                name="Test",
                points=[
                    IDFPoint(10, 15.0, 4.5),
                    IDFPoint(10, 15.0, 5.0),
                ],
            )

    def test_get_return_periods_sorted(self, simple_curve):
        """Return periods are sorted ascending."""
        periods = simple_curve.get_return_periods()
        assert periods == [10, 100]

    def test_get_durations_all(self, simple_curve):
        """Gets all unique durations."""
        durations = simple_curve.get_durations()
        assert durations == [15.0, 30.0, 60.0]

    def test_get_durations_for_return_period(self, simple_curve):
        """Gets durations for specific return period."""
        durations = simple_curve.get_durations(return_period_years=10)
        assert durations == [15.0, 30.0, 60.0]

    def test_serializes_to_dict(self, simple_curve):
        """Curve serializes to dictionary."""
        data = simple_curve.to_dict()
        assert data["id"] == "test-curve"
        assert data["name"] == "Test Curve"
        assert len(data["points"]) == 6

    def test_deserializes_from_dict(self, simple_curve):
        """Curve deserializes from dictionary."""
        data = simple_curve.to_dict()
        restored = IDFCurve.from_dict(data)
        assert restored.id == simple_curve.id
        assert restored.name == simple_curve.name
        assert len(restored.points) == len(simple_curve.points)

    def test_round_trip_serialization(self, simple_curve):
        """Curve round-trips through serialization."""
        restored = IDFCurve.from_dict(simple_curve.to_dict())
        assert restored.get_return_periods() == simple_curve.get_return_periods()
        assert restored.get_durations() == simple_curve.get_durations()

    def test_default_units(self, simple_curve):
        """Curve has default units metadata."""
        assert simple_curve.units["duration"] == "minutes"
        assert simple_curve.units["rainfall_intensity"] == "in/hr"
        assert simple_curve.units["rainfall_depth"] == "in"


class TestIDFCurveLookupIntensity:
    """Tests for IDFCurve.lookup_intensity."""

    @pytest.fixture
    def curve(self):
        """Create a curve for lookup tests."""
        return IDFCurve(
            id="test",
            name="Test",
            points=[
                IDFPoint(10, 15.0, 4.5),
                IDFPoint(10, 30.0, 3.0),
                IDFPoint(10, 60.0, 2.0),
                IDFPoint(100, 15.0, 7.0),
                IDFPoint(100, 30.0, 4.5),
                IDFPoint(100, 60.0, 3.0),
            ],
        )

    def test_exact_lookup(self, curve):
        """Exact return period and duration returns stored value."""
        result = curve.lookup_intensity(10, 15.0)
        assert result == 4.5

    def test_duration_interpolation(self, curve):
        """Interpolates between durations."""
        result = curve.lookup_intensity(10, 22.5)
        assert result == 3.75

    def test_duration_interpolation_disabled_fails(self, curve):
        """Non-exact duration fails when interpolation disabled."""
        with pytest.raises(IDFLookupError, match="Enable interpolate_duration"):
            curve.lookup_intensity(10, 22.5, interpolate_duration=False)

    def test_missing_return_period_fails(self, curve):
        """Missing return period raises error."""
        with pytest.raises(IDFLookupError, match="Return period 50 not in curve"):
            curve.lookup_intensity(50, 15.0)

    def test_below_duration_range_fails(self, curve):
        """Duration below range fails."""
        with pytest.raises(IDFInterpolationError, match="below available range"):
            curve.lookup_intensity(10, 5.0)

    def test_above_duration_range_fails(self, curve):
        """Duration above range fails."""
        with pytest.raises(IDFInterpolationError, match="above available range"):
            curve.lookup_intensity(10, 120.0)

    def test_return_period_interpolation_raises(self, curve):
        """Return period interpolation raises not implemented."""
        with pytest.raises(IDFInterpolationError, match="not implemented"):
            curve.lookup_intensity(50, 15.0, interpolate_return_period=True)


class TestIDFCurveLookupDepth:
    """Tests for IDFCurve.lookup_depth."""

    @pytest.fixture
    def curve_with_depth(self):
        """Create a curve with stored depth values."""
        return IDFCurve(
            id="test",
            name="Test",
            points=[
                IDFPoint(10, 15.0, 4.5, rainfall_depth_in=1.125),
                IDFPoint(10, 60.0, 2.0, rainfall_depth_in=2.0),
            ],
        )

    @pytest.fixture
    def curve_without_depth(self):
        """Create a curve without stored depth values."""
        return IDFCurve(
            id="test",
            name="Test",
            points=[
                IDFPoint(10, 15.0, 4.5),
                IDFPoint(10, 60.0, 2.0),
            ],
        )

    def test_exact_stored_depth(self, curve_with_depth):
        """Returns stored depth for exact match."""
        result = curve_with_depth.lookup_depth(10, 15.0)
        assert result == 1.125

    def test_interpolated_stored_depth(self, curve_with_depth):
        """Interpolates between stored depths."""
        result = curve_with_depth.lookup_depth(10, 37.5)
        expected = (1.125 + 2.0) / 2
        assert abs(result - expected) < 0.001

    def test_derived_depth_from_intensity(self, curve_without_depth):
        """Derives depth from intensity when not stored."""
        result = curve_without_depth.lookup_depth(10, 15.0)
        expected = 4.5 * 15.0 / 60.0
        assert abs(result - expected) < 0.001

    def test_derived_depth_with_interpolation(self, curve_without_depth):
        """Derives depth from interpolated intensity."""
        result = curve_without_depth.lookup_depth(10, 37.5)
        intensity = curve_without_depth.lookup_intensity(10, 37.5)
        expected = intensity * 37.5 / 60.0
        assert abs(result - expected) < 0.001

    def test_missing_return_period_fails(self, curve_without_depth):
        """Missing return period fails."""
        with pytest.raises(IDFLookupError):
            curve_without_depth.lookup_depth(50, 15.0)


class TestExampleIDFCurve:
    """Tests for synthetic example IDF curve."""

    def test_example_curve_loads(self):
        """Example curve loads successfully."""
        curve = create_example_idf_curve()
        assert curve.id == "example-synthetic"
        assert curve.name == "Example Synthetic IDF Curve"

    def test_example_has_multiple_return_periods(self):
        """Example curve has multiple return periods."""
        curve = create_example_idf_curve()
        periods = curve.get_return_periods()
        assert len(periods) >= 3
        assert 10 in periods
        assert 100 in periods

    def test_example_has_multiple_durations(self):
        """Example curve has multiple durations."""
        curve = create_example_idf_curve()
        durations = curve.get_durations()
        assert len(durations) >= 3
        assert 15.0 in durations
        assert 60.0 in durations

    def test_example_lookup_works(self):
        """Example curve lookup works."""
        curve = create_example_idf_curve()
        intensity = curve.lookup_intensity(10, 15.0)
        assert intensity > 0

    def test_example_marked_synthetic(self):
        """Example curve is marked as synthetic."""
        curve = create_example_idf_curve()
        assert curve.metadata.get("synthetic") is True
        assert curve.metadata.get("for_testing_only") is True


class TestPublicExports:
    """Tests for public module exports."""

    def test_idf_point_importable(self):
        """IDFPoint is importable from package."""
        from civil_toolbox.rainfall import IDFPoint
        assert IDFPoint is not None

    def test_idf_curve_importable(self):
        """IDFCurve is importable from package."""
        from civil_toolbox.rainfall import IDFCurve
        assert IDFCurve is not None

    def test_example_function_importable(self):
        """create_example_idf_curve is importable."""
        from civil_toolbox.rainfall import create_example_idf_curve
        assert create_example_idf_curve is not None

    def test_errors_importable(self):
        """Error classes are importable."""
        from civil_toolbox.rainfall import (
            RainfallDataError,
            InvalidIDFDataError,
            IDFLookupError,
            IDFInterpolationError,
        )
        assert RainfallDataError is not None
        assert InvalidIDFDataError is not None
        assert IDFLookupError is not None
        assert IDFInterpolationError is not None
