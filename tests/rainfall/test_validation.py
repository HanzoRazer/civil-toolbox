"""Tests for rainfall validation utilities."""

import pytest

from civil_toolbox.rainfall.errors import (
    RainfallDataError,
    InvalidIDFDataError,
    IDFLookupError,
    IDFInterpolationError,
)
from civil_toolbox.rainfall.validation import (
    require_positive,
    require_non_negative,
    validate_return_period,
    validate_duration_minutes,
    validate_intensity_in_per_hr,
    validate_depth_in,
)


class TestRainfallErrors:
    """Tests for rainfall error hierarchy."""

    def test_invalid_idf_data_inherits_rainfall_error(self):
        """InvalidIDFDataError inherits from RainfallDataError."""
        error = InvalidIDFDataError("test")
        assert isinstance(error, RainfallDataError)

    def test_idf_lookup_error_inherits_rainfall_error(self):
        """IDFLookupError inherits from RainfallDataError."""
        error = IDFLookupError("test")
        assert isinstance(error, RainfallDataError)

    def test_idf_interpolation_error_inherits_lookup_error(self):
        """IDFInterpolationError inherits from IDFLookupError."""
        error = IDFInterpolationError("test")
        assert isinstance(error, IDFLookupError)
        assert isinstance(error, RainfallDataError)

    def test_errors_include_message(self):
        """Errors include useful messages."""
        error = InvalidIDFDataError("specific issue")
        assert "specific issue" in str(error)


class TestRequirePositive:
    """Tests for require_positive."""

    def test_positive_value_passes(self):
        """Positive value returns unchanged."""
        result = require_positive(5.0, "test_field")
        assert result == 5.0

    def test_zero_fails(self):
        """Zero raises error."""
        with pytest.raises(InvalidIDFDataError, match="must be positive"):
            require_positive(0.0, "test_field")

    def test_negative_fails(self):
        """Negative raises error."""
        with pytest.raises(InvalidIDFDataError, match="must be positive"):
            require_positive(-1.0, "test_field")

    def test_error_includes_field_name(self):
        """Error message includes field name."""
        with pytest.raises(InvalidIDFDataError, match="my_field"):
            require_positive(0.0, "my_field")


class TestRequireNonNegative:
    """Tests for require_non_negative."""

    def test_positive_value_passes(self):
        """Positive value passes."""
        result = require_non_negative(5.0, "test_field")
        assert result == 5.0

    def test_zero_passes(self):
        """Zero passes (it's non-negative)."""
        result = require_non_negative(0.0, "test_field")
        assert result == 0.0

    def test_negative_fails(self):
        """Negative raises error."""
        with pytest.raises(InvalidIDFDataError, match="cannot be negative"):
            require_non_negative(-1.0, "test_field")


class TestValidateReturnPeriod:
    """Tests for validate_return_period."""

    def test_valid_return_period_passes(self):
        """Valid return period passes."""
        result = validate_return_period(100)
        assert result == 100

    def test_zero_return_period_fails(self):
        """Zero return period fails."""
        with pytest.raises(InvalidIDFDataError, match="must be positive"):
            validate_return_period(0)

    def test_negative_return_period_fails(self):
        """Negative return period fails."""
        with pytest.raises(InvalidIDFDataError, match="must be positive"):
            validate_return_period(-10)

    def test_non_integer_return_period_fails(self):
        """Non-integer return period fails."""
        with pytest.raises(InvalidIDFDataError, match="must be an integer"):
            validate_return_period(10.5)  # type: ignore


class TestValidateDurationMinutes:
    """Tests for validate_duration_minutes."""

    def test_valid_duration_passes(self):
        """Valid duration passes."""
        result = validate_duration_minutes(15.0)
        assert result == 15.0

    def test_zero_duration_fails(self):
        """Zero duration fails."""
        with pytest.raises(InvalidIDFDataError, match="must be positive"):
            validate_duration_minutes(0.0)

    def test_negative_duration_fails(self):
        """Negative duration fails."""
        with pytest.raises(InvalidIDFDataError, match="must be positive"):
            validate_duration_minutes(-5.0)

    def test_integer_converted_to_float(self):
        """Integer input is converted to float."""
        result = validate_duration_minutes(15)
        assert result == 15.0
        assert isinstance(result, float)


class TestValidateIntensity:
    """Tests for validate_intensity_in_per_hr."""

    def test_valid_intensity_passes(self):
        """Valid intensity passes."""
        result = validate_intensity_in_per_hr(4.5)
        assert result == 4.5

    def test_zero_intensity_passes(self):
        """Zero intensity passes (non-negative)."""
        result = validate_intensity_in_per_hr(0.0)
        assert result == 0.0

    def test_negative_intensity_fails(self):
        """Negative intensity fails."""
        with pytest.raises(InvalidIDFDataError, match="cannot be negative"):
            validate_intensity_in_per_hr(-1.0)


class TestValidateDepth:
    """Tests for validate_depth_in."""

    def test_valid_depth_passes(self):
        """Valid depth passes."""
        result = validate_depth_in(2.5)
        assert result == 2.5

    def test_none_depth_passes(self):
        """None depth passes."""
        result = validate_depth_in(None)
        assert result is None

    def test_zero_depth_passes(self):
        """Zero depth passes (non-negative)."""
        result = validate_depth_in(0.0)
        assert result == 0.0

    def test_negative_depth_fails(self):
        """Negative depth fails."""
        with pytest.raises(InvalidIDFDataError, match="cannot be negative"):
            validate_depth_in(-0.5)
