"""Tests for culvert validation utilities."""

import pytest

from civil_toolbox.culverts.errors import (
    CulvertAnalysisError,
    InvalidCulvertInputError,
)
from civil_toolbox.culverts.validation import (
    require_field,
    require_non_negative,
    require_positive,
    validate_control_status,
    validate_governing_control,
    validate_severity,
)


class TestRequirePositive:
    def test_accepts_positive(self):
        assert require_positive(3.0, "x") == 3.0

    def test_returns_float(self):
        assert isinstance(require_positive(2, "x"), float)

    @pytest.mark.parametrize("value", [0, -1, -0.5])
    def test_rejects_non_positive(self, value):
        with pytest.raises(InvalidCulvertInputError, match="must be positive"):
            require_positive(value, "x")


class TestRequireNonNegative:
    def test_accepts_zero(self):
        assert require_non_negative(0, "x") == 0.0

    def test_rejects_negative(self):
        with pytest.raises(InvalidCulvertInputError, match="cannot be negative"):
            require_non_negative(-1, "x")


class TestRequireField:
    def test_accepts_value(self):
        assert require_field(5, "x") == 5

    def test_rejects_none(self):
        with pytest.raises(InvalidCulvertInputError, match="is required"):
            require_field(None, "x")

    def test_includes_entity_context(self):
        with pytest.raises(InvalidCulvertInputError, match="for 'c1'"):
            require_field(None, "x", entity_id="c1")


class TestValidateSeverity:
    @pytest.mark.parametrize("sev", ["info", "warning", "error"])
    def test_accepts_supported(self, sev):
        assert validate_severity(sev) == sev

    def test_rejects_unsupported(self):
        with pytest.raises(CulvertAnalysisError, match="severity must be one of"):
            validate_severity("critical")


class TestValidateControlStatus:
    @pytest.mark.parametrize(
        "status", ["unknown", "passes", "exceeds", "not_evaluated"]
    )
    def test_accepts_supported(self, status):
        assert validate_control_status(status) == status

    def test_rejects_unsupported(self):
        with pytest.raises(CulvertAnalysisError, match="control status must be one of"):
            validate_control_status("fails")


class TestValidateGoverningControl:
    @pytest.mark.parametrize("control", ["inlet", "outlet", "unknown"])
    def test_accepts_supported(self, control):
        assert validate_governing_control(control) == control

    def test_rejects_unsupported(self):
        with pytest.raises(CulvertAnalysisError, match="governing control must be one of"):
            validate_governing_control("both")
