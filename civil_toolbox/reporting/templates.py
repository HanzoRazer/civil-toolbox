"""HTML templates for PDF report rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.assets import get_report_css
from civil_toolbox.reporting.formatters import format_datetime

if TYPE_CHECKING:
    from civil_toolbox.reporting.models import (
        Report,
        ReportSection,
        ReportTable,
    )


def escape_html(text: str) -> str:
    """Escape HTML special characters.

    Args:
        text: Text to escape.

    Returns:
        HTML-escaped text.
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_html_document(body: str, title: str = "Report") -> str:
    """Render a complete HTML document.

    Args:
        body: HTML body content.
        title: Document title.

    Returns:
        Complete HTML document string.
    """
    css = get_report_css()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{escape_html(title)}</title>
    <style>
{css}
    </style>
</head>
<body>
{body}
</body>
</html>"""


def render_table_html(table: ReportTable) -> str:
    """Render a ReportTable as HTML.

    Args:
        table: The table to render.

    Returns:
        HTML table string.
    """
    lines = []

    if table.title:
        lines.append(f'<div class="table-title">{escape_html(table.title)}</div>')

    lines.append("<table>")

    lines.append("<thead><tr>")
    for i, header in enumerate(table.headers):
        align = table.alignments[i] if table.alignments else "left"
        lines.append(f'<th class="align-{align}">{escape_html(header)}</th>')
    lines.append("</tr></thead>")

    lines.append("<tbody>")
    for row in table.rows:
        lines.append("<tr>")
        for i, cell in enumerate(row):
            align = table.alignments[i] if table.alignments else "left"
            lines.append(f'<td class="align-{align}">{escape_html(cell)}</td>')
        lines.append("</tr>")
    lines.append("</tbody>")

    lines.append("</table>")

    if table.footer:
        lines.append(f'<div class="table-footer">{escape_html(table.footer)}</div>')

    return "\n".join(lines)


def render_section_html(section: ReportSection) -> str:
    """Render a ReportSection as HTML.

    Args:
        section: The section to render.

    Returns:
        HTML string for the section.
    """
    from civil_toolbox.reporting.models import SectionType

    lines = []

    if section.section_type == SectionType.TITLE:
        lines.append(f"<h1>{escape_html(section.title or '')}</h1>")

    elif section.section_type == SectionType.HEADING:
        level = min(max(section.level, 1), 6)
        lines.append(f"<h{level}>{escape_html(section.title or '')}</h{level}>")

    elif section.section_type == SectionType.TEXT:
        if section.content:
            lines.append(f"<p>{escape_html(section.content)}</p>")

    elif section.section_type == SectionType.LIST:
        if section.title:
            lines.append(f'<p class="section-title"><strong>{escape_html(section.title)}:</strong></p>')
        if section.items:
            lines.append("<ul>")
            for item in section.items:
                lines.append(f"<li>{escape_html(item)}</li>")
            lines.append("</ul>")

    elif section.section_type == SectionType.TABLE:
        if section.table:
            lines.append(render_table_html(section.table))

    elif section.section_type == SectionType.METADATA:
        lines.append('<div class="metadata-block">')
        if section.table:
            lines.append(render_table_html(section.table))
        lines.append("</div>")

    elif section.section_type == SectionType.SUMMARY:
        if section.table:
            lines.append(render_table_html(section.table))

    elif section.section_type == SectionType.CALCULATION:
        lines.append('<div class="calculation-section">')
        if section.title:
            lines.append(f"<h3>{escape_html(section.title)}</h3>")
        lines.append("</div>")

    elif section.section_type == SectionType.ASSUMPTIONS:
        lines.append('<div class="assumptions-section">')
        if section.title:
            lines.append(f'<p class="section-title"><strong>{escape_html(section.title)}:</strong></p>')
        if section.items:
            lines.append("<ul>")
            for item in section.items:
                lines.append(f"<li>{escape_html(item)}</li>")
            lines.append("</ul>")
        lines.append("</div>")

    elif section.section_type == SectionType.WARNINGS:
        lines.append('<div class="warnings-section">')
        if section.title:
            lines.append(f'<p class="section-title"><strong>{escape_html(section.title)}:</strong></p>')
        if section.items:
            lines.append("<ul>")
            for item in section.items:
                lines.append(f'<li class="warning-item"><span class="warning-icon">&#9888;</span>{escape_html(item)}</li>')
            lines.append("</ul>")
        lines.append("</div>")

    elif section.section_type == SectionType.REFERENCES:
        lines.append('<div class="references-section">')
        if section.title:
            lines.append(f'<p class="section-title"><strong>{escape_html(section.title)}:</strong></p>')
        if section.items:
            lines.append("<ol>")
            for item in section.items:
                lines.append(f"<li>{escape_html(item)}</li>")
            lines.append("</ol>")
        lines.append("</div>")

    elif section.section_type == SectionType.FIGURE_PLACEHOLDER:
        lines.append('<div class="figure-placeholder">')
        if section.figure:
            lines.append(f'<p>[Figure: {escape_html(section.figure.figure_id)}]</p>')
            lines.append(f'<p class="figure-caption">{escape_html(section.figure.caption)}</p>')
            if section.figure.description:
                lines.append(f"<p>{escape_html(section.figure.description)}</p>")
        lines.append("</div>")

    if section.subsections:
        for subsection in section.subsections:
            lines.append(render_section_html(subsection))

    return "\n".join(lines)


def render_report_html(report: Report) -> str:
    """Render a Report as HTML body content.

    Args:
        report: The report to render.

    Returns:
        HTML body content string.
    """
    lines = []

    lines.append('<div class="title-block">')
    lines.append(f"<h1>{escape_html(report.metadata.title)}</h1>")

    lines.append('<div class="metadata-block">')
    lines.append("<table>")

    if report.metadata.project_name:
        lines.append(f"<tr><th>Project</th><td>{escape_html(report.metadata.project_name)}</td></tr>")
    if report.metadata.scenario_names:
        scenarios = ", ".join(report.metadata.scenario_names)
        lines.append(f"<tr><th>Scenarios</th><td>{escape_html(scenarios)}</td></tr>")
    if report.metadata.author:
        lines.append(f"<tr><th>Author</th><td>{escape_html(report.metadata.author)}</td></tr>")
    if report.metadata.organization:
        lines.append(f"<tr><th>Organization</th><td>{escape_html(report.metadata.organization)}</td></tr>")

    lines.append("</table>")
    lines.append("</div>")

    timestamp = format_datetime(report.metadata.generated_at)
    lines.append(f'<div class="generated-timestamp">Generated: {escape_html(timestamp)}</div>')
    lines.append("</div>")

    for section in report.sections:
        if section.section_type.value == "title":
            continue
        lines.append(render_section_html(section))

    return "\n".join(lines)


def render_report_to_html_document(report: Report) -> str:
    """Render a Report as a complete HTML document.

    Args:
        report: The report to render.

    Returns:
        Complete HTML document string.
    """
    body = render_report_html(report)
    return render_html_document(body, title=report.metadata.title)


def render_markdown_to_html_body(markdown_content: str) -> str:
    """Convert markdown content to HTML body.

    Uses the markdown library if available, otherwise falls back
    to a simple conversion.

    Args:
        markdown_content: Markdown text.

    Returns:
        HTML body content.
    """
    try:
        import markdown as md
        html = md.markdown(
            markdown_content,
            extensions=["tables", "fenced_code"],
        )
        return html
    except ImportError:
        return _simple_markdown_to_html(markdown_content)


def _simple_markdown_to_html(text: str) -> str:
    """Simple fallback markdown to HTML conversion.

    Handles basic formatting when markdown library is unavailable.

    Args:
        text: Markdown text.

    Returns:
        Basic HTML conversion.
    """
    lines = text.split("\n")
    html_lines = []
    in_list = False
    in_table = False
    table_alignment = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{escape_html(line[2:])}</h1>")

        elif line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{escape_html(line[3:])}</h2>")

        elif line.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{escape_html(line[4:])}</h3>")

        elif line.startswith("#### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h4>{escape_html(line[5:])}</h4>")

        elif line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{escape_html(line[2:])}</li>")

        elif line.startswith("| ") and line.endswith(" |"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False

            if not in_table:
                html_lines.append("<table>")
                in_table = True
                cells = [c.strip() for c in line[1:-1].split("|")]
                html_lines.append("<thead><tr>")
                for cell in cells:
                    html_lines.append(f"<th>{escape_html(cell)}</th>")
                html_lines.append("</tr></thead>")
                html_lines.append("<tbody>")

                if i + 1 < len(lines) and lines[i + 1].startswith("|"):
                    i += 1
            else:
                cells = [c.strip() for c in line[1:-1].split("|")]
                html_lines.append("<tr>")
                for cell in cells:
                    html_lines.append(f"<td>{escape_html(cell)}</td>")
                html_lines.append("</tr>")

        elif line.strip() == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append("")

        elif line.startswith("---"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append("<hr>")

        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if line.strip():
                html_lines.append(f"<p>{escape_html(line)}</p>")

        i += 1

    if in_list:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append("</tbody></table>")

    return "\n".join(html_lines)
