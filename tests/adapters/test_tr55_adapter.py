"""Tests for TR-55 adapter."""

import pytest

from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.calculation import CalculationResult

from civil_toolbox.adapters.tr55 import TR55Adapter
from civil_toolbox.adapters.errors import MissingFieldError, IncompatibleEntityError


class TestTR55AdapterCalculateRunoffDepth:
    """Tests for TR55Adapter.calculate_runoff_depth."""

    def test_calculates_runoff_depth(self):
        area = DrainageArea(
            name="Test Basin",
            curve_number=80,
        )
        storm = StormEvent(
            name="10-year",
            rainfall_depth_in=5.0,
        )

        result = TR55Adapter.calculate_runoff_depth(area, storm)

        assert isinstance(result, CalculationResult)
        assert result.method == "tr55_runoff_depth"
        assert result.outputs["runoff_depth_in"] > 0

    def test_includes_intermediate_values(self):
        area = DrainageArea(name="Test", curve_number=80)
        storm = StormEvent(name="Storm", rainfall_depth_in=5.0)

        result = TR55Adapter.calculate_runoff_depth(area, storm)

        assert "potential_retention_in" in result.outputs
        assert "initial_abstraction_in" in result.outputs
        assert result.outputs["potential_retention_in"] == pytest.approx(2.5)
        assert result.outputs["initial_abstraction_in"] == pytest.approx(0.5)

    def test_includes_inputs_and_units(self):
        area = DrainageArea(name="Test", curve_number=75)
        storm = StormEvent(name="Storm", rainfall_depth_in=4.0)

        result = TR55Adapter.calculate_runoff_depth(area, storm)

        assert result.inputs["rainfall_depth_in"] == 4.0
        assert result.inputs["curve_number"] == 75
        assert result.inputs["ia_ratio"] == 0.2
        assert result.units["runoff_depth_in"] == "in"

    def test_links_to_entity(self):
        area = DrainageArea(name="Test", curve_number=80)
        storm = StormEvent(name="Storm", rainfall_depth_in=5.0)

        result = TR55Adapter.calculate_runoff_depth(area, storm)

        assert result.entity_id == area.id
        assert result.entity_type == "DrainageArea"

    def test_custom_ia_ratio(self):
        area = DrainageArea(name="Test", curve_number=80)
        storm = StormEvent(name="Storm", rainfall_depth_in=5.0)

        result = TR55Adapter.calculate_runoff_depth(area, storm, ia_ratio=0.05)

        assert result.inputs["ia_ratio"] == 0.05
        assert len(result.assumptions) == 1
        assert "initial abstraction" in result.assumptions[0].description.lower()

    def test_missing_curve_number_raises(self):
        area = DrainageArea(name="No CN")
        storm = StormEvent(name="Storm", rainfall_depth_in=5.0)

        with pytest.raises(MissingFieldError) as exc_info:
            TR55Adapter.calculate_runoff_depth(area, storm)

        assert exc_info.value.field_name == "curve_number"

    def test_missing_rainfall_depth_raises(self):
        area = DrainageArea(name="Test", curve_number=80)
        storm = StormEvent(name="No Depth")

        with pytest.raises(MissingFieldError) as exc_info:
            TR55Adapter.calculate_runoff_depth(area, storm)

        assert exc_info.value.field_name == "rainfall_depth_in"


class TestTR55AdapterCalculateWeightedCN:
    """Tests for TR55Adapter.calculate_weighted_cn."""

    def test_calculates_weighted_cn(self):
        areas = [
            DrainageArea(name="A", curve_number=60, area_acres=10.0),
            DrainageArea(name="B", curve_number=80, area_acres=10.0),
        ]

        result = TR55Adapter.calculate_weighted_cn(areas)

        assert result.method == "tr55_weighted_cn"
        assert result.outputs["weighted_curve_number"] == pytest.approx(70.0)

    def test_includes_inputs(self):
        areas = [
            DrainageArea(name="A", curve_number=70, area_acres=15.0),
            DrainageArea(name="B", curve_number=90, area_acres=5.0),
        ]

        result = TR55Adapter.calculate_weighted_cn(areas)

        assert result.inputs["sub_area_count"] == 2
        assert result.inputs["total_area_acres"] == 20.0

    def test_records_area_ids(self):
        areas = [
            DrainageArea(name="A", curve_number=70, area_acres=10.0),
            DrainageArea(name="B", curve_number=80, area_acres=10.0),
        ]

        result = TR55Adapter.calculate_weighted_cn(areas)

        assert "drainage_area_ids" in result.metadata
        assert len(result.metadata["drainage_area_ids"]) == 2

    def test_empty_list_raises(self):
        with pytest.raises(IncompatibleEntityError):
            TR55Adapter.calculate_weighted_cn([])

    def test_missing_cn_raises(self):
        areas = [
            DrainageArea(name="A", curve_number=70, area_acres=10.0),
            DrainageArea(name="B", area_acres=10.0),  # Missing CN
        ]

        with pytest.raises(MissingFieldError) as exc_info:
            TR55Adapter.calculate_weighted_cn(areas)

        assert exc_info.value.field_name == "curve_number"

    def test_missing_area_raises(self):
        areas = [
            DrainageArea(name="A", curve_number=70, area_acres=10.0),
            DrainageArea(name="B", curve_number=80),  # Missing area
        ]

        with pytest.raises(MissingFieldError) as exc_info:
            TR55Adapter.calculate_weighted_cn(areas)

        assert exc_info.value.field_name == "area_acres"


class TestTR55AdapterCalculateRunoffVolume:
    """Tests for TR55Adapter.calculate_runoff_volume."""

    def test_calculates_volume(self):
        area = DrainageArea(
            name="Test Basin",
            curve_number=80,
            area_acres=100.0,
        )
        storm = StormEvent(
            name="10-year",
            rainfall_depth_in=5.0,
        )

        result = TR55Adapter.calculate_runoff_volume(area, storm)

        assert result.method == "tr55_runoff_volume"
        assert "runoff_volume_cf" in result.outputs
        assert "runoff_volume_ac_ft" in result.outputs
        assert result.outputs["runoff_volume_cf"] > 0

    def test_volume_units(self):
        area = DrainageArea(name="Test", curve_number=80, area_acres=50.0)
        storm = StormEvent(name="Storm", rainfall_depth_in=4.0)

        result = TR55Adapter.calculate_runoff_volume(area, storm)

        assert result.units["runoff_volume_cf"] == "cf"
        assert result.units["runoff_volume_ac_ft"] == "ac-ft"

    def test_missing_area_acres_raises(self):
        area = DrainageArea(name="Test", curve_number=80)  # Missing area
        storm = StormEvent(name="Storm", rainfall_depth_in=5.0)

        with pytest.raises(MissingFieldError) as exc_info:
            TR55Adapter.calculate_runoff_volume(area, storm)

        assert exc_info.value.field_name == "area_acres"
