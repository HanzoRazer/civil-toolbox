"""Tests for infrastructure sizing models."""

import pytest

from civil_toolbox.infrastructure_sizing import (
    InfrastructureCheckResult,
    InfrastructureCheckWarning,
)


class TestInfrastructureCheckWarning:
    """Tests for InfrastructureCheckWarning."""

    def test_basic_creation(self):
        """Create a basic warning."""
        warning = InfrastructureCheckWarning(
            warning_code="TEST",
            message="Test warning message",
        )
        assert warning.warning_code == "TEST"
        assert warning.message == "Test warning message"
        assert warning.severity == "warning"

    def test_with_element_info(self):
        """Warning with element information."""
        warning = InfrastructureCheckWarning(
            warning_code="LOW_VELOCITY",
            message="Velocity too low",
            element_id="p1",
            element_name="P-1",
        )
        assert warning.element_id == "p1"
        assert warning.element_name == "P-1"

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip."""
        original = InfrastructureCheckWarning(
            warning_code="HIGH_VELOCITY",
            message="Velocity exceeds limit",
            element_id="p1",
            element_name="P-1",
            severity="error",
        )
        restored = InfrastructureCheckWarning.from_dict(original.to_dict())
        assert restored.warning_code == original.warning_code
        assert restored.message == original.message
        assert restored.element_id == original.element_id
        assert restored.severity == original.severity


class TestInfrastructureCheckResult:
    """Tests for InfrastructureCheckResult."""

    def test_basic_creation(self):
        """Create a basic result."""
        result = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=True,
        )
        assert result.element_id == "p1"
        assert result.element_name == "P-1"
        assert result.passes is True

    def test_utilization_ratio_auto_calculated(self):
        """Utilization ratio is calculated from capacity and design flow."""
        result = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=True,
            capacity_cfs=20.0,
            design_flow_cfs=10.0,
        )
        assert result.utilization_ratio == pytest.approx(0.5)

    def test_utilization_ratio_zero_design_flow(self):
        """Utilization ratio is None when design flow is zero."""
        result = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=True,
            capacity_cfs=20.0,
            design_flow_cfs=0.0,
        )
        assert result.utilization_ratio is None

    def test_is_overcapacity(self):
        """is_overcapacity property works."""
        result = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=False,
            capacity_cfs=10.0,
            design_flow_cfs=15.0,
        )
        assert result.is_overcapacity is True

    def test_add_warning(self):
        """add_warning method works."""
        result = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=True,
        )
        result.add_warning("TEST", "Test warning")
        assert len(result.warnings) == 1
        assert result.warnings[0].warning_code == "TEST"
        assert result.warnings[0].element_id == "p1"

    def test_add_assumption(self):
        """add_assumption method works."""
        result = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=True,
        )
        result.add_assumption("Full flow assumed")
        assert "Full flow assumed" in result.assumptions

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip."""
        original = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=True,
            capacity_cfs=20.0,
            design_flow_cfs=10.0,
            velocity_fps=5.0,
            method="Manning",
            metadata={"test": True},
        )
        original.add_warning("TEST", "Test warning")
        original.add_assumption("Test assumption")

        restored = InfrastructureCheckResult.from_dict(original.to_dict())
        assert restored.element_id == original.element_id
        assert restored.passes == original.passes
        assert restored.capacity_cfs == original.capacity_cfs
        assert restored.utilization_ratio == original.utilization_ratio
        assert len(restored.warnings) == 1
        assert "Test assumption" in restored.assumptions
