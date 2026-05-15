"""Tests for TR-55 runoff depth calculator."""

import pytest

from civil_toolbox.calculators.tr55 import (
    TR55,
    TR55RunoffResult,
)
from civil_toolbox.calculators.validation import CalculatorInputError


class TestPotentialRetention:
    """Tests for TR55.potential_retention."""

    def test_cn_100_gives_zero_retention(self):
        s = TR55.potential_retention(100)
        assert s == pytest.approx(0.0)

    def test_cn_50_gives_10_inches(self):
        s = TR55.potential_retention(50)
        assert s == pytest.approx(10.0)

    def test_cn_80_typical_urban(self):
        s = TR55.potential_retention(80)
        expected = (1000.0 / 80) - 10
        assert s == pytest.approx(expected)

    def test_cn_70_typical_residential(self):
        s = TR55.potential_retention(70)
        expected = (1000.0 / 70) - 10
        assert s == pytest.approx(expected)

    def test_invalid_cn_raises(self):
        with pytest.raises(CalculatorInputError):
            TR55.potential_retention(0)

        with pytest.raises(CalculatorInputError):
            TR55.potential_retention(101)


class TestInitialAbstraction:
    """Tests for TR55.initial_abstraction."""

    def test_default_ratio(self):
        ia = TR55.initial_abstraction(10.0)
        assert ia == pytest.approx(2.0)

    def test_custom_ratio(self):
        ia = TR55.initial_abstraction(10.0, ia_ratio=0.05)
        assert ia == pytest.approx(0.5)

    def test_zero_retention_gives_zero_ia(self):
        ia = TR55.initial_abstraction(0.0)
        assert ia == pytest.approx(0.0)

    def test_invalid_ratio_raises(self):
        with pytest.raises(CalculatorInputError):
            TR55.initial_abstraction(10.0, ia_ratio=-0.1)

        with pytest.raises(CalculatorInputError):
            TR55.initial_abstraction(10.0, ia_ratio=1.1)

    def test_negative_retention_raises(self):
        with pytest.raises(CalculatorInputError):
            TR55.initial_abstraction(-1.0)


class TestRunoffDepth:
    """Tests for TR55.runoff_depth."""

    def test_no_runoff_below_ia(self):
        result = TR55.runoff_depth(
            rainfall_depth_in=0.5,
            curve_number=70,
        )
        assert result.runoff_depth_in == pytest.approx(0.0)

    def test_runoff_above_ia(self):
        result = TR55.runoff_depth(
            rainfall_depth_in=5.0,
            curve_number=80,
        )
        assert result.runoff_depth_in > 0

    def test_high_cn_more_runoff(self):
        low_cn_result = TR55.runoff_depth(rainfall_depth_in=5.0, curve_number=60)
        high_cn_result = TR55.runoff_depth(rainfall_depth_in=5.0, curve_number=90)
        assert high_cn_result.runoff_depth_in > low_cn_result.runoff_depth_in

    def test_cn_100_equals_rainfall(self):
        result = TR55.runoff_depth(
            rainfall_depth_in=5.0,
            curve_number=100,
        )
        assert result.runoff_depth_in == pytest.approx(5.0)

    def test_returns_result_dataclass(self):
        result = TR55.runoff_depth(
            rainfall_depth_in=5.0,
            curve_number=80,
        )
        assert isinstance(result, TR55RunoffResult)
        assert result.rainfall_depth_in == 5.0
        assert result.curve_number == 80
        assert result.potential_retention_in > 0
        assert result.initial_abstraction_in > 0

    def test_known_value_cn80_p5(self):
        result = TR55.runoff_depth(
            rainfall_depth_in=5.0,
            curve_number=80,
        )
        s = 2.5
        ia = 0.5
        p_minus_ia = 5.0 - 0.5
        expected_q = (p_minus_ia ** 2) / (p_minus_ia + s)
        assert result.runoff_depth_in == pytest.approx(expected_q)
        assert result.potential_retention_in == pytest.approx(s)
        assert result.initial_abstraction_in == pytest.approx(ia)

    def test_zero_rainfall_gives_zero_runoff(self):
        result = TR55.runoff_depth(
            rainfall_depth_in=0.0,
            curve_number=80,
        )
        assert result.runoff_depth_in == pytest.approx(0.0)

    def test_invalid_rainfall_raises(self):
        with pytest.raises(CalculatorInputError):
            TR55.runoff_depth(rainfall_depth_in=-1.0, curve_number=80)

    def test_invalid_cn_raises(self):
        with pytest.raises(CalculatorInputError):
            TR55.runoff_depth(rainfall_depth_in=5.0, curve_number=0)

    def test_custom_ia_ratio(self):
        result_default = TR55.runoff_depth(
            rainfall_depth_in=5.0,
            curve_number=80,
            ia_ratio=0.2,
        )
        result_custom = TR55.runoff_depth(
            rainfall_depth_in=5.0,
            curve_number=80,
            ia_ratio=0.05,
        )
        assert result_custom.runoff_depth_in > result_default.runoff_depth_in


class TestWeightedCurveNumber:
    """Tests for TR55.weighted_curve_number."""

    def test_single_area(self):
        cn = TR55.weighted_curve_number([(80, 10.0)])
        assert cn == pytest.approx(80.0)

    def test_equal_areas(self):
        cn = TR55.weighted_curve_number([
            (60, 10.0),
            (80, 10.0),
        ])
        assert cn == pytest.approx(70.0)

    def test_weighted_by_area(self):
        cn = TR55.weighted_curve_number([
            (60, 80.0),
            (90, 20.0),
        ])
        expected = (60 * 80 + 90 * 20) / 100.0
        assert cn == pytest.approx(expected)

    def test_three_areas(self):
        cn = TR55.weighted_curve_number([
            (50, 10.0),
            (70, 30.0),
            (90, 10.0),
        ])
        expected = (50 * 10 + 70 * 30 + 90 * 10) / 50.0
        assert cn == pytest.approx(expected)

    def test_empty_list_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            TR55.weighted_curve_number([])
        assert exc_info.value.parameter == "sub_areas"

    def test_invalid_cn_raises(self):
        with pytest.raises(CalculatorInputError):
            TR55.weighted_curve_number([(101, 10.0)])

    def test_invalid_area_raises(self):
        with pytest.raises(CalculatorInputError):
            TR55.weighted_curve_number([(80, 0)])


class TestRunoffDepthMetric:
    """Tests for TR55.runoff_depth_metric."""

    def test_converts_units_correctly(self):
        rainfall_mm = 127.0
        cn = 80

        result_mm = TR55.runoff_depth_metric(rainfall_mm, cn)
        result_in = TR55.runoff_depth(rainfall_mm / 25.4, cn)

        assert result_mm == pytest.approx(result_in.runoff_depth_in * 25.4)

    def test_zero_rainfall_gives_zero(self):
        result = TR55.runoff_depth_metric(0.0, 80)
        assert result == pytest.approx(0.0)

    def test_invalid_inputs_raise(self):
        with pytest.raises(CalculatorInputError):
            TR55.runoff_depth_metric(-1.0, 80)

        with pytest.raises(CalculatorInputError):
            TR55.runoff_depth_metric(100.0, 0)
