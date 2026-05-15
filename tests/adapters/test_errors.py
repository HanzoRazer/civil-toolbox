"""Tests for adapter error types."""

import pytest

from civil_toolbox.adapters.errors import (
    AdapterError,
    MissingFieldError,
    IncompatibleEntityError,
    CalculationNotApplicableError,
)


class TestAdapterErrorInheritance:
    """Test error type inheritance."""

    def test_missing_field_inherits_from_adapter_error(self):
        assert issubclass(MissingFieldError, AdapterError)

    def test_incompatible_entity_inherits_from_adapter_error(self):
        assert issubclass(IncompatibleEntityError, AdapterError)

    def test_not_applicable_inherits_from_adapter_error(self):
        assert issubclass(CalculationNotApplicableError, AdapterError)

    def test_adapter_error_inherits_from_exception(self):
        assert issubclass(AdapterError, Exception)


class TestMissingFieldError:
    """Tests for MissingFieldError."""

    def test_creates_with_message(self):
        error = MissingFieldError("area_acres is required")
        assert str(error) == "area_acres is required"

    def test_creates_with_entity_info(self):
        error = MissingFieldError(
            "Missing runoff_coefficient",
            entity_type="DrainageArea",
            entity_id="area-123",
            field_name="runoff_coefficient",
        )
        assert error.entity_type == "DrainageArea"
        assert error.entity_id == "area-123"
        assert error.field_name == "runoff_coefficient"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(MissingFieldError) as exc_info:
            raise MissingFieldError(
                "Missing curve_number",
                field_name="curve_number",
            )
        assert exc_info.value.field_name == "curve_number"


class TestIncompatibleEntityError:
    """Tests for IncompatibleEntityError."""

    def test_creates_with_message(self):
        error = IncompatibleEntityError("Cannot combine these entities")
        assert str(error) == "Cannot combine these entities"

    def test_creates_with_reason(self):
        error = IncompatibleEntityError(
            "StormEvent missing rainfall_intensity_in_per_hr",
            reason="Rational Method requires rainfall intensity",
        )
        assert error.reason == "Rational Method requires rainfall intensity"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(IncompatibleEntityError) as exc_info:
            raise IncompatibleEntityError("Mismatch", reason="test")
        assert exc_info.value.reason == "test"


class TestCalculationNotApplicableError:
    """Tests for CalculationNotApplicableError."""

    def test_creates_with_message(self):
        error = CalculationNotApplicableError("Method not applicable")
        assert str(error) == "Method not applicable"

    def test_creates_with_method_and_limit(self):
        error = CalculationNotApplicableError(
            "Drainage area exceeds Rational Method limit",
            method="rational_method",
            limit_exceeded="area > 200 acres",
        )
        assert error.method == "rational_method"
        assert error.limit_exceeded == "area > 200 acres"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(CalculationNotApplicableError) as exc_info:
            raise CalculationNotApplicableError("Limit exceeded", method="kirpich")
        assert exc_info.value.method == "kirpich"
