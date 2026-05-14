"""Tests for StormEvent domain entity."""

import pytest

from civil_toolbox.domain.storm import StormEvent


class TestStormEvent:
    """Tests for StormEvent."""

    def test_creates_with_name(self):
        event = StormEvent(name="100-year Storm")
        assert event.name == "100-year Storm"
        assert event.id is not None

    def test_raises_on_missing_name(self):
        with pytest.raises(ValueError, match="requires a name"):
            StormEvent(name="")

    def test_creates_with_return_period(self):
        event = StormEvent(name="Test", return_period_years=100)
        assert event.return_period_years == 100

    def test_raises_on_non_positive_return_period(self):
        with pytest.raises(ValueError, match="return_period_years must be positive"):
            StormEvent(name="Test", return_period_years=0)
        with pytest.raises(ValueError, match="return_period_years must be positive"):
            StormEvent(name="Test", return_period_years=-25)

    def test_creates_with_duration(self):
        event = StormEvent(name="Test", duration_hours=24.0)
        assert event.duration_hours == 24.0

    def test_raises_on_non_positive_duration(self):
        with pytest.raises(ValueError, match="duration_hours must be positive"):
            StormEvent(name="Test", duration_hours=0)

    def test_creates_with_rainfall_depth(self):
        event = StormEvent(name="Test", rainfall_depth_in=5.5)
        assert event.rainfall_depth_in == 5.5

    def test_allows_zero_rainfall_depth(self):
        event = StormEvent(name="Test", rainfall_depth_in=0.0)
        assert event.rainfall_depth_in == 0.0

    def test_raises_on_negative_rainfall_depth(self):
        with pytest.raises(ValueError, match="rainfall_depth_in cannot be negative"):
            StormEvent(name="Test", rainfall_depth_in=-1.0)

    def test_creates_with_rainfall_intensity(self):
        event = StormEvent(name="Test", rainfall_intensity_in_per_hr=4.5)
        assert event.rainfall_intensity_in_per_hr == 4.5

    def test_raises_on_negative_intensity(self):
        with pytest.raises(ValueError, match="rainfall_intensity_in_per_hr cannot be negative"):
            StormEvent(name="Test", rainfall_intensity_in_per_hr=-2.0)

    def test_creates_with_distribution(self):
        event = StormEvent(name="Test", distribution="Type III")
        assert event.distribution == "Type III"

    def test_creates_with_full_properties(self):
        event = StormEvent(
            name="Design Storm",
            return_period_years=25,
            duration_hours=24.0,
            rainfall_depth_in=6.0,
            rainfall_intensity_in_per_hr=0.25,
            distribution="Type II",
            description="25-year 24-hour design storm",
        )
        assert event.return_period_years == 25
        assert event.duration_hours == 24.0
        assert event.rainfall_depth_in == 6.0
        assert event.distribution == "Type II"

    def test_to_dict_serialization(self):
        event = StormEvent(
            name="Serialization Test",
            return_period_years=50,
            rainfall_depth_in=7.5,
        )
        data = event.to_dict()
        assert data["name"] == "Serialization Test"
        assert data["return_period_years"] == 50
        assert data["rainfall_depth_in"] == 7.5

    def test_from_dict_deserialization(self):
        data = {
            "id": "storm-123",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
            "name": "Restored Storm",
            "return_period_years": 100,
            "duration_hours": 12.0,
            "rainfall_depth_in": 8.0,
        }
        event = StormEvent.from_dict(data)
        assert event.id == "storm-123"
        assert event.name == "Restored Storm"
        assert event.return_period_years == 100

    def test_round_trip_serialization(self):
        event = StormEvent(
            name="Round Trip Storm",
            return_period_years=10,
            duration_hours=6.0,
            rainfall_depth_in=3.5,
            rainfall_intensity_in_per_hr=0.58,
        )
        data = event.to_dict()
        restored = StormEvent.from_dict(data)
        assert restored.id == event.id
        assert restored.name == event.name
        assert restored.return_period_years == event.return_period_years
        assert restored.rainfall_depth_in == event.rainfall_depth_in
