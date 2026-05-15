"""Tests for Rational Method adapter."""

import pytest

from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.calculation import CalculationResult

from civil_toolbox.adapters.rational_method import RationalMethodAdapter
from civil_toolbox.adapters.errors import MissingFieldError, IncompatibleEntityError


class TestRationalMethodAdapterCalculate:
    """Tests for RationalMethodAdapter.calculate."""

    def test_calculates_peak_runoff(self):
        area = DrainageArea(
            name="Test Basin",
            area_acres=25.0,
            runoff_coefficient=0.65,
        )
        storm = StormEvent(
            name="10-year",
            rainfall_intensity_in_per_hr=5.0,
        )

        result = RationalMethodAdapter.calculate(area, storm)

        assert isinstance(result, CalculationResult)
        assert result.method == "rational_method"
        assert result.outputs["peak_runoff_cfs"] == pytest.approx(81.25)

    def test_includes_inputs_and_units(self):
        area = DrainageArea(
            name="Test",
            area_acres=10.0,
            runoff_coefficient=0.5,
        )
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        result = RationalMethodAdapter.calculate(area, storm)

        assert result.inputs["area_acres"] == 10.0
        assert result.inputs["runoff_coefficient"] == 0.5
        assert result.inputs["rainfall_intensity_in_per_hr"] == 4.0
        assert result.units["area_acres"] == "acres"
        assert result.units["peak_runoff_cfs"] == "cfs"

    def test_links_to_entity(self):
        area = DrainageArea(
            name="Test",
            area_acres=10.0,
            runoff_coefficient=0.5,
        )
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        result = RationalMethodAdapter.calculate(area, storm)

        assert result.entity_id == area.id
        assert result.entity_type == "DrainageArea"

    def test_includes_reference(self):
        area = DrainageArea(
            name="Test",
            area_acres=10.0,
            runoff_coefficient=0.5,
        )
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        result = RationalMethodAdapter.calculate(area, storm)

        assert len(result.references) == 1
        assert "HEC-22" in result.references[0].source

    def test_warns_on_large_area(self):
        area = DrainageArea(
            name="Large Basin",
            area_acres=250.0,
            runoff_coefficient=0.5,
        )
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        result = RationalMethodAdapter.calculate(area, storm)

        assert len(result.warnings) == 1
        assert "exceeds" in result.warnings[0].message
        assert "200" in result.warnings[0].message

    def test_no_warning_when_disabled(self):
        area = DrainageArea(
            name="Large Basin",
            area_acres=250.0,
            runoff_coefficient=0.5,
        )
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        result = RationalMethodAdapter.calculate(
            area, storm, warn_on_large_area=False
        )

        assert len(result.warnings) == 0

    def test_missing_area_acres_raises(self):
        area = DrainageArea(
            name="No Area",
            runoff_coefficient=0.5,
        )
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        with pytest.raises(MissingFieldError) as exc_info:
            RationalMethodAdapter.calculate(area, storm)

        assert exc_info.value.field_name == "area_acres"
        assert exc_info.value.entity_type == "DrainageArea"

    def test_missing_coefficient_raises(self):
        area = DrainageArea(
            name="No Coefficient",
            area_acres=10.0,
        )
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        with pytest.raises(MissingFieldError) as exc_info:
            RationalMethodAdapter.calculate(area, storm)

        assert exc_info.value.field_name == "runoff_coefficient"

    def test_missing_intensity_raises(self):
        area = DrainageArea(
            name="Test",
            area_acres=10.0,
            runoff_coefficient=0.5,
        )
        storm = StormEvent(name="No Intensity")

        with pytest.raises(MissingFieldError) as exc_info:
            RationalMethodAdapter.calculate(area, storm)

        assert exc_info.value.field_name == "rainfall_intensity_in_per_hr"
        assert exc_info.value.entity_type == "StormEvent"


class TestRationalMethodAdapterCalculateComposite:
    """Tests for RationalMethodAdapter.calculate_composite."""

    def test_calculates_composite_runoff(self):
        areas = [
            DrainageArea(name="Basin A", area_acres=10.0, runoff_coefficient=0.3),
            DrainageArea(name="Basin B", area_acres=10.0, runoff_coefficient=0.7),
        ]
        storm = StormEvent(
            name="10-year",
            rainfall_intensity_in_per_hr=5.0,
        )

        result = RationalMethodAdapter.calculate_composite(areas, storm)

        assert result.method == "rational_method_composite"
        weighted_c = (0.3 * 10 + 0.7 * 10) / 20
        expected_q = weighted_c * 5.0 * 20
        assert result.outputs["peak_runoff_cfs"] == pytest.approx(expected_q)

    def test_includes_composite_inputs(self):
        areas = [
            DrainageArea(name="A", area_acres=15.0, runoff_coefficient=0.4),
            DrainageArea(name="B", area_acres=5.0, runoff_coefficient=0.8),
        ]
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        result = RationalMethodAdapter.calculate_composite(areas, storm)

        assert result.inputs["sub_area_count"] == 2
        assert result.inputs["total_area_acres"] == 20.0
        expected_c = (0.4 * 15 + 0.8 * 5) / 20
        assert result.inputs["composite_runoff_coefficient"] == pytest.approx(expected_c)

    def test_records_area_ids_in_metadata(self):
        areas = [
            DrainageArea(name="A", area_acres=10.0, runoff_coefficient=0.5),
            DrainageArea(name="B", area_acres=10.0, runoff_coefficient=0.5),
        ]
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        result = RationalMethodAdapter.calculate_composite(areas, storm)

        assert "drainage_area_ids" in result.metadata
        assert len(result.metadata["drainage_area_ids"]) == 2

    def test_empty_list_raises(self):
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        with pytest.raises(IncompatibleEntityError):
            RationalMethodAdapter.calculate_composite([], storm)

    def test_missing_field_in_any_area_raises(self):
        areas = [
            DrainageArea(name="A", area_acres=10.0, runoff_coefficient=0.5),
            DrainageArea(name="B", area_acres=10.0),  # Missing coefficient
        ]
        storm = StormEvent(
            name="Storm",
            rainfall_intensity_in_per_hr=4.0,
        )

        with pytest.raises(MissingFieldError) as exc_info:
            RationalMethodAdapter.calculate_composite(areas, storm)

        assert exc_info.value.field_name == "runoff_coefficient"
