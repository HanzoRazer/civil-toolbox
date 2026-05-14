"""Tests for DrainageArea domain entity."""

import pytest

from civil_toolbox.domain.drainage import DrainageArea


class TestDrainageArea:
    """Tests for DrainageArea."""

    def test_creates_with_name(self):
        area = DrainageArea(name="Basin A")
        assert area.name == "Basin A"
        assert area.id is not None

    def test_raises_on_missing_name(self):
        with pytest.raises(ValueError, match="requires a name"):
            DrainageArea(name="")

    def test_creates_with_area(self):
        area = DrainageArea(name="Test", area_acres=25.5)
        assert area.area_acres == 25.5

    def test_raises_on_non_positive_area(self):
        with pytest.raises(ValueError, match="area_acres must be positive"):
            DrainageArea(name="Test", area_acres=0)
        with pytest.raises(ValueError, match="area_acres must be positive"):
            DrainageArea(name="Test", area_acres=-10)

    def test_creates_with_runoff_coefficient(self):
        area = DrainageArea(name="Test", runoff_coefficient=0.65)
        assert area.runoff_coefficient == 0.65

    def test_runoff_coefficient_valid_range(self):
        # Valid at boundaries
        DrainageArea(name="Test", runoff_coefficient=0.0)
        DrainageArea(name="Test", runoff_coefficient=1.0)

    def test_raises_on_invalid_runoff_coefficient(self):
        with pytest.raises(ValueError, match="runoff_coefficient must be between 0 and 1"):
            DrainageArea(name="Test", runoff_coefficient=1.5)
        with pytest.raises(ValueError, match="runoff_coefficient must be between 0 and 1"):
            DrainageArea(name="Test", runoff_coefficient=-0.1)

    def test_creates_with_curve_number(self):
        area = DrainageArea(name="Test", curve_number=75)
        assert area.curve_number == 75

    def test_curve_number_valid_range(self):
        DrainageArea(name="Test", curve_number=0)
        DrainageArea(name="Test", curve_number=100)

    def test_raises_on_invalid_curve_number(self):
        with pytest.raises(ValueError, match="curve_number must be between 0 and 100"):
            DrainageArea(name="Test", curve_number=101)
        with pytest.raises(ValueError, match="curve_number must be between 0 and 100"):
            DrainageArea(name="Test", curve_number=-1)

    def test_creates_with_soil_group(self):
        area = DrainageArea(name="Test", soil_group="B")
        assert area.soil_group == "B"

    def test_creates_with_land_use(self):
        area = DrainageArea(name="Test", land_use="commercial")
        assert area.land_use == "commercial"

    def test_to_dict_serialization(self):
        area = DrainageArea(
            name="Test Area",
            area_acres=50.0,
            runoff_coefficient=0.75,
            curve_number=85,
            soil_group="C",
            land_use="residential",
        )
        data = area.to_dict()
        assert data["name"] == "Test Area"
        assert data["area_acres"] == 50.0
        assert data["runoff_coefficient"] == 0.75
        assert data["curve_number"] == 85
        assert data["soil_group"] == "C"

    def test_from_dict_deserialization(self):
        data = {
            "id": "area-123",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
            "name": "Restored Area",
            "area_acres": 30.0,
            "runoff_coefficient": 0.60,
            "curve_number": 70,
        }
        area = DrainageArea.from_dict(data)
        assert area.id == "area-123"
        assert area.name == "Restored Area"
        assert area.area_acres == 30.0

    def test_round_trip_serialization(self):
        area = DrainageArea(
            name="Round Trip",
            area_acres=100.0,
            runoff_coefficient=0.85,
            curve_number=90,
        )
        data = area.to_dict()
        restored = DrainageArea.from_dict(data)
        assert restored.id == area.id
        assert restored.name == area.name
        assert restored.area_acres == area.area_acres
        assert restored.runoff_coefficient == area.runoff_coefficient
        assert restored.curve_number == area.curve_number
