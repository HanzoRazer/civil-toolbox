"""Tests for Rational Method runoff calculator."""

import pytest

from civil_toolbox.calculators.rational_method import (
    RationalMethod,
    RationalMethodResult,
    RationalMethodResultMetric,
)
from civil_toolbox.calculators.validation import CalculatorInputError


class TestRationalMethodCalculate:
    """Tests for RationalMethod.calculate."""

    def test_basic_calculation(self):
        result = RationalMethod.calculate(
            runoff_coefficient=0.5,
            rainfall_intensity_in_per_hr=4.0,
            area_acres=10.0,
        )
        assert result.peak_runoff_cfs == pytest.approx(20.0)

    def test_unit_values(self):
        result = RationalMethod.calculate(
            runoff_coefficient=1.0,
            rainfall_intensity_in_per_hr=1.0,
            area_acres=1.0,
        )
        assert result.peak_runoff_cfs == pytest.approx(1.0)

    def test_realistic_residential(self):
        result = RationalMethod.calculate(
            runoff_coefficient=0.45,
            rainfall_intensity_in_per_hr=5.5,
            area_acres=25.0,
        )
        assert result.peak_runoff_cfs == pytest.approx(61.875)

    def test_returns_result_dataclass(self):
        result = RationalMethod.calculate(
            runoff_coefficient=0.5,
            rainfall_intensity_in_per_hr=4.0,
            area_acres=10.0,
        )
        assert isinstance(result, RationalMethodResult)
        assert result.runoff_coefficient == 0.5
        assert result.rainfall_intensity_in_per_hr == 4.0
        assert result.area_acres == 10.0

    def test_invalid_coefficient_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            RationalMethod.calculate(
                runoff_coefficient=1.5,
                rainfall_intensity_in_per_hr=4.0,
                area_acres=10.0,
            )
        assert exc_info.value.parameter == "runoff_coefficient"

    def test_zero_coefficient_raises(self):
        with pytest.raises(CalculatorInputError):
            RationalMethod.calculate(
                runoff_coefficient=0,
                rainfall_intensity_in_per_hr=4.0,
                area_acres=10.0,
            )

    def test_negative_intensity_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            RationalMethod.calculate(
                runoff_coefficient=0.5,
                rainfall_intensity_in_per_hr=-1.0,
                area_acres=10.0,
            )
        assert exc_info.value.parameter == "rainfall_intensity_in_per_hr"

    def test_zero_area_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            RationalMethod.calculate(
                runoff_coefficient=0.5,
                rainfall_intensity_in_per_hr=4.0,
                area_acres=0,
            )
        assert exc_info.value.parameter == "area_acres"


class TestRationalMethodCalculateMetric:
    """Tests for RationalMethod.calculate_metric."""

    def test_basic_calculation(self):
        result = RationalMethod.calculate_metric(
            runoff_coefficient=0.5,
            rainfall_intensity_mm_per_hr=50.0,
            area_hectares=10.0,
        )
        expected = 0.5 * 50.0 * 10.0 / 360.0
        assert result.peak_runoff_m3_per_s == pytest.approx(expected)

    def test_returns_result_dataclass(self):
        result = RationalMethod.calculate_metric(
            runoff_coefficient=0.5,
            rainfall_intensity_mm_per_hr=50.0,
            area_hectares=10.0,
        )
        assert isinstance(result, RationalMethodResultMetric)
        assert result.runoff_coefficient == 0.5
        assert result.rainfall_intensity_mm_per_hr == 50.0
        assert result.area_hectares == 10.0

    def test_known_value(self):
        result = RationalMethod.calculate_metric(
            runoff_coefficient=1.0,
            rainfall_intensity_mm_per_hr=360.0,
            area_hectares=1.0,
        )
        assert result.peak_runoff_m3_per_s == pytest.approx(1.0)

    def test_invalid_inputs_raise(self):
        with pytest.raises(CalculatorInputError):
            RationalMethod.calculate_metric(
                runoff_coefficient=0,
                rainfall_intensity_mm_per_hr=50.0,
                area_hectares=10.0,
            )


class TestRationalMethodCalculateComposite:
    """Tests for RationalMethod.calculate_composite."""

    def test_single_sub_area(self):
        result = RationalMethod.calculate_composite(
            sub_areas=[(0.5, 10.0)],
            rainfall_intensity_in_per_hr=4.0,
        )
        assert result.peak_runoff_cfs == pytest.approx(20.0)
        assert result.runoff_coefficient == pytest.approx(0.5)
        assert result.area_acres == pytest.approx(10.0)

    def test_multiple_sub_areas(self):
        result = RationalMethod.calculate_composite(
            sub_areas=[
                (0.3, 5.0),   # Forest: C=0.3, 5 acres
                (0.7, 5.0),   # Parking: C=0.7, 5 acres
            ],
            rainfall_intensity_in_per_hr=4.0,
        )
        expected_c = (0.3 * 5 + 0.7 * 5) / 10.0
        assert result.runoff_coefficient == pytest.approx(expected_c)
        assert result.area_acres == pytest.approx(10.0)
        expected_q = expected_c * 4.0 * 10.0
        assert result.peak_runoff_cfs == pytest.approx(expected_q)

    def test_weighted_coefficient(self):
        result = RationalMethod.calculate_composite(
            sub_areas=[
                (0.2, 80.0),  # Large forest area
                (0.9, 20.0),  # Small impervious area
            ],
            rainfall_intensity_in_per_hr=5.0,
        )
        expected_c = (0.2 * 80 + 0.9 * 20) / 100.0
        assert result.runoff_coefficient == pytest.approx(expected_c)

    def test_empty_sub_areas_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            RationalMethod.calculate_composite(
                sub_areas=[],
                rainfall_intensity_in_per_hr=4.0,
            )
        assert exc_info.value.parameter == "sub_areas"

    def test_invalid_sub_area_coefficient_raises(self):
        with pytest.raises(CalculatorInputError):
            RationalMethod.calculate_composite(
                sub_areas=[(1.5, 10.0)],
                rainfall_intensity_in_per_hr=4.0,
            )

    def test_invalid_sub_area_area_raises(self):
        with pytest.raises(CalculatorInputError):
            RationalMethod.calculate_composite(
                sub_areas=[(0.5, 0)],
                rainfall_intensity_in_per_hr=4.0,
            )

    def test_invalid_intensity_raises(self):
        with pytest.raises(CalculatorInputError):
            RationalMethod.calculate_composite(
                sub_areas=[(0.5, 10.0)],
                rainfall_intensity_in_per_hr=-1.0,
            )
