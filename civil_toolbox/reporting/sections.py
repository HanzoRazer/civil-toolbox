"""Section building utilities for reports."""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.models import (
    ReportSection,
    ReportTable,
    ReportFigurePlaceholder,
    SectionType,
)
from civil_toolbox.reporting.formatters import (
    format_value_with_unit,
    format_delta,
    format_percent,
    format_metric_name,
    format_date,
)
from civil_toolbox.reporting.tables import (
    create_key_value_table,
    create_metric_comparison_table,
    create_entity_summary_table,
    render_table_markdown,
)

if TYPE_CHECKING:
    from civil_toolbox.domain.project import Project
    from civil_toolbox.domain.scenario import Scenario
    from civil_toolbox.comparison.models import ScenarioComparisonResult


def create_heading(title: str, level: int = 2) -> ReportSection:
    """Create a heading section.

    Args:
        title: Heading text.
        level: Heading level (1-6).

    Returns:
        ReportSection of type HEADING.
    """
    return ReportSection(
        section_type=SectionType.HEADING,
        title=title,
        level=level,
    )


def create_text(content: str) -> ReportSection:
    """Create a text section.

    Args:
        content: Paragraph text.

    Returns:
        ReportSection of type TEXT.
    """
    return ReportSection(
        section_type=SectionType.TEXT,
        content=content,
    )


def create_list(items: list[str], title: str | None = None) -> ReportSection:
    """Create a list section.

    Args:
        items: List items.
        title: Optional section title.

    Returns:
        ReportSection of type LIST.
    """
    return ReportSection(
        section_type=SectionType.LIST,
        title=title,
        items=items,
    )


def create_table_section(table: ReportTable) -> ReportSection:
    """Create a table section.

    Args:
        table: The table to include.

    Returns:
        ReportSection of type TABLE.
    """
    return ReportSection(
        section_type=SectionType.TABLE,
        table=table,
    )


def create_figure_placeholder(
    figure_id: str,
    caption: str,
    description: str | None = None,
) -> ReportSection:
    """Create a figure placeholder section.

    Args:
        figure_id: Unique figure identifier.
        caption: Figure caption.
        description: Description of what the figure should show.

    Returns:
        ReportSection of type FIGURE_PLACEHOLDER.
    """
    return ReportSection(
        section_type=SectionType.FIGURE_PLACEHOLDER,
        figure=ReportFigurePlaceholder(
            figure_id=figure_id,
            caption=caption,
            description=description,
        ),
    )


def create_project_metadata_section(project: Project) -> ReportSection:
    """Create a project metadata section.

    Args:
        project: The project to describe.

    Returns:
        ReportSection with project metadata table.
    """
    items = [
        ("Project Name", project.name),
        ("Project ID", project.id),
    ]
    if hasattr(project, "description") and project.description:
        items.append(("Description", project.description))
    if hasattr(project, "client") and project.client:
        items.append(("Client", project.client))
    if hasattr(project, "location") and project.location:
        items.append(("Location", project.location))
    if hasattr(project, "created_at"):
        items.append(("Created", format_date(project.created_at)))

    table = create_key_value_table(items)
    table.title = "Project Information"

    return ReportSection(
        section_type=SectionType.METADATA,
        table=table,
    )


def create_scenario_summary_section(scenario: Scenario) -> ReportSection:
    """Create a scenario summary section.

    Args:
        scenario: The scenario to summarize.

    Returns:
        ReportSection with scenario information.
    """
    items = [
        ("Scenario Name", scenario.name),
        ("Drainage Areas", str(len(scenario.drainage_areas))),
        ("Storm Events", str(len(scenario.storm_events))),
        ("Flow Paths", str(len(scenario.flow_paths))),
        ("Calculations", str(len(scenario.calculation_results))),
    ]
    if scenario.description:
        items.insert(1, ("Description", scenario.description))

    table = create_key_value_table(items)
    table.title = f"Scenario: {scenario.name}"

    return ReportSection(
        section_type=SectionType.SUMMARY,
        title=scenario.name,
        table=table,
    )


def create_comparison_summary_section(
    comparison: ScenarioComparisonResult,
) -> ReportSection:
    """Create a comparison summary section.

    Args:
        comparison: The comparison result.

    Returns:
        ReportSection with comparison overview.
    """
    items = [
        ("Baseline Scenario", comparison.baseline_scenario_name),
        ("Comparison Scenario", comparison.comparison_scenario_name),
        ("Storm Event", comparison.storm_event_name or "All"),
        ("Match Strategy", comparison.match_strategy.value),
        ("Entities Compared", str(len(comparison.entity_comparisons))),
        ("Unmatched (Baseline)", str(len(comparison.unmatched_baseline_ids))),
        ("Unmatched (Comparison)", str(len(comparison.unmatched_comparison_ids))),
    ]

    table = create_key_value_table(items)
    table.title = "Comparison Overview"

    return ReportSection(
        section_type=SectionType.SUMMARY,
        title="Comparison Overview",
        table=table,
    )


def create_comparison_totals_section(
    comparison: ScenarioComparisonResult,
) -> ReportSection:
    """Create a section showing scenario-level totals.

    Args:
        comparison: The comparison result.

    Returns:
        ReportSection with totals table.
    """
    metrics = []
    for metric, totals in comparison.totals.items():
        metrics.append({
            "metric": format_metric_name(metric.value),
            "baseline": format_value_with_unit(
                totals.baseline_total, totals.unit, precision=1
            ),
            "comparison": format_value_with_unit(
                totals.comparison_total, totals.unit, precision=1
            ),
            "delta": format_delta(totals.delta, totals.unit, precision=1),
            "percent": format_percent(totals.percent_delta, precision=1),
        })

    table = create_metric_comparison_table(
        comparison.baseline_scenario_name,
        comparison.comparison_scenario_name,
        metrics,
    )
    table.title = "Scenario Totals"

    return ReportSection(
        section_type=SectionType.TABLE,
        title="Scenario Totals",
        table=table,
    )


def create_assumptions_section(
    assumptions: list[str],
    title: str = "Assumptions",
) -> ReportSection:
    """Create an assumptions section.

    Args:
        assumptions: List of assumption descriptions.
        title: Section title.

    Returns:
        ReportSection of type ASSUMPTIONS.
    """
    return ReportSection(
        section_type=SectionType.ASSUMPTIONS,
        title=title,
        items=assumptions,
    )


def create_warnings_section(
    warnings: list[str],
    title: str = "Warnings",
) -> ReportSection:
    """Create a warnings section.

    Args:
        warnings: List of warning messages.
        title: Section title.

    Returns:
        ReportSection of type WARNINGS.
    """
    return ReportSection(
        section_type=SectionType.WARNINGS,
        title=title,
        items=warnings,
    )


def create_references_section(
    references: list[dict[str, str]],
    title: str = "References",
) -> ReportSection:
    """Create a references section.

    Args:
        references: List of reference dictionaries with keys:
            - title: Reference title
            - source: Source/publisher
            - year: Publication year (optional)
        title: Section title.

    Returns:
        ReportSection of type REFERENCES.
    """
    items = []
    for ref in references:
        ref_str = f"{ref['title']}"
        if ref.get("source"):
            ref_str += f", {ref['source']}"
        if ref.get("year"):
            ref_str += f" ({ref['year']})"
        items.append(ref_str)

    return ReportSection(
        section_type=SectionType.REFERENCES,
        title=title,
        items=items,
    )
