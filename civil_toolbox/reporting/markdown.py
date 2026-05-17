"""Markdown rendering for reports."""

from __future__ import annotations

from civil_toolbox.reporting.models import (
    Report,
    ReportSection,
    SectionType,
)
from civil_toolbox.reporting.tables import render_table_markdown
from civil_toolbox.reporting.formatters import format_datetime


def render_report_markdown(report: Report) -> str:
    """Render a complete report as Markdown.

    Args:
        report: The report to render.

    Returns:
        Markdown-formatted string.
    """
    lines = []

    for section in report.sections:
        section_lines = render_section_markdown(section)
        lines.extend(section_lines)
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def render_section_markdown(section: ReportSection, depth: int = 0) -> list[str]:
    """Render a section as Markdown lines.

    Args:
        section: The section to render.
        depth: Nesting depth for indentation.

    Returns:
        List of Markdown lines.
    """
    lines = []

    if section.section_type == SectionType.TITLE:
        lines.append(f"# {section.title}")

    elif section.section_type == SectionType.HEADING:
        prefix = "#" * section.level
        lines.append(f"{prefix} {section.title}")

    elif section.section_type == SectionType.TEXT:
        if section.content:
            lines.append(section.content)

    elif section.section_type == SectionType.LIST:
        if section.title:
            lines.append(f"**{section.title}:**")
            lines.append("")
        if section.items:
            for item in section.items:
                lines.append(f"- {item}")

    elif section.section_type == SectionType.TABLE:
        if section.table:
            lines.append(render_table_markdown(section.table))

    elif section.section_type == SectionType.METADATA:
        if section.table:
            lines.append(render_table_markdown(section.table))

    elif section.section_type == SectionType.SUMMARY:
        if section.table:
            lines.append(render_table_markdown(section.table))

    elif section.section_type == SectionType.CALCULATION:
        if section.title:
            lines.append(f"### {section.title}")
            lines.append("")

    elif section.section_type == SectionType.ASSUMPTIONS:
        if section.title:
            lines.append(f"**{section.title}:**")
            lines.append("")
        if section.items:
            for item in section.items:
                lines.append(f"- {item}")

    elif section.section_type == SectionType.WARNINGS:
        if section.title:
            lines.append(f"**{section.title}:**")
            lines.append("")
        if section.items:
            for item in section.items:
                lines.append(f"- ⚠️ {item}")

    elif section.section_type == SectionType.REFERENCES:
        if section.title:
            lines.append(f"**{section.title}:**")
            lines.append("")
        if section.items:
            for i, item in enumerate(section.items, 1):
                lines.append(f"{i}. {item}")

    elif section.section_type == SectionType.FIGURE_PLACEHOLDER:
        if section.figure:
            lines.append(f"*[Figure: {section.figure.caption}]*")
            if section.figure.description:
                lines.append(f"*{section.figure.description}*")

    if section.subsections:
        for subsection in section.subsections:
            lines.append("")
            subsection_lines = render_section_markdown(subsection, depth + 1)
            lines.extend(subsection_lines)

    return lines


def render_metadata_header(report: Report) -> str:
    """Render a metadata header block.

    Args:
        report: The report to extract metadata from.

    Returns:
        Markdown-formatted metadata block.
    """
    meta = report.metadata
    lines = [
        "---",
        f"title: {meta.title}",
        f"type: {meta.report_type.value}",
        f"generated: {format_datetime(meta.generated_at)}",
    ]
    if meta.project_name:
        lines.append(f"project: {meta.project_name}")
    if meta.scenario_names:
        lines.append(f"scenarios: {', '.join(meta.scenario_names)}")
    if meta.author:
        lines.append(f"author: {meta.author}")
    if meta.organization:
        lines.append(f"organization: {meta.organization}")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def render_full_report_markdown(
    report: Report,
    include_metadata_header: bool = True,
) -> str:
    """Render a complete report with optional metadata header.

    Args:
        report: The report to render.
        include_metadata_header: Whether to include YAML-style metadata header.

    Returns:
        Complete Markdown document.
    """
    parts = []

    if include_metadata_header:
        parts.append(render_metadata_header(report))

    parts.append(render_report_markdown(report))

    return "\n".join(parts)
