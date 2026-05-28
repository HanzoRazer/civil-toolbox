"""Infrastructure section builders for reports.

Builds ReportSection objects from infrastructure data. Does not run
calculations — only formats existing data from InfrastructureNetwork
and InfrastructureCheckResult objects.

Example:
    >>> from civil_toolbox.reporting.infrastructure_sections import (
    ...     build_infrastructure_summary_section,
    ...     build_pipe_schedule_section,
    ... )
    >>> sections = build_infrastructure_summary_section(network)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.models import ReportSection, SectionType
from civil_toolbox.reporting.sections import (
    create_heading,
    create_text,
    create_table_section,
    create_list,
)
from civil_toolbox.reporting.infrastructure_tables import (
    build_infrastructure_summary_table,
    build_pipe_schedule_table,
    build_inlet_schedule_table,
    build_detention_schedule_table,
    build_infrastructure_check_summary_table,
)

if TYPE_CHECKING:
    from civil_toolbox.infrastructure import InfrastructureNetwork
    from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult


def build_infrastructure_summary_section(
    network: InfrastructureNetwork,
    title: str = "Infrastructure Summary",
    level: int = 2,
) -> list[ReportSection]:
    """Build infrastructure summary section.

    Includes element type counts and status breakdown.

    Args:
        network: The infrastructure network.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    element_count = len(network.elements)
    node_count = len(network.nodes)

    if element_count == 0 and node_count == 0:
        sections.append(create_text("No infrastructure elements defined."))
        return sections

    table = build_infrastructure_summary_table(network)
    sections.append(create_table_section(table))

    return sections


def build_infrastructure_schedule_section(
    network: InfrastructureNetwork,
    title: str = "Infrastructure Schedule",
    level: int = 2,
) -> list[ReportSection]:
    """Build combined infrastructure schedule section.

    Includes pipes, inlets, and detention facilities.

    Args:
        network: The infrastructure network.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    has_content = False

    pipes = list(network.iter_pipes())
    if pipes:
        has_content = True
        table = build_pipe_schedule_table(network)
        sections.append(create_table_section(table))

    inlets = list(network.iter_inlets())
    if inlets:
        has_content = True
        table = build_inlet_schedule_table(network)
        sections.append(create_table_section(table))

    detention = list(network.iter_detention())
    if detention:
        has_content = True
        table = build_detention_schedule_table(network)
        sections.append(create_table_section(table))

    if not has_content:
        sections.append(create_text("No infrastructure elements defined."))

    return sections


def build_pipe_schedule_section(
    network: InfrastructureNetwork,
    title: str = "Pipe Schedule",
    level: int = 2,
) -> list[ReportSection]:
    """Build pipe schedule section.

    Args:
        network: The infrastructure network.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    pipes = list(network.iter_pipes())
    if not pipes:
        sections.append(create_text("No pipes defined."))
        return sections

    table = build_pipe_schedule_table(network)
    sections.append(create_table_section(table))

    return sections


def build_inlet_schedule_section(
    network: InfrastructureNetwork,
    title: str = "Inlet Schedule",
    level: int = 2,
) -> list[ReportSection]:
    """Build inlet schedule section.

    Args:
        network: The infrastructure network.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    inlets = list(network.iter_inlets())
    if not inlets:
        sections.append(create_text("No inlets defined."))
        return sections

    table = build_inlet_schedule_table(network)
    sections.append(create_table_section(table))

    return sections


def build_detention_schedule_section(
    network: InfrastructureNetwork,
    title: str = "Detention Schedule",
    level: int = 2,
) -> list[ReportSection]:
    """Build detention facility schedule section.

    Args:
        network: The infrastructure network.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    facilities = list(network.iter_detention())
    if not facilities:
        sections.append(create_text("No detention facilities defined."))
        return sections

    table = build_detention_schedule_table(network)
    sections.append(create_table_section(table))

    return sections


def build_infrastructure_check_summary_section(
    check_results: list[InfrastructureCheckResult],
    title: str = "Infrastructure Sizing Checks",
    level: int = 2,
) -> list[ReportSection]:
    """Build infrastructure sizing check summary section.

    Args:
        check_results: List of infrastructure check results.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    if not check_results:
        sections.append(create_text("No infrastructure sizing checks performed."))
        return sections

    passing = sum(1 for r in check_results if r.passes)
    failing = len(check_results) - passing

    summary_text = f"{len(check_results)} checks performed: {passing} passing, {failing} failing."
    sections.append(create_text(summary_text))

    table = build_infrastructure_check_summary_table(check_results)
    sections.append(create_table_section(table))

    return sections


def build_infrastructure_warnings_section(
    check_results: list[InfrastructureCheckResult],
    title: str = "Infrastructure Warnings",
    level: int = 2,
) -> list[ReportSection]:
    """Build infrastructure warnings section.

    Aggregates all warnings from check results.

    Args:
        check_results: List of infrastructure check results.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    all_warnings = []
    for result in check_results:
        for warning in result.warnings:
            warning_text = f"[{warning.warning_code}] {result.element_name}: {warning.message}"
            all_warnings.append(warning_text)

    if not all_warnings:
        sections.append(create_text("No warnings generated."))
        return sections

    sorted_warnings = sorted(set(all_warnings))
    sections.append(create_list(sorted_warnings))

    return sections


def build_infrastructure_assumptions_section(
    check_results: list[InfrastructureCheckResult],
    title: str = "Infrastructure Assumptions",
    level: int = 2,
) -> list[ReportSection]:
    """Build infrastructure assumptions section.

    Aggregates all assumptions from check results.

    Args:
        check_results: List of infrastructure check results.
        title: Section title.
        level: Heading level.

    Returns:
        List of ReportSection objects.
    """
    sections = []
    sections.append(create_heading(title, level=level))

    all_assumptions = set()
    for result in check_results:
        for assumption in result.assumptions:
            all_assumptions.add(assumption)

    if not all_assumptions:
        sections.append(create_text("No assumptions recorded."))
        return sections

    sorted_assumptions = sorted(all_assumptions)
    sections.append(create_list(sorted_assumptions))

    return sections
