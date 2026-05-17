"""Tests for calculation appendix generation."""

import pytest

from civil_toolbox.reporting.appendix import (
    create_calculation_section,
    generate_calculation_appendix,
    _format_key,
    _format_method_name,
)
from civil_toolbox.reporting.models import (
    ReportType,
    SectionType,
)
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.domain.base import (
    EngineeringAssumption,
    EngineeringReference,
    ValidationWarning,
)


class TestFormatKey:
    """Tests for _format_key."""

    def test_formats_snake_case(self):
        """Formats snake_case to Title Case."""
        assert _format_key("peak_flow_cfs") == "Peak Flow Cfs"

    def test_single_word(self):
        """Formats single word."""
        assert _format_key("area") == "Area"


class TestFormatMethodName:
    """Tests for _format_method_name."""

    def test_known_methods(self):
        """Formats known method names."""
        assert _format_method_name("rational_method") == "Rational Method"
        assert _format_method_name("tr55") == "TR-55 Runoff"
        assert _format_method_name("kirpich") == "Kirpich Time of Concentration"

    def test_unknown_method(self):
        """Formats unknown method by titlecasing."""
        assert _format_method_name("custom_method") == "Custom Method"


class TestCreateCalculationSection:
    """Tests for create_calculation_section."""

    def test_creates_section_with_method_title(self):
        """Creates section with method as title."""
        result = CalculationResult(
            method="rational_method",
            entity_id="area-1",
            entity_type="DrainageArea",
            inputs={"area_acres": 25.0},
            outputs={"peak_flow_cfs": 100.0},
        )
        section = create_calculation_section(result)

        assert section.section_type == SectionType.CALCULATION
        assert section.title == "Rational Method"

    def test_includes_entity_info(self):
        """Includes entity information."""
        result = CalculationResult(
            method="tr55",
            entity_id="area-1",
            entity_type="DrainageArea",
            outputs={},
        )
        section = create_calculation_section(result)

        text_sections = [s for s in section.subsections if s.section_type == SectionType.TEXT]
        assert len(text_sections) > 0
        assert "DrainageArea" in text_sections[0].content

    def test_includes_inputs(self):
        """Includes input values."""
        result = CalculationResult(
            method="rational_method",
            inputs={"area_acres": 25.0, "runoff_coefficient": 0.85},
            units={"area_acres": "acres"},
            outputs={},
        )
        section = create_calculation_section(result)

        list_sections = [s for s in section.subsections if s.section_type == SectionType.LIST]
        input_section = [s for s in list_sections if s.title == "Inputs"]
        assert len(input_section) == 1
        assert len(input_section[0].items) == 2

    def test_includes_outputs(self):
        """Includes output values."""
        result = CalculationResult(
            method="rational_method",
            inputs={},
            outputs={"peak_flow_cfs": 100.0},
            units={"peak_flow_cfs": "cfs"},
        )
        section = create_calculation_section(result)

        list_sections = [s for s in section.subsections if s.section_type == SectionType.LIST]
        output_section = [s for s in list_sections if s.title == "Outputs"]
        assert len(output_section) == 1

    def test_includes_assumptions(self):
        """Includes assumptions."""
        result = CalculationResult(
            method="rational_method",
            outputs={},
            assumptions=[
                EngineeringAssumption(description="Steady-state conditions"),
            ],
        )
        section = create_calculation_section(result)

        assumption_sections = [
            s for s in section.subsections
            if s.section_type == SectionType.ASSUMPTIONS
        ]
        assert len(assumption_sections) == 1

    def test_includes_warnings(self):
        """Includes warnings."""
        result = CalculationResult(
            method="rational_method",
            outputs={},
            warnings=[
                ValidationWarning(message="Area exceeds limit"),
            ],
        )
        section = create_calculation_section(result)

        warning_sections = [
            s for s in section.subsections
            if s.section_type == SectionType.WARNINGS
        ]
        assert len(warning_sections) == 1

    def test_includes_references(self):
        """Includes references."""
        result = CalculationResult(
            method="rational_method",
            outputs={},
            references=[
                EngineeringReference(title="TR-55", source="NRCS", year=1986),
            ],
        )
        section = create_calculation_section(result)

        ref_sections = [
            s for s in section.subsections
            if s.section_type == SectionType.REFERENCES
        ]
        assert len(ref_sections) == 1


class TestGenerateCalculationAppendix:
    """Tests for generate_calculation_appendix."""

    def test_creates_report_with_metadata(self):
        """Creates report with correct metadata."""
        scenario = Scenario(name="Test Scenario")
        report = generate_calculation_appendix(scenario)

        assert report.metadata.report_type == ReportType.CALCULATION_APPENDIX
        assert "Test Scenario" in report.metadata.title

    def test_includes_scenario_name_in_metadata(self):
        """Includes scenario name in metadata."""
        scenario = Scenario(name="Existing")
        report = generate_calculation_appendix(scenario)

        assert "Existing" in report.metadata.scenario_names

    def test_custom_title(self):
        """Supports custom title."""
        scenario = Scenario(name="Test")
        report = generate_calculation_appendix(scenario, title="Custom Appendix")

        assert report.metadata.title == "Custom Appendix"

    def test_empty_scenario_message(self):
        """Shows message for empty scenario."""
        scenario = Scenario(name="Empty")
        report = generate_calculation_appendix(scenario)

        text_sections = [
            s for s in report.sections
            if s.section_type == SectionType.TEXT
        ]
        assert any("No calculation" in s.content for s in text_sections)

    def test_includes_calculations(self):
        """Includes calculation sections."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="tr55",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"runoff_depth_in": 2.5},
            )
        )

        report = generate_calculation_appendix(scenario)

        calc_sections = [
            s for s in report.sections
            if s.section_type == SectionType.CALCULATION
        ]
        assert len(calc_sections) == 2

    def test_aggregates_assumptions(self):
        """Aggregates assumptions from all calculations."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                outputs={},
                assumptions=[
                    EngineeringAssumption(description="Assumption A"),
                ],
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="tr55",
                outputs={},
                assumptions=[
                    EngineeringAssumption(description="Assumption B"),
                ],
            )
        )

        report = generate_calculation_appendix(scenario)

        assumption_sections = [
            s for s in report.sections
            if s.section_type == SectionType.ASSUMPTIONS
        ]
        all_assumptions = []
        for s in assumption_sections:
            all_assumptions.extend(s.items or [])

        assert "Assumption A" in all_assumptions
        assert "Assumption B" in all_assumptions

    def test_deduplicates_references(self):
        """Deduplicates references across calculations."""
        ref = EngineeringReference(title="TR-55", source="NRCS", year=1986)

        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="method1",
                outputs={},
                references=[ref],
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="method2",
                outputs={},
                references=[ref],
            )
        )

        report = generate_calculation_appendix(scenario)

        ref_sections = [
            s for s in report.sections
            if s.section_type == SectionType.REFERENCES
        ]
        assert len(ref_sections) == 1
        assert len(ref_sections[0].items) == 1

    def test_report_is_serializable(self):
        """Report can be serialized."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                outputs={"peak_flow_cfs": 100.0},
            )
        )

        report = generate_calculation_appendix(scenario)
        data = report.to_dict()

        assert data["metadata"]["report_type"] == "calculation_appendix"
        assert len(data["sections"]) > 0
