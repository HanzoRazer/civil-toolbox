"""Reporting engine for Civil Toolbox.

Generate engineering reports from domain objects:
- Project summaries
- Scenario comparisons
- Calculation appendices

Output formats:
- Markdown (current)
- PDF (planned)

Example:
    >>> from civil_toolbox.reporting import (
    ...     generate_project_summary_report,
    ...     render_full_report_markdown,
    ... )
    >>> report = generate_project_summary_report(project)
    >>> markdown = render_full_report_markdown(report)
    >>> print(markdown)

The reporting engine consumes domain objects and comparison results.
It does not run calculations — it only formats existing data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.models import (
    Report,
    ReportMetadata,
    ReportSection,
    ReportTable,
    ReportFigurePlaceholder,
    ReportType,
    SectionType,
)

from civil_toolbox.reporting.errors import (
    ReportingError,
    InvalidReportDataError,
    MissingProjectError,
    MissingScenarioError,
    MissingComparisonError,
    RenderingError,
)

from civil_toolbox.reporting.formatters import (
    format_number,
    format_percent,
    format_delta,
    format_value_with_unit,
    format_datetime,
    format_date,
    format_status,
    format_metric_name,
    escape_markdown,
    truncate,
)

from civil_toolbox.reporting.tables import (
    render_table_markdown,
    create_comparison_table,
    create_key_value_table,
    create_metric_comparison_table,
    create_entity_summary_table,
)

from civil_toolbox.reporting.sections import (
    create_heading,
    create_text,
    create_list,
    create_table_section,
    create_figure_placeholder,
    create_project_metadata_section,
    create_scenario_summary_section,
    create_comparison_summary_section,
    create_comparison_totals_section,
    create_assumptions_section,
    create_warnings_section,
    create_references_section,
)

from civil_toolbox.reporting.appendix import (
    create_calculation_section,
    generate_calculation_appendix,
)

from civil_toolbox.reporting.markdown import (
    render_report_markdown,
    render_section_markdown,
    render_metadata_header,
    render_full_report_markdown,
)

if TYPE_CHECKING:
    from civil_toolbox.domain.project import Project
    from civil_toolbox.domain.scenario import Scenario
    from civil_toolbox.comparison.models import ScenarioComparisonResult


def generate_project_summary_report(
    project: Project,
    title: str | None = None,
) -> Report:
    """Generate a project summary report.

    Args:
        project: The project to summarize.
        title: Optional custom title.

    Returns:
        Report with project overview.
    """
    report_title = title or f"Project Summary: {project.name}"

    metadata = ReportMetadata(
        title=report_title,
        report_type=ReportType.PROJECT_SUMMARY,
        project_name=project.name,
        project_id=project.id,
    )

    report = Report(metadata=metadata)

    report.add_section(create_heading(report_title, level=1))

    report.add_section(create_project_metadata_section(project))

    if hasattr(project, "scenarios") and project.scenarios:
        report.add_section(create_heading("Scenarios", level=2))
        for scenario in project.scenarios:
            report.add_section(create_scenario_summary_section(scenario))

    return report


def generate_scenario_comparison_report(
    comparison: ScenarioComparisonResult,
    title: str | None = None,
) -> Report:
    """Generate a scenario comparison report.

    Args:
        comparison: The comparison result.
        title: Optional custom title.

    Returns:
        Report with comparison details.
    """
    from civil_toolbox.comparison.models import ComparisonMetric

    report_title = title or (
        f"Scenario Comparison: {comparison.baseline_scenario_name} "
        f"vs {comparison.comparison_scenario_name}"
    )

    metadata = ReportMetadata(
        title=report_title,
        report_type=ReportType.SCENARIO_COMPARISON,
        scenario_names=[
            comparison.baseline_scenario_name,
            comparison.comparison_scenario_name,
        ],
    )

    report = Report(metadata=metadata)

    report.add_section(create_heading(report_title, level=1))

    report.add_section(create_comparison_summary_section(comparison))

    if comparison.totals:
        report.add_section(create_heading("Scenario Totals", level=2))
        report.add_section(create_comparison_totals_section(comparison))

    if comparison.entity_comparisons:
        report.add_section(create_heading("Entity Comparisons", level=2))

        entities_data = []
        for entity in comparison.entity_comparisons:
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
            report.add_section(create_table_section(table))

    if comparison.unmatched_baseline_ids or comparison.unmatched_comparison_ids:
        report.add_section(create_heading("Unmatched Entities", level=2))
        if comparison.unmatched_baseline_ids:
            report.add_section(
                create_list(
                    comparison.unmatched_baseline_ids,
                    title=f"Unmatched in {comparison.baseline_scenario_name}",
                )
            )
        if comparison.unmatched_comparison_ids:
            report.add_section(
                create_list(
                    comparison.unmatched_comparison_ids,
                    title=f"Unmatched in {comparison.comparison_scenario_name}",
                )
            )

    return report


__all__ = [
    # Models
    "Report",
    "ReportMetadata",
    "ReportSection",
    "ReportTable",
    "ReportFigurePlaceholder",
    "ReportType",
    "SectionType",
    # Errors
    "ReportingError",
    "InvalidReportDataError",
    "MissingProjectError",
    "MissingScenarioError",
    "MissingComparisonError",
    "RenderingError",
    # Formatters
    "format_number",
    "format_percent",
    "format_delta",
    "format_value_with_unit",
    "format_datetime",
    "format_date",
    "format_status",
    "format_metric_name",
    "escape_markdown",
    "truncate",
    # Tables
    "render_table_markdown",
    "create_comparison_table",
    "create_key_value_table",
    "create_metric_comparison_table",
    "create_entity_summary_table",
    # Sections
    "create_heading",
    "create_text",
    "create_list",
    "create_table_section",
    "create_figure_placeholder",
    "create_project_metadata_section",
    "create_scenario_summary_section",
    "create_comparison_summary_section",
    "create_comparison_totals_section",
    "create_assumptions_section",
    "create_warnings_section",
    "create_references_section",
    # Appendix
    "create_calculation_section",
    "generate_calculation_appendix",
    # Markdown
    "render_report_markdown",
    "render_section_markdown",
    "render_metadata_header",
    "render_full_report_markdown",
    # Report Generators
    "generate_project_summary_report",
    "generate_scenario_comparison_report",
]
