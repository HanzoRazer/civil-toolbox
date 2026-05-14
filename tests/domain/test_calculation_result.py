"""Tests for CalculationResult domain entity."""

import pytest

from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.domain.base import (
    EngineeringAssumption,
    EngineeringReference,
    ValidationWarning,
)


class TestCalculationResult:
    """Tests for CalculationResult."""

    def test_creates_with_method(self):
        result = CalculationResult(method="Rational Method")
        assert result.method == "Rational Method"
        assert result.id is not None

    def test_raises_on_missing_method(self):
        with pytest.raises(ValueError, match="requires a method name"):
            CalculationResult(method="")

    def test_creates_with_entity_info(self):
        result = CalculationResult(
            method="TR-55",
            entity_id="area-123",
            entity_type="DrainageArea",
        )
        assert result.entity_id == "area-123"
        assert result.entity_type == "DrainageArea"

    def test_creates_with_inputs_and_outputs(self):
        result = CalculationResult(
            method="Rational Method",
            inputs={
                "runoff_coefficient": 0.65,
                "rainfall_intensity_in_per_hr": 4.5,
                "area_acres": 25.0,
            },
            outputs={
                "peak_flow_cfs": 73.125,
            },
        )
        assert result.inputs["runoff_coefficient"] == 0.65
        assert result.outputs["peak_flow_cfs"] == 73.125

    def test_creates_with_units(self):
        result = CalculationResult(
            method="Rational Method",
            units={
                "rainfall_intensity_in_per_hr": "in/hr",
                "area_acres": "acre",
                "peak_flow_cfs": "cfs",
            },
        )
        assert result.units["peak_flow_cfs"] == "cfs"

    def test_creates_with_metadata(self):
        result = CalculationResult(
            method="Test",
            metadata={"version": "1.0", "calculator": "civil_toolbox"},
        )
        assert result.metadata["version"] == "1.0"

    def test_add_assumption(self):
        result = CalculationResult(method="Test")
        assumption = EngineeringAssumption(description="Steady state conditions")
        result.add_assumption(assumption)
        assert len(result.assumptions) == 1
        assert result.assumptions[0].description == "Steady state conditions"

    def test_add_assumption_validates_type(self):
        result = CalculationResult(method="Test")
        with pytest.raises(TypeError, match="Expected an EngineeringAssumption"):
            result.add_assumption("not an assumption")

    def test_add_warning(self):
        result = CalculationResult(method="Test")
        warning = ValidationWarning(message="Value exceeds typical range")
        result.add_warning(warning)
        assert len(result.warnings) == 1
        assert result.warnings[0].message == "Value exceeds typical range"

    def test_add_warning_validates_type(self):
        result = CalculationResult(method="Test")
        with pytest.raises(TypeError, match="Expected a ValidationWarning"):
            result.add_warning("not a warning")

    def test_add_reference(self):
        result = CalculationResult(method="Test")
        reference = EngineeringReference(
            title="Urban Drainage Design Manual",
            source="FHWA HEC-22",
        )
        result.add_reference(reference)
        assert len(result.references) == 1
        assert result.references[0].source == "FHWA HEC-22"

    def test_add_reference_validates_type(self):
        result = CalculationResult(method="Test")
        with pytest.raises(TypeError, match="Expected an EngineeringReference"):
            result.add_reference("not a reference")

    def test_to_dict_serialization(self):
        result = CalculationResult(
            method="Rational Method",
            entity_id="area-456",
            entity_type="DrainageArea",
            inputs={"C": 0.65, "i": 4.5, "A": 25.0},
            outputs={"Q": 73.125},
            units={"Q": "cfs"},
        )
        result.add_assumption(EngineeringAssumption(description="Test assumption"))
        result.add_reference(EngineeringReference(title="HEC-22", source="FHWA"))

        data = result.to_dict()
        assert data["method"] == "Rational Method"
        assert data["entity_id"] == "area-456"
        assert data["inputs"]["C"] == 0.65
        assert data["outputs"]["Q"] == 73.125
        assert len(data["assumptions"]) == 1
        assert len(data["references"]) == 1

    def test_from_dict_deserialization(self):
        data = {
            "id": "calc-123",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
            "method": "TR-55 Runoff Depth",
            "scenario_id": "scen-456",
            "entity_id": "area-789",
            "entity_type": "DrainageArea",
            "inputs": {"precipitation": 5.0, "curve_number": 75},
            "outputs": {"runoff_depth_in": 2.5},
            "units": {"precipitation": "in", "runoff_depth_in": "in"},
            "assumptions": [
                {"description": "Type II distribution", "category": "hydrology"}
            ],
            "warnings": [
                {"message": "CN at lower limit", "field": "curve_number", "severity": "info"}
            ],
            "references": [
                {"title": "TR-55", "source": "NRCS", "year": 1986}
            ],
            "metadata": {"version": "1.0"},
        }
        result = CalculationResult.from_dict(data)
        assert result.id == "calc-123"
        assert result.method == "TR-55 Runoff Depth"
        assert result.inputs["curve_number"] == 75
        assert result.outputs["runoff_depth_in"] == 2.5
        assert len(result.assumptions) == 1
        assert len(result.warnings) == 1
        assert len(result.references) == 1
        assert result.references[0].year == 1986

    def test_round_trip_serialization(self):
        result = CalculationResult(
            method="Kirpich Time of Concentration",
            entity_id="path-100",
            entity_type="FlowPath",
            inputs={"length_ft": 2500, "slope_ft_per_ft": 0.02},
            outputs={"tc_min": 15.3},
            units={"length_ft": "ft", "tc_min": "min"},
        )
        result.add_assumption(EngineeringAssumption(
            description="Natural channel conditions",
            category="hydraulics",
        ))
        result.add_warning(ValidationWarning(
            message="Length exceeds typical Kirpich range",
            severity="warning",
        ))
        result.add_reference(EngineeringReference(
            title="Applied Hydrology",
            source="Chow et al.",
            year=1988,
        ))

        data = result.to_dict()
        restored = CalculationResult.from_dict(data)

        assert restored.id == result.id
        assert restored.method == result.method
        assert restored.entity_id == result.entity_id
        assert restored.inputs["length_ft"] == 2500
        assert restored.outputs["tc_min"] == 15.3
        assert len(restored.assumptions) == 1
        assert restored.assumptions[0].category == "hydraulics"
        assert len(restored.warnings) == 1
        assert restored.warnings[0].severity == "warning"
        assert len(restored.references) == 1
        assert restored.references[0].year == 1988

    def test_creates_auditable_result(self):
        """Integration test for a complete auditable calculation result."""
        result = CalculationResult(
            method="Rational Method",
            entity_id="basin-a",
            entity_type="DrainageArea",
            inputs={
                "runoff_coefficient": 0.65,
                "rainfall_intensity_in_per_hr": 4.5,
                "area_acres": 25.0,
            },
            outputs={
                "peak_flow_cfs": 73.125,
            },
            units={
                "runoff_coefficient": "dimensionless",
                "rainfall_intensity_in_per_hr": "in/hr",
                "area_acres": "acre",
                "peak_flow_cfs": "cfs",
            },
        )

        result.add_assumption(EngineeringAssumption(
            description="Uniform rainfall intensity over drainage area",
            category="hydrology",
        ))
        result.add_assumption(EngineeringAssumption(
            description="Peak discharge occurs when entire area is contributing",
            category="hydrology",
        ))

        result.add_reference(EngineeringReference(
            title="Urban Drainage Design Manual",
            source="FHWA HEC-22",
            year=2009,
            section="Chapter 3",
        ))

        # Verify all components are present for auditability
        assert result.method is not None
        assert result.entity_id is not None
        assert len(result.inputs) == 3
        assert len(result.outputs) == 1
        assert len(result.units) == 4
        assert len(result.assumptions) == 2
        assert len(result.references) == 1
        assert result.created_at is not None
