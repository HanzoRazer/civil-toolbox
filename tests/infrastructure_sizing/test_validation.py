"""Tests for infrastructure sizing validation utilities."""

import pytest

from civil_toolbox.infrastructure_sizing import (
    validate_positive_flow,
    validate_positive_storage,
    validate_mannings_n,
    validate_positive_slope,
    validate_positive_dimension,
)
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


class TestValidatePositiveFlow:
    """Tests for validate_positive_flow."""

    def test_positive_flow(self):
        """Positive flow passes."""
        assert validate_positive_flow(10.0, "flow") == 10.0

    def test_zero_flow(self):
        """Zero flow is valid."""
        assert validate_positive_flow(0.0, "flow") == 0.0

    def test_negative_flow_raises(self):
        """Negative flow raises error."""
        with pytest.raises(InvalidSizingInputError, match="cannot be negative"):
            validate_positive_flow(-5.0, "design_flow")


class TestValidatePositiveStorage:
    """Tests for validate_positive_storage."""

    def test_positive_storage(self):
        """Positive storage passes."""
        assert validate_positive_storage(50000.0, "storage") == 50000.0

    def test_zero_storage(self):
        """Zero storage is valid."""
        assert validate_positive_storage(0.0, "storage") == 0.0

    def test_negative_storage_raises(self):
        """Negative storage raises error."""
        with pytest.raises(InvalidSizingInputError, match="cannot be negative"):
            validate_positive_storage(-1000.0, "required_storage")


class TestValidateManningsN:
    """Tests for validate_mannings_n."""

    def test_typical_values(self):
        """Typical Manning's n values pass."""
        assert validate_mannings_n(0.013, "n") == 0.013
        assert validate_mannings_n(0.035, "n") == 0.035
        assert validate_mannings_n(0.1, "n") == 0.1

    def test_zero_raises(self):
        """Zero raises error."""
        with pytest.raises(InvalidSizingInputError, match="between 0 and 0.5"):
            validate_mannings_n(0.0, "mannings_n")

    def test_too_high_raises(self):
        """Value above 0.5 raises error."""
        with pytest.raises(InvalidSizingInputError, match="between 0 and 0.5"):
            validate_mannings_n(0.6, "mannings_n")


class TestValidatePositiveSlope:
    """Tests for validate_positive_slope."""

    def test_positive_slope(self):
        """Positive slope passes."""
        assert validate_positive_slope(0.01, "slope") == 0.01

    def test_zero_raises(self):
        """Zero slope raises error."""
        with pytest.raises(InvalidSizingInputError, match="must be positive"):
            validate_positive_slope(0.0, "slope")

    def test_negative_raises(self):
        """Negative slope raises error."""
        with pytest.raises(InvalidSizingInputError, match="must be positive"):
            validate_positive_slope(-0.01, "slope")


class TestValidatePositiveDimension:
    """Tests for validate_positive_dimension."""

    def test_positive_dimension(self):
        """Positive dimension passes."""
        assert validate_positive_dimension(18.0, "diameter") == 18.0

    def test_zero_raises(self):
        """Zero raises error."""
        with pytest.raises(InvalidSizingInputError, match="must be positive"):
            validate_positive_dimension(0.0, "width")

    def test_negative_raises(self):
        """Negative raises error."""
        with pytest.raises(InvalidSizingInputError, match="must be positive"):
            validate_positive_dimension(-5.0, "height")
