"""Tests for infrastructure validation utilities."""

import pytest

from civil_toolbox.infrastructure.errors import InvalidInfrastructureError
from civil_toolbox.infrastructure.validation import (
    validate_positive,
    validate_non_negative,
    validate_mannings_n,
    validate_slope,
    validate_pipe_shape,
    validate_inlet_type,
    validate_channel_shape,
    validate_outlet_type,
)


class TestValidatePositive:
    """Tests for validate_positive."""

    def test_valid_positive(self):
        """Positive values pass."""
        assert validate_positive(1.0, "x") == 1.0
        assert validate_positive(0.001, "x") == 0.001

    def test_zero_raises(self):
        """Zero raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be positive"):
            validate_positive(0, "x")

    def test_negative_raises(self):
        """Negative raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be positive"):
            validate_positive(-1, "x")


class TestValidateNonNegative:
    """Tests for validate_non_negative."""

    def test_positive_valid(self):
        """Positive values pass."""
        assert validate_non_negative(1.0, "x") == 1.0

    def test_zero_valid(self):
        """Zero is valid."""
        assert validate_non_negative(0.0, "x") == 0.0

    def test_negative_raises(self):
        """Negative raises error."""
        with pytest.raises(InvalidInfrastructureError, match="cannot be negative"):
            validate_non_negative(-0.1, "x")


class TestValidateManningsN:
    """Tests for validate_mannings_n."""

    def test_typical_values(self):
        """Typical Manning's n values pass."""
        assert validate_mannings_n(0.013, "n") == 0.013
        assert validate_mannings_n(0.035, "n") == 0.035

    def test_zero_raises(self):
        """Zero raises error."""
        with pytest.raises(InvalidInfrastructureError, match="between 0 and 0.5"):
            validate_mannings_n(0, "n")

    def test_too_high_raises(self):
        """Value above 0.5 raises error."""
        with pytest.raises(InvalidInfrastructureError, match="between 0 and 0.5"):
            validate_mannings_n(0.6, "n")


class TestValidateSlope:
    """Tests for validate_slope."""

    def test_positive_slope(self):
        """Positive slope passes."""
        assert validate_slope(0.01, "s") == 0.01

    def test_zero_slope(self):
        """Zero slope is valid."""
        assert validate_slope(0.0, "s") == 0.0

    def test_negative_raises(self):
        """Negative slope raises error."""
        with pytest.raises(InvalidInfrastructureError, match="cannot be negative"):
            validate_slope(-0.01, "s")


class TestValidatePipeShape:
    """Tests for validate_pipe_shape."""

    def test_valid_shapes(self):
        """Valid shapes return normalized."""
        assert validate_pipe_shape("circular") == "circular"
        assert validate_pipe_shape("box") == "box"
        assert validate_pipe_shape("arch") == "arch"
        assert validate_pipe_shape("elliptical") == "elliptical"

    def test_case_insensitive(self):
        """Shapes are case insensitive."""
        assert validate_pipe_shape("CIRCULAR") == "circular"
        assert validate_pipe_shape("Box") == "box"

    def test_whitespace_stripped(self):
        """Whitespace is stripped."""
        assert validate_pipe_shape("  circular  ") == "circular"

    def test_invalid_raises(self):
        """Invalid shape raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be one of"):
            validate_pipe_shape("square")


class TestValidateInletType:
    """Tests for validate_inlet_type."""

    def test_valid_types(self):
        """Valid types return normalized."""
        assert validate_inlet_type("grate") == "grate"
        assert validate_inlet_type("curb_opening") == "curb_opening"
        assert validate_inlet_type("combination") == "combination"
        assert validate_inlet_type("slotted") == "slotted"

    def test_invalid_raises(self):
        """Invalid type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be one of"):
            validate_inlet_type("unknown")


class TestValidateChannelShape:
    """Tests for validate_channel_shape."""

    def test_valid_shapes(self):
        """Valid shapes return normalized."""
        assert validate_channel_shape("rectangular") == "rectangular"
        assert validate_channel_shape("trapezoidal") == "trapezoidal"
        assert validate_channel_shape("triangular") == "triangular"
        assert validate_channel_shape("parabolic") == "parabolic"

    def test_invalid_raises(self):
        """Invalid shape raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be one of"):
            validate_channel_shape("circular")


class TestValidateOutletType:
    """Tests for validate_outlet_type."""

    def test_valid_types(self):
        """Valid types return normalized."""
        assert validate_outlet_type("orifice") == "orifice"
        assert validate_outlet_type("weir") == "weir"
        assert validate_outlet_type("riser") == "riser"
        assert validate_outlet_type("culvert") == "culvert"
        assert validate_outlet_type("combined") == "combined"

    def test_invalid_raises(self):
        """Invalid type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be one of"):
            validate_outlet_type("unknown")
