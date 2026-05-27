"""Tests for design criteria validation utilities."""

import pytest

from civil_toolbox.design_criteria.errors import (
    DesignCriteriaError,
    InvalidDesignCriteriaError,
    DesignCriteriaLookupError,
    CriteriaNotFoundError,
)
from civil_toolbox.design_criteria.validation import (
    VALID_SOIL_GROUPS,
    validate_runoff_coefficient,
    validate_curve_number,
    validate_soil_group,
    validate_return_period,
    validate_duration_minutes,
)


class TestDesignCriteriaErrors:
    """Tests for design criteria error hierarchy."""

    def test_invalid_design_criteria_inherits_base(self):
        """InvalidDesignCriteriaError inherits from DesignCriteriaError."""
        error = InvalidDesignCriteriaError("test")
        assert isinstance(error, DesignCriteriaError)
        assert isinstance(error, ValueError)

    def test_design_criteria_lookup_inherits_base(self):
        """DesignCriteriaLookupError inherits from DesignCriteriaError."""
        error = DesignCriteriaLookupError("test")
        assert isinstance(error, DesignCriteriaError)

    def test_criteria_not_found_inherits_base(self):
        """CriteriaNotFoundError inherits from DesignCriteriaError."""
        error = CriteriaNotFoundError("test")
        assert isinstance(error, DesignCriteriaError)

    def test_errors_include_message(self):
        """Errors include useful messages."""
        error = InvalidDesignCriteriaError("specific issue")
        assert "specific issue" in str(error)


class TestValidSoilGroups:
    """Tests for VALID_SOIL_GROUPS constant."""

    def test_contains_expected_groups(self):
        """VALID_SOIL_GROUPS contains A, B, C, D."""
        assert VALID_SOIL_GROUPS == {"A", "B", "C", "D"}

    def test_is_frozen(self):
        """VALID_SOIL_GROUPS is immutable."""
        assert isinstance(VALID_SOIL_GROUPS, frozenset)


class TestValidateRunoffCoefficient:
    """Tests for validate_runoff_coefficient."""

    def test_valid_coefficient(self):
        """Valid coefficient in range returns float."""
        assert validate_runoff_coefficient(0.5, "c") == 0.5

    def test_zero_is_valid(self):
        """Zero is valid lower bound."""
        assert validate_runoff_coefficient(0.0, "c") == 0.0

    def test_one_is_valid(self):
        """One is valid upper bound."""
        assert validate_runoff_coefficient(1.0, "c") == 1.0

    def test_negative_raises(self):
        """Negative coefficient raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="between 0 and 1"):
            validate_runoff_coefficient(-0.1, "c")

    def test_above_one_raises(self):
        """Coefficient above 1 raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="between 0 and 1"):
            validate_runoff_coefficient(1.1, "c")

    def test_field_name_in_error(self):
        """Field name appears in error message."""
        with pytest.raises(InvalidDesignCriteriaError, match="my_field"):
            validate_runoff_coefficient(-0.5, "my_field")


class TestValidateCurveNumber:
    """Tests for validate_curve_number."""

    def test_valid_curve_number(self):
        """Valid curve number in range returns int."""
        assert validate_curve_number(75, "cn") == 75

    def test_one_is_valid_lower_bound(self):
        """One is valid lower bound."""
        assert validate_curve_number(1, "cn") == 1

    def test_zero_raises(self):
        """Zero raises error (CN must be > 0)."""
        with pytest.raises(InvalidDesignCriteriaError, match="between 1 and 100"):
            validate_curve_number(0, "cn")

    def test_one_hundred_is_valid(self):
        """100 is valid upper bound."""
        assert validate_curve_number(100, "cn") == 100

    def test_negative_raises(self):
        """Negative curve number raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="between 1 and 100"):
            validate_curve_number(-1, "cn")

    def test_above_hundred_raises(self):
        """Curve number above 100 raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="between 1 and 100"):
            validate_curve_number(101, "cn")

    def test_float_raises(self):
        """Float raises error (must be int)."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be an integer"):
            validate_curve_number(75.5, "cn")  # type: ignore

    def test_field_name_in_error(self):
        """Field name appears in error message."""
        with pytest.raises(InvalidDesignCriteriaError, match="my_cn"):
            validate_curve_number(-1, "my_cn")


class TestValidateSoilGroup:
    """Tests for validate_soil_group."""

    def test_valid_groups(self):
        """Valid soil groups A, B, C, D return uppercase."""
        assert validate_soil_group("A", "sg") == "A"
        assert validate_soil_group("B", "sg") == "B"
        assert validate_soil_group("C", "sg") == "C"
        assert validate_soil_group("D", "sg") == "D"

    def test_lowercase_normalized(self):
        """Lowercase is normalized to uppercase."""
        assert validate_soil_group("a", "sg") == "A"
        assert validate_soil_group("b", "sg") == "B"
        assert validate_soil_group("c", "sg") == "C"
        assert validate_soil_group("d", "sg") == "D"

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        assert validate_soil_group(" A ", "sg") == "A"
        assert validate_soil_group("  b  ", "sg") == "B"

    def test_invalid_group_raises(self):
        """Invalid soil group raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be one of"):
            validate_soil_group("E", "sg")

    def test_error_shows_available(self):
        """Error message shows valid options."""
        with pytest.raises(InvalidDesignCriteriaError, match=r"\['A', 'B', 'C', 'D'\]"):
            validate_soil_group("X", "sg")


class TestValidateReturnPeriod:
    """Tests for validate_return_period."""

    def test_valid_return_period(self):
        """Valid positive integer returns unchanged."""
        assert validate_return_period(10, "rp") == 10
        assert validate_return_period(100, "rp") == 100

    def test_one_is_valid(self):
        """Return period of 1 year is valid."""
        assert validate_return_period(1, "rp") == 1

    def test_zero_raises(self):
        """Zero return period raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be positive"):
            validate_return_period(0, "rp")

    def test_negative_raises(self):
        """Negative return period raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be positive"):
            validate_return_period(-5, "rp")

    def test_float_raises(self):
        """Float raises error (must be int)."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be an integer"):
            validate_return_period(10.5, "rp")  # type: ignore


class TestValidateDurationMinutes:
    """Tests for validate_duration_minutes."""

    def test_valid_duration(self):
        """Valid positive duration returns float."""
        assert validate_duration_minutes(15.0, "d") == 15.0
        assert validate_duration_minutes(1440.0, "d") == 1440.0

    def test_small_positive_is_valid(self):
        """Small positive duration is valid."""
        assert validate_duration_minutes(0.1, "d") == 0.1

    def test_zero_raises(self):
        """Zero duration raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be positive"):
            validate_duration_minutes(0.0, "d")

    def test_negative_raises(self):
        """Negative duration raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be positive"):
            validate_duration_minutes(-5.0, "d")

    def test_integer_converted_to_float(self):
        """Integer input is converted to float."""
        result = validate_duration_minutes(60, "d")
        assert result == 60.0
        assert isinstance(result, float)
