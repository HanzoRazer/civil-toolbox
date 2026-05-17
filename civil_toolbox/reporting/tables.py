"""Table rendering utilities for reports."""

from __future__ import annotations

from civil_toolbox.reporting.models import ReportTable


def render_table_markdown(table: ReportTable) -> str:
    """Render a ReportTable as Markdown.

    Args:
        table: The table to render.

    Returns:
        Markdown-formatted table string.
    """
    lines = []

    if table.title:
        lines.append(f"**{table.title}**")
        lines.append("")

    lines.append("| " + " | ".join(table.headers) + " |")

    alignment_chars = []
    for align in table.alignments or ["left"] * len(table.headers):
        if align == "center":
            alignment_chars.append(":---:")
        elif align == "right":
            alignment_chars.append("---:")
        else:
            alignment_chars.append(":---")
    lines.append("| " + " | ".join(alignment_chars) + " |")

    for row in table.rows:
        escaped_cells = [_escape_pipe(cell) for cell in row]
        lines.append("| " + " | ".join(escaped_cells) + " |")

    if table.footer:
        lines.append("")
        lines.append(f"*{table.footer}*")

    return "\n".join(lines)


def _escape_pipe(text: str) -> str:
    """Escape pipe characters in table cells."""
    return text.replace("|", "\\|")


def create_comparison_table(
    headers: list[str],
    rows: list[dict[str, str]],
    key_column: str = "name",
) -> ReportTable:
    """Create a comparison table from row dictionaries.

    Args:
        headers: Column headers.
        rows: List of row dictionaries with keys matching headers.
        key_column: Name of the key column (first column).

    Returns:
        ReportTable with data aligned.
    """
    table_rows = []
    for row_dict in rows:
        row = []
        for header in headers:
            key = header.lower().replace(" ", "_")
            row.append(row_dict.get(key, row_dict.get(header, "—")))
        table_rows.append(row)

    alignments = ["left"] + ["right"] * (len(headers) - 1)

    return ReportTable(
        headers=headers,
        rows=table_rows,
        alignments=alignments,
    )


def create_key_value_table(
    items: list[tuple[str, str]],
    key_header: str = "Property",
    value_header: str = "Value",
) -> ReportTable:
    """Create a simple key-value table.

    Args:
        items: List of (key, value) tuples.
        key_header: Header for key column.
        value_header: Header for value column.

    Returns:
        ReportTable with two columns.
    """
    return ReportTable(
        headers=[key_header, value_header],
        rows=[[k, v] for k, v in items],
        alignments=["left", "left"],
    )


def create_metric_comparison_table(
    baseline_name: str,
    comparison_name: str,
    metrics: list[dict[str, str]],
) -> ReportTable:
    """Create a metric comparison table.

    Args:
        baseline_name: Name of baseline scenario.
        comparison_name: Name of comparison scenario.
        metrics: List of metric dictionaries with keys:
            - metric: Metric display name
            - baseline: Baseline value
            - comparison: Comparison value
            - delta: Delta value
            - percent: Percent change

    Returns:
        ReportTable for metric comparison.
    """
    headers = ["Metric", baseline_name, comparison_name, "Delta", "% Change"]
    rows = []

    for m in metrics:
        rows.append([
            m.get("metric", "—"),
            m.get("baseline", "—"),
            m.get("comparison", "—"),
            m.get("delta", "—"),
            m.get("percent", "—"),
        ])

    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "right", "right", "right", "right"],
    )


def create_entity_summary_table(
    entities: list[dict[str, str]],
    columns: list[tuple[str, str]],
) -> ReportTable:
    """Create an entity summary table.

    Args:
        entities: List of entity dictionaries.
        columns: List of (key, header) tuples defining columns.

    Returns:
        ReportTable summarizing entities.
    """
    headers = [header for _, header in columns]
    rows = []

    for entity in entities:
        row = []
        for key, _ in columns:
            row.append(entity.get(key, "—"))
        rows.append(row)

    alignments = ["left"] + ["right"] * (len(columns) - 1)

    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=alignments,
    )
