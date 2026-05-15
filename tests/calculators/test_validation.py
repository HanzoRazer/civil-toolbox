"""Tests for calculator validation utilities."""

import pytest

from civil_toolbox.calculators.validation import (
    CalculatorInputError,
    validate_positive,
    validate_non_negative,
    validate_range,
    validate_runoff_coefficient,
    validate_curve_number,
    validate_slope_percent,
    validate_mannings_n,
)


class TestCalculatorInputError:
    """Tests for CalculatorInputError."""

    def test_creates_with_message(self):
        error = CalculatorInputError("Invalid input")
        assert str(error) == "Invalid input"

    def test_creates_with_parameter(self):
        error = CalculatorInputError("Bad value", parameter="area")
        assert error.parameter == "area"

    def test_inherits_from_value_error(self):
        assert issubclass(CalculatorInputError, ValueError)


class TestValidatePositive:
    """Tests for validate_positive."""

    def test_positive_value_passes(self):
        validate_positive(1.0, "test")
        validate_positive(0.001, "test")
        validate_positive(1000.0, "test")

    def test_zero_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_positive(0, "area")
        assert exc_info.value.parameter == "area"
        assert "positive" in str(exc_info.value)

    def test_negative_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_positive(-1.0, "intensity")
        assert exc_info.value.parameter == "intensity"


class TestValidateNonNegative:
    """Tests for validate_non_negative."""

    def test_positive_value_passes(self):
        validate_non_negative(1.0, "test")

    def test_zero_passes(self):
        validate_non_negative(0, "test")

    def test_negative_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_non_negative(-0.1, "depth")
        assert exc_info.value.parameter == "depth"


class TestValidateRange:
    """Tests for validate_range."""

    def test_value_in_range_passes(self):
        validate_range(5, "test", 0, 10)
        validate_range(0, "test", 0, 10)
        validate_range(10, "test", 0, 10)

    def test_value_below_range_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_range(-1, "test", 0, 10)
        assert "between 0 and 10" in str(exc_info.value)

    def test_value_above_range_raises(self):
        with pytest.raises(CalculatorInputError):
            validate_range(11, "test", 0, 10)

    def test_exclusive_range(self):
        with pytest.raises(CalculatorInputError):
            validate_range(0, "test", 0, 10, inclusive=False)
        with pytest.raises(CalculatorInputError):
            validate_range(10, "test", 0, 10, inclusive=False)
        validate_range(5, "test", 0, 10, inclusive=False)


class TestValidateRunoffCoefficient:
    """Tests for validate_runoff_coefficient."""

    def test_valid_coefficients_pass(self):
        validate_runoff_coefficient(0.1)
        validate_runoff_coefficient(0.5)
        validate_runoff_coefficient(1.0)

    def test_zero_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_runoff_coefficient(0)
        assert exc_info.value.parameter == "runoff_coefficient"

    def test_negative_raises(self):
        with pytest.raises(CalculatorInputError):
            validate_runoff_coefficient(-0.1)

    def test_above_one_raises(self):
        with pytest.raises(CalculatorInputError):
            validate_runoff_coefficient(1.1)


class TestValidateCurveNumber:
    """Tests for validate_curve_number."""

    def test_valid_curve_numbers_pass(self):
        validate_curve_number(30)
        validate_curve_number(70)
        validate_curve_number(98)
        validate_curve_number(100)

    def test_zero_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_curve_number(0)
        assert exc_info.value.parameter == "curve_number"

    def test_negative_raises(self):
        with pytest.raises(CalculatorInputError):
            validate_curve_number(-10)

    def test_above_100_raises(self):
        with pytest.raises(CalculatorInputError):
            validate_curve_number(101)


class TestValidateSlopePercent:
    """Tests for validate_slope_percent."""

    def test_valid_slopes_pass(self):
        validate_slope_percent(0.5)
        validate_slope_percent(2.0)
        validate_slope_percent(10.0)

    def test_zero_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_slope_percent(0)
        assert exc_info.value.parameter == "slope_percent"

    def test_negative_raises(self):
        with pytest.raises(CalculatorInputError):
            validate_slope_percent(-1.0)


class TestValidateManningsN:
    """Tests for validate_mannings_n."""

    def test_valid_n_values_pass(self):
        validate_mannings_n(0.011)  # Smooth concrete
        validate_mannings_n(0.035)  # Natural channel
        validate_mannings_n(0.15)   # Dense vegetation
        validate_mannings_n(0.8)    # Very dense brush

    def test_zero_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_mannings_n(0)
        assert exc_info.value.parameter == "mannings_n"

    def test_negative_raises(self):
        with pytest.raises(CalculatorInputError):
            validate_mannings_n(-0.01)

    def test_above_one_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            validate_mannings_n(1.5)
        assert "unusually high" in str(exc_info.value)
