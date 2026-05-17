"""Calculation appendix generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.models import (
    Report,
    ReportMetadata,
    ReportSection,
    ReportTable,
    ReportType,
    SectionType,
)
from civil_toolbox.reporting.formatters import (
    format_value_with_unit,
    format_date,
)
from civil_toolbox.reporting.tables import (
    create_key_value_table,
)
from civil_toolbox.reporting.sections import (
    create_heading,
    create_text,
    create_list,
    create_table_section,
    create_assumptions_section,
    create_warnings_section,
    create_references_section,
)

if TYPE_CHECKING:
    from civil_toolbox.domain.scenario import Scenario
    from civil_toolbox.domain.calculation import CalculationResult


def create_calculation_section(result: CalculationResult) -> ReportSection:
    """Create a section for a single calculation result.

    Args:
        result: The calculation result.

    Returns:
        ReportSection with calculation details.
    """
    subsections = []

    entity_info = f"Entity: {result.entity_type or 'Unknown'}"
    if result.entity_id:
        entity_info += f" ({result.entity_id})"
    subsections.append(create_text(entity_info))

    if result.inputs:
        input_items = []
        for key, value in result.inputs.items():
            unit = result.units.get(key, "")
            if isinstance(value, (int, float)):
                formatted = format_value_with_unit(value, unit) if unit else str(value)
            else:
                formatted = str(value)
            input_items.append(f"{_format_key(key)}: {formatted}")
        subsections.append(create_list(input_items, title="Inputs"))

    if result.outputs:
        output_items = []
        for key, value in result.outputs.items():
            unit = result.units.get(key, "")
            if isinstance(value, (int, float)):
                formatted = format_value_with_unit(value, unit) if unit else str(value)
            else:
                formatted = str(value)
            output_items.append(f"{_format_key(key)}: {formatted}")
        subsections.append(create_list(output_items, title="Outputs"))

    if result.assumptions:
        assumption_texts = [a.description for a in result.assumptions]
        subsections.append(create_assumptions_section(assumption_texts))

    if result.warnings:
        warning_texts = [w.message for w in result.warnings]
        subsections.append(create_warnings_section(warning_texts))

    if result.references:
        ref_dicts = []
        for ref in result.references:
            ref_dicts.append({
                "title": ref.title,
                "source": ref.source,
                "year": str(ref.year) if ref.year else None,
            })
        subsections.append(create_references_section(ref_dicts))

    return ReportSection(
        section_type=SectionType.CALCULATION,
        title=_format_method_name(result.method),
        level=3,
        subsections=subsections,
        metadata={"method": result.method, "entity_id": result.entity_id},
    )


def generate_calculation_appendix(
    scenario: Scenario,
    title: str | None = None,
    include_timestamp: bool = True,
) -> Report:
    """Generate a calculation appendix for a scenario.

    Args:
        scenario: The scenario containing calculations.
        title: Optional custom title.
        include_timestamp: Whether to include generation timestamp.

    Returns:
        Report containing all calculation details.
    """
    report_title = title or f"Calculation Appendix: {scenario.name}"

    metadata = ReportMetadata(
        title=report_title,
        report_type=ReportType.CALCULATION_APPENDIX,
        scenario_names=[scenario.name],
    )

    report = Report(metadata=metadata)

    report.add_section(create_heading(report_title, level=1))

    summary_items = [
        ("Scenario", scenario.name),
        ("Total Calculations", str(len(scenario.calculation_results))),
    ]
    if include_timestamp:
        summary_items.append(("Generated", format_date(metadata.generated_at)))

    summary_table = create_key_value_table(summary_items)
    report.add_section(create_table_section(summary_table))

    if not scenario.calculation_results:
        report.add_section(
            create_text("No calculation results available for this scenario.")
        )
        return report

    report.add_section(create_heading("Calculations", level=2))

    for result in scenario.calculation_results:
        report.add_section(create_calculation_section(result))

    all_assumptions = set()
    all_references = []
    seen_refs = set()

    for result in scenario.calculation_results:
        for assumption in result.assumptions:
            all_assumptions.add(assumption.description)
        for ref in result.references:
            ref_key = (ref.title, ref.source)
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                all_references.append({
                    "title": ref.title,
                    "source": ref.source,
                    "year": str(ref.year) if ref.year else None,
                })

    if all_assumptions:
        report.add_section(create_heading("All Assumptions", level=2))
        report.add_section(create_assumptions_section(sorted(all_assumptions)))

    if all_references:
        report.add_section(create_heading("References", level=2))
        report.add_section(create_references_section(all_references))

    return report


def _format_key(key: str) -> str:
    """Format a key string for display."""
    return key.replace("_", " ").title()


def _format_method_name(method: str) -> str:
    """Format a method name for display."""
    method_names = {
        "rational_method": "Rational Method",
        "tr55": "TR-55 Runoff",
        "kirpich": "Kirpich Time of Concentration",
        "kerby": "Kerby Time of Concentration",
        "kinematic_wave": "Kinematic Wave Sheet Flow",
        "nrcs_lag": "NRCS Lag Method",
    }
    return method_names.get(method, method.replace("_", " ").title())
