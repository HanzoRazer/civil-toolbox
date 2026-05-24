"""Template-based report builders.

Builds structured Report objects from templates and context.
Reuses existing section creation functions from the reporting engine.

Example:
    >>> from civil_toolbox.reporting.template_builders import build_report_from_template
    >>> from civil_toolbox.reporting.builtins import get_builtin_templates
    >>> template = get_builtin_templates()[0]
    >>> report = build_report_from_template(template, context)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from civil_toolbox.reporting.models import (
    Report,
    ReportMetadata,
    ReportSection,
    ReportType,
    SectionType,
)
from civil_toolbox.reporting.report_templates import ReportTemplate, SectionTemplate
from civil_toolbox.reporting.template_context import ReportTemplateContext
from civil_toolbox.reporting.template_validation import (
    validate_template,
    validate_template_context,
    can_build_section,
    ContextValidationError,
)
from civil_toolbox.reporting.sections import (
    create_heading,
    create_text,
    create_project_metadata_section,
    create_scenario_summary_section,
    create_comparison_summary_section,
    create_comparison_totals_section,
    create_assumptions_section,
    create_warnings_section,
    create_references_section,
)
from civil_toolbox.reporting.appendix import create_calculation_section
from civil_toolbox.reporting.tables import create_key_value_table
from civil_toolbox.reporting.formatters import format_date
from civil_toolbox.reporting.infrastructure_sections import (
    build_infrastructure_summary_section,
    build_infrastructure_schedule_section,
    build_pipe_schedule_section,
    build_inlet_schedule_section,
    build_detention_schedule_section,
    build_infrastructure_check_summary_section,
    build_infrastructure_warnings_section,
    build_infrastructure_assumptions_section,
)

if TYPE_CHECKING:
    pass


class TemplateBuildError(Exception):
    """Raised when report building from template fails."""

    def __init__(self, message: str, section_id: str | None = None):
        self.section_id = section_id
        super().__init__(message)


def _build_project_summary_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build project summary sections."""
    if not context.project:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    sections.append(create_project_metadata_section(context.project))
    return sections


def _build_scenario_summary_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build scenario summary sections."""
    if not context.scenario:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    sections.append(create_scenario_summary_section(context.scenario))
    return sections


def _build_comparison_summary_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build comparison summary sections."""
    if not context.comparison:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    sections.append(create_comparison_summary_section(context.comparison))
    return sections


def _build_comparison_table_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build comparison table sections."""
    if not context.comparison:
        return []

    from civil_toolbox.comparison.models import ComparisonMetric
    from civil_toolbox.reporting.tables import create_entity_summary_table
    from civil_toolbox.reporting.sections import create_table_section
    from civil_toolbox.reporting.formatters import format_delta, format_metric_name

    sections = []
    sections.append(create_heading(section.title, level=2))

    if context.comparison.entity_comparisons:
        entities_data = []
        for entity in context.comparison.entity_comparisons:
            row = {"name": entity.entity_name}
            for metric, result in entity.metrics.items():
                col_name = metric.value.replace("_", " ").title()
                if result.delta is not None:
                    row[col_name.lower().replace(" ", "_")] = format_delta(
                        result.delta, result.unit, precision=1
                    )
                else:
                    row[col_name.lower().replace(" ", "_")] = "—"
            entities_data.append(row)

        if entities_data:
            columns = [("name", "Entity")]
            for metric in ComparisonMetric:
                col_key = metric.value.replace("_", " ").title().lower().replace(" ", "_")
                col_header = format_metric_name(metric.value)
                columns.append((col_key, col_header))

            table = create_entity_summary_table(entities_data, columns)
            table.title = "Delta by Entity"
            sections.append(create_table_section(table))

    return sections


def _build_comparison_totals_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build comparison totals sections."""
    if not context.comparison or not context.comparison.totals:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    sections.append(create_comparison_totals_section(context.comparison))
    return sections


def _build_calculation_summary_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build calculation summary sections."""
    if not context.scenario:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))

    summary_items = [
        ("Scenario", context.scenario.name),
        ("Total Calculations", str(len(context.scenario.calculation_results))),
    ]

    table = create_key_value_table(summary_items)
    sections.append(ReportSection(
        section_type=SectionType.TABLE,
        table=table,
    ))

    return sections


def _build_calculation_appendix_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build calculation appendix sections."""
    if not context.scenario:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))

    if not context.scenario.calculation_results:
        sections.append(
            create_text("No calculation results available for this scenario.")
        )
        return sections

    for result in context.scenario.calculation_results:
        sections.append(create_calculation_section(result))

    return sections


def _build_assumptions_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build assumptions sections."""
    assumptions = context.get_all_assumptions()

    if not assumptions and not section.include_when_empty:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    if assumptions:
        sections.append(create_assumptions_section(assumptions))
    else:
        sections.append(create_text("No assumptions recorded."))

    return sections


def _build_warnings_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build warnings sections."""
    warnings = context.get_all_warnings()

    if not warnings and not section.include_when_empty:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    if warnings:
        sections.append(create_warnings_section(warnings))
    else:
        sections.append(create_text("No warnings recorded."))

    return sections


def _build_references_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build references sections."""
    references = context.get_all_references()

    if not references and not section.include_when_empty:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    if references:
        sections.append(create_references_section(references))
    else:
        sections.append(create_text("No references recorded."))

    return sections


def _build_custom_text_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build custom text sections."""
    custom_text = context.get_custom_section(section.id)

    if not custom_text and not section.include_when_empty:
        return []

    sections = []
    sections.append(create_heading(section.title, level=2))
    if custom_text:
        sections.append(create_text(custom_text))
    else:
        sections.append(create_text(""))

    return sections


def _build_heading_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build heading-only sections."""
    level = section.metadata.get("level", 2)
    return [create_heading(section.title, level=level)]


def _build_infrastructure_summary_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build infrastructure summary sections."""
    if not context.infrastructure_network:
        return []
    return build_infrastructure_summary_section(
        context.infrastructure_network,
        title=section.title,
    )


def _build_infrastructure_schedule_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build infrastructure schedule sections."""
    if not context.infrastructure_network:
        return []
    return build_infrastructure_schedule_section(
        context.infrastructure_network,
        title=section.title,
    )


def _build_pipe_schedule_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build pipe schedule sections."""
    if not context.infrastructure_network:
        return []
    return build_pipe_schedule_section(
        context.infrastructure_network,
        title=section.title,
    )


def _build_inlet_schedule_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build inlet schedule sections."""
    if not context.infrastructure_network:
        return []
    return build_inlet_schedule_section(
        context.infrastructure_network,
        title=section.title,
    )


def _build_detention_schedule_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build detention schedule sections."""
    if not context.infrastructure_network:
        return []
    return build_detention_schedule_section(
        context.infrastructure_network,
        title=section.title,
    )


def _build_infrastructure_check_summary_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build infrastructure check summary sections."""
    if not context.infrastructure_check_results:
        return []
    return build_infrastructure_check_summary_section(
        context.infrastructure_check_results,
        title=section.title,
    )


def _build_infrastructure_warnings_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build infrastructure warnings sections."""
    if not context.infrastructure_check_results:
        return []
    return build_infrastructure_warnings_section(
        context.infrastructure_check_results,
        title=section.title,
    )


def _build_infrastructure_assumptions_section_wrapper(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build infrastructure assumptions sections."""
    if not context.infrastructure_check_results:
        return []
    return build_infrastructure_assumptions_section(
        context.infrastructure_check_results,
        title=section.title,
    )


def _build_storm_sensitivity_table_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> list[ReportSection]:
    """Build storm sensitivity table sections."""
    if not context.storm_sensitivity:
        return []

    from civil_toolbox.comparison.models import ComparisonMetric
    from civil_toolbox.reporting.tables import create_entity_summary_table
    from civil_toolbox.reporting.sections import create_table_section
    from civil_toolbox.reporting.formatters import format_delta, format_metric_name

    sections = []
    sections.append(create_heading(section.title, level=2))

    sensitivity = context.storm_sensitivity

    if sensitivity.metrics:
        entities_data = []

        entity_ids = sorted(set(m.entity_id for m in sensitivity.metrics))
        for entity_id in entity_ids:
            entity_metrics = sensitivity.get_metrics_for_entity(entity_id)
            if not entity_metrics:
                continue

            entity_name = entity_metrics[0].entity_name

            storm_ids = sorted(set(m.storm_event_id for m in entity_metrics))
            for storm_id in storm_ids:
                storm_metrics = [
                    m for m in entity_metrics if m.storm_event_id == storm_id
                ]
                if not storm_metrics:
                    continue

                storm_name = storm_metrics[0].storm_event_name
                row = {"entity": entity_name, "storm": storm_name}

                for m in storm_metrics:
                    col_key = m.metric.value
                    if m.delta is not None:
                        row[col_key] = format_delta(m.delta, m.unit, precision=1)
                    else:
                        row[col_key] = "—"

                entities_data.append(row)

        if entities_data:
            columns = [
                ("entity", "Entity"),
                ("storm", "Storm Event"),
            ]
            for metric in ComparisonMetric:
                col_header = format_metric_name(metric.value)
                columns.append((metric.value, col_header))

            table = create_entity_summary_table(entities_data, columns)
            table.title = "Storm Sensitivity Analysis"
            sections.append(create_table_section(table))

    if sensitivity.totals:
        totals_data = []

        storm_ids = sorted(set(t.storm_event_id for t in sensitivity.totals))
        for storm_id in storm_ids:
            storm_totals = sensitivity.get_totals_for_storm(storm_id)
            if not storm_totals:
                continue

            storm_name = storm_totals[0].storm_event_name
            row = {"storm": storm_name}

            for t in storm_totals:
                col_key = f"{t.metric.value}_total"
                if t.delta is not None:
                    row[col_key] = format_delta(t.delta, t.unit, precision=1)
                else:
                    row[col_key] = "—"

            totals_data.append(row)

        if totals_data:
            columns = [("storm", "Storm Event")]
            additive_metrics = ComparisonMetric.additive_metrics()
            for metric in additive_metrics:
                col_header = f"{format_metric_name(metric.value)} Total"
                columns.append((f"{metric.value}_total", col_header))

            table = create_entity_summary_table(totals_data, columns)
            table.title = "Storm Totals"
            sections.append(create_table_section(table))

    return sections


SECTION_BUILDERS: dict[
    str,
    Callable[[SectionTemplate, ReportTemplateContext], list[ReportSection]],
] = {
    "project_summary": _build_project_summary_section,
    "scenario_summary": _build_scenario_summary_section,
    "comparison_summary": _build_comparison_summary_section,
    "comparison_table": _build_comparison_table_section,
    "comparison_totals": _build_comparison_totals_section,
    "storm_sensitivity_table": _build_storm_sensitivity_table_section,
    "calculation_summary": _build_calculation_summary_section,
    "calculation_appendix": _build_calculation_appendix_section,
    "assumptions": _build_assumptions_section,
    "warnings": _build_warnings_section,
    "references": _build_references_section,
    "custom_text": _build_custom_text_section,
    "heading": _build_heading_section,
    # Infrastructure section builders
    "infrastructure_summary": _build_infrastructure_summary_section_wrapper,
    "infrastructure_schedule": _build_infrastructure_schedule_section_wrapper,
    "pipe_schedule": _build_pipe_schedule_section_wrapper,
    "inlet_schedule": _build_inlet_schedule_section_wrapper,
    "detention_schedule": _build_detention_schedule_section_wrapper,
    "infrastructure_check_summary": _build_infrastructure_check_summary_section_wrapper,
    "infrastructure_warnings": _build_infrastructure_warnings_section_wrapper,
    "infrastructure_assumptions": _build_infrastructure_assumptions_section_wrapper,
}


def _determine_report_type(template: ReportTemplate) -> ReportType:
    """Determine the report type from template sections."""
    section_types = {s.section_type for s in template.sections}
    appendix_types = {a.section_type for a in template.appendices}
    all_types = section_types | appendix_types

    if "comparison_summary" in all_types or "comparison_table" in all_types:
        return ReportType.SCENARIO_COMPARISON
    if "calculation_appendix" in all_types:
        return ReportType.CALCULATION_APPENDIX
    return ReportType.PROJECT_SUMMARY


def build_report_from_template(
    template: ReportTemplate,
    context: ReportTemplateContext,
) -> Report:
    """Build a structured Report from a template and context.

    Args:
        template: The report template defining structure.
        context: The context providing data.

    Returns:
        A Report object ready for rendering.

    Raises:
        TemplateBuildError: If report cannot be built.
        ContextValidationError: If required data is missing.
    """
    validate_template(template)
    validate_template_context(template, context)

    report_type = _determine_report_type(template)

    project_name = None
    project_id = None
    scenario_names = []

    if context.project:
        project_name = context.project.name
        project_id = context.project.id
    if context.scenario:
        scenario_names.append(context.scenario.name)
    if context.comparison:
        scenario_names = [
            context.comparison.baseline_scenario_name,
            context.comparison.comparison_scenario_name,
        ]

    metadata = ReportMetadata(
        title=template.name,
        report_type=report_type,
        project_name=project_name,
        project_id=project_id,
        scenario_names=scenario_names,
        author=context.metadata.get("author"),
        organization=context.metadata.get("organization"),
    )

    report = Report(metadata=metadata)

    report.add_section(create_heading(template.name, level=1))

    for section in template.get_ordered_sections():
        if not can_build_section(section, context):
            if section.required:
                raise TemplateBuildError(
                    f"Cannot build required section: {section.id}",
                    section_id=section.id,
                )
            continue

        builder = SECTION_BUILDERS.get(section.section_type)
        if builder is None:
            raise TemplateBuildError(
                f"No builder for section type: {section.section_type}",
                section_id=section.id,
            )

        built_sections = builder(section, context)
        for built_section in built_sections:
            report.add_section(built_section)

    if template.appendices:
        report.add_section(create_heading("Appendices", level=1))

        for appendix in template.get_ordered_appendices():
            if not can_build_section(appendix, context):
                if appendix.required:
                    raise TemplateBuildError(
                        f"Cannot build required appendix: {appendix.id}",
                        section_id=appendix.id,
                    )
                continue

            builder = SECTION_BUILDERS.get(appendix.section_type)
            if builder is None:
                raise TemplateBuildError(
                    f"No builder for section type: {appendix.section_type}",
                    section_id=appendix.id,
                )

            built_sections = builder(appendix, context)
            for built_section in built_sections:
                report.add_section(built_section)

    return report
