"""Tests for result builder utilities."""

import pytest

from civil_toolbox.adapters.result_builder import (
    ResultBuilder,
    RATIONAL_METHOD_REFERENCE,
    TR55_REFERENCE,
    KIRPICH_REFERENCE,
)
from civil_toolbox.domain.calculation import CalculationResult


class TestResultBuilder:
    """Tests for ResultBuilder."""

    def test_creates_minimal_result(self):
        result = ResultBuilder("test_method").build()
        assert isinstance(result, CalculationResult)
        assert result.method == "test_method"

    def test_for_entity(self):
        result = (
            ResultBuilder("test")
            .for_entity("entity-123", "DrainageArea")
            .build()
        )
        assert result.entity_id == "entity-123"
        assert result.entity_type == "DrainageArea"

    def test_with_input(self):
        result = (
            ResultBuilder("test")
            .with_input("area_acres", 25.0, "acres")
            .with_input("coefficient", 0.65)
            .build()
        )
        assert result.inputs["area_acres"] == 25.0
        assert result.inputs["coefficient"] == 0.65
        assert result.units["area_acres"] == "acres"
        assert "coefficient" not in result.units

    def test_with_output(self):
        result = (
            ResultBuilder("test")
            .with_output("peak_runoff", 50.0, "cfs")
            .build()
        )
        assert result.outputs["peak_runoff"] == 50.0
        assert result.units["peak_runoff"] == "cfs"

    def test_with_assumption(self):
        result = (
            ResultBuilder("test")
            .with_assumption("Steady-state conditions", category="hydraulic")
            .with_assumption("Uniform rainfall distribution")
            .build()
        )
        assert len(result.assumptions) == 2
        assert result.assumptions[0].description == "Steady-state conditions"
        assert result.assumptions[0].category == "hydraulic"

    def test_with_warning(self):
        result = (
            ResultBuilder("test")
            .with_warning("Area exceeds recommended limit", field="area_acres")
            .build()
        )
        assert len(result.warnings) == 1
        assert "exceeds" in result.warnings[0].message
        assert result.warnings[0].field == "area_acres"

    def test_with_reference(self):
        result = (
            ResultBuilder("test")
            .with_reference("HEC-22", "FHWA", year=2009)
            .build()
        )
        assert len(result.references) == 1
        assert result.references[0].title == "HEC-22"
        assert result.references[0].year == 2009

    def test_with_metadata(self):
        result = (
            ResultBuilder("test")
            .with_metadata("adapter_version", "1.0.0")
            .with_metadata("calculation_time_ms", 15)
            .build()
        )
        assert result.metadata["adapter_version"] == "1.0.0"
        assert result.metadata["calculation_time_ms"] == 15

    def test_fluent_interface(self):
        result = (
            ResultBuilder("rational_method")
            .for_entity("area-456", "DrainageArea")
            .with_input("runoff_coefficient", 0.65)
            .with_input("rainfall_intensity", 5.0, "in/hr")
            .with_input("area", 25.0, "acres")
            .with_output("peak_runoff", 81.25, "cfs")
            .with_assumption("Steady-state conditions")
            .with_reference("HEC-22", "FHWA", year=2009)
            .build()
        )
        assert result.method == "rational_method"
        assert result.entity_id == "area-456"
        assert len(result.inputs) == 3
        assert len(result.outputs) == 1
        assert len(result.assumptions) == 1
        assert len(result.references) == 1


class TestStandardReferences:
    """Tests for standard engineering references."""

    def test_rational_method_reference(self):
        assert RATIONAL_METHOD_REFERENCE.source == "FHWA HEC-22"
        assert RATIONAL_METHOD_REFERENCE.year == 2009

    def test_tr55_reference(self):
        assert TR55_REFERENCE.source == "NRCS TR-55"
        assert TR55_REFERENCE.year == 1986

    def test_kirpich_reference(self):
        assert KIRPICH_REFERENCE.year == 1940
        assert "Kirpich" in KIRPICH_REFERENCE.section
