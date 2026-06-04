"""Tests for inlet capacity validation utilities."""

import pytest

from civil_toolbox.inlets.errors import (
    InletCapacityError,
    InvalidInletInputError,
    MissingInletDataError,
)
from civil_toolbox.inlets.validation import (
    require_field,
    require_non_negative,
    require_positive,
    validate_status,
)


class TestRequirePositive:
    def test_accepts_positive(self):
        assert require_positive(2.0, "x") == 2.0

    @pytest.mark.parametrize("value", [0, -1])
    def test_rejects_non_positive(self, value):
        with pytest.raises(InvalidInletInputError, match="must be positive"):
            require_positive(value, "x")


class TestRequireNonNegative:
    def test_accepts_zero(self):
        assert require_non_negative(0, "x") == 0.0

    def test_rejects_negative(self):
        with pytest.raises(InvalidInletInputError, match="cannot be negative"):
            require_non_negative(-1, "x")


class TestRequireField:
    def test_accepts_value(self):
        assert require_field(3, "x") == 3

    def test_rejects_none(self):
        with pytest.raises(MissingInletDataError, match="is required"):
            require_field(None, "x")

    def test_entity_context(self):
        with pytest.raises(MissingInletDataError, match="for 'i1'"):
            require_field(None, "x", entity_id="i1")


class TestValidateStatus:
    @pytest.mark.parametrize("status", ["pass", "fail", "warning", "not_evaluated"])
    def test_accepts_supported(self, status):
        assert validate_status(status) == status

    def test_rejects_unsupported(self):
        with pytest.raises(InletCapacityError, match="status must be one of"):
            validate_status("passes")
