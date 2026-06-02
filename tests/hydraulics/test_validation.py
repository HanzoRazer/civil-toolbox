"""Tests for hydraulics validation utilities."""

import pytest

from civil_toolbox.hydraulics.errors import (
    HydraulicAnalysisError,
    InvalidHydraulicInputError,
    MissingHydraulicDataError,
    UnsupportedHydraulicMethodError,
)
from civil_toolbox.hydraulics.validation import (
    SUPPORTED_SEVERITIES,
    SUPPORTED_SURCHARGE_STATUSES,
    require_positive,
    require_non_negative,
    require_field,
    validate_severity,
    validate_surcharge_status,
)


class TestErrorInheritance:
    """Tests for error inheritance."""

    def test_hydraulic_analysis_error_is_value_error(self):
        """HydraulicAnalysisError inherits from ValueError."""
        assert issubclass(HydraulicAnalysisError, ValueError)

    def test_invalid_input_error_is_hydraulic_error(self):
        """InvalidHydraulicInputError inherits from HydraulicAnalysisError."""
        assert issubclass(InvalidHydraulicInputError, HydraulicAnalysisError)

    def test_missing_data_error_is_hydraulic_error(self):
        """MissingHydraulicDataError inherits from HydraulicAnalysisError."""
        assert issubclass(MissingHydraulicDataError, HydraulicAnalysisError)

    def test_unsupported_method_error_is_hydraulic_error(self):
        """UnsupportedHydraulicMethodError inherits from HydraulicAnalysisError."""
        assert issubclass(UnsupportedHydraulicMethodError, HydraulicAnalysisError)


class TestRequirePositive:
    """Tests for require_positive."""

    def test_positive_value_passes(self):
        """Positive values pass."""
        assert require_positive(1.0, "x") == 1.0
        assert require_positive(0.001, "x") == 0.001

    def test_zero_raises(self):
        """Zero raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            require_positive(0, "x")

    def test_negative_raises(self):
        """Negative raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            require_positive(-1, "x")

    def test_converts_to_float(self):
        """Integer values are converted to float."""
        result = require_positive(5, "x")
        assert result == 5.0
        assert isinstance(result, float)


class TestRequireNonNegative:
    """Tests for require_non_negative."""

    def test_positive_passes(self):
        """Positive values pass."""
        assert require_non_negative(1.0, "x") == 1.0

    def test_zero_passes(self):
        """Zero is valid."""
        assert require_non_negative(0.0, "x") == 0.0

    def test_negative_raises(self):
        """Negative raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="cannot be negative"):
            require_non_negative(-0.1, "x")

    def test_converts_to_float(self):
        """Integer values are converted to float."""
        result = require_non_negative(0, "x")
        assert result == 0.0
        assert isinstance(result, float)


class TestRequireField:
    """Tests for require_field."""

    def test_non_none_passes(self):
        """Non-None values pass."""
        assert require_field(10.0, "elevation") == 10.0

    def test_string_passes(self):
        """String values pass."""
        assert require_field("test", "name") == "test"

    def test_zero_passes(self):
        """Zero is not None, so it passes."""
        assert require_field(0, "value") == 0

    def test_empty_string_passes(self):
        """Empty string is not None, so it passes."""
        assert require_field("", "name") == ""

    def test_none_raises(self):
        """None raises error."""
        with pytest.raises(MissingHydraulicDataError, match="is required"):
            require_field(None, "elevation")

    def test_none_with_entity_id(self):
        """None with entity_id includes context."""
        with pytest.raises(MissingHydraulicDataError, match="for 'pipe_001'"):
            require_field(None, "elevation", entity_id="pipe_001")


class TestValidateSeverity:
    """Tests for validate_severity."""

    def test_info_valid(self):
        """info is valid."""
        assert validate_severity("info") == "info"

    def test_warning_valid(self):
        """warning is valid."""
        assert validate_severity("warning") == "warning"

    def test_error_valid(self):
        """error is valid."""
        assert validate_severity("error") == "error"

    def test_all_severities_valid(self):
        """All supported severities pass."""
        for sev in SUPPORTED_SEVERITIES:
            assert validate_severity(sev) == sev

    def test_unsupported_severity_fails(self):
        """Unsupported severity raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be one of"):
            validate_severity("critical")


class TestValidateSurchargeStatus:
    """Tests for validate_surcharge_status."""

    def test_free_surface_valid(self):
        """free_surface is valid."""
        assert validate_surcharge_status("free_surface") == "free_surface"

    def test_pressurized_valid(self):
        """pressurized is valid."""
        assert validate_surcharge_status("pressurized") == "pressurized"

    def test_surcharged_above_crown_valid(self):
        """surcharged_above_crown is valid."""
        assert validate_surcharge_status("surcharged_above_crown") == "surcharged_above_crown"

    def test_surcharged_above_rim_valid(self):
        """surcharged_above_rim is valid."""
        assert validate_surcharge_status("surcharged_above_rim") == "surcharged_above_rim"

    def test_unknown_valid(self):
        """unknown is valid."""
        assert validate_surcharge_status("unknown") == "unknown"

    def test_all_statuses_valid(self):
        """All supported statuses pass."""
        for status in SUPPORTED_SURCHARGE_STATUSES:
            assert validate_surcharge_status(status) == status

    def test_unsupported_status_fails(self):
        """Unsupported status raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be one of"):
            validate_surcharge_status("full_pipe")


class TestSupportedConstants:
    """Tests for constant sets."""

    def test_severities_content(self):
        """Expected severities are defined."""
        assert SUPPORTED_SEVERITIES == {"info", "warning", "error"}

    def test_surcharge_statuses_content(self):
        """Expected surcharge statuses are defined."""
        expected = {
            "free_surface",
            "pressurized",
            "surcharged_above_crown",
            "surcharged_above_rim",
            "unknown",
        }
        assert SUPPORTED_SURCHARGE_STATUSES == expected
