"""Tests for table rendering utilities."""

import pytest

from civil_toolbox.reporting.tables import (
    render_table_markdown,
    create_comparison_table,
    create_key_value_table,
    create_metric_comparison_table,
    create_entity_summary_table,
    _escape_pipe,
)
from civil_toolbox.reporting.models import ReportTable


class TestRenderTableMarkdown:
    """Tests for render_table_markdown."""

    def test_renders_simple_table(self):
        """Renders a simple table."""
        table = ReportTable(
            headers=["Name", "Value"],
            rows=[["A", "100"], ["B", "200"]],
        )
        result = render_table_markdown(table)

        assert "| Name | Value |" in result
        assert "| A | 100 |" in result
        assert "| B | 200 |" in result

    def test_renders_alignment_row(self):
        """Renders alignment row correctly."""
        table = ReportTable(
            headers=["Left", "Center", "Right"],
            rows=[["a", "b", "c"]],
            alignments=["left", "center", "right"],
        )
        result = render_table_markdown(table)

        assert "| :--- | :---: | ---: |" in result

    def test_renders_title(self):
        """Renders table title."""
        table = ReportTable(
            headers=["X"],
            rows=[["Y"]],
            title="Table 1: Results",
        )
        result = render_table_markdown(table)

        assert "**Table 1: Results**" in result

    def test_renders_footer(self):
        """Renders table footer."""
        table = ReportTable(
            headers=["X"],
            rows=[["Y"]],
            footer="Note: All values in cfs",
        )
        result = render_table_markdown(table)

        assert "*Note: All values in cfs*" in result

    def test_escapes_pipe_characters(self):
        """Escapes pipe characters in cells."""
        table = ReportTable(
            headers=["Expression"],
            rows=[["a | b"]],
        )
        result = render_table_markdown(table)

        assert "a \\| b" in result

    def test_deterministic_output(self):
        """Output is deterministic."""
        table = ReportTable(
            headers=["A", "B"],
            rows=[["1", "2"], ["3", "4"]],
        )
        result1 = render_table_markdown(table)
        result2 = render_table_markdown(table)

        assert result1 == result2


class TestEscapePipe:
    """Tests for _escape_pipe."""

    def test_escapes_single_pipe(self):
        """Escapes single pipe."""
        assert _escape_pipe("a|b") == "a\\|b"

    def test_escapes_multiple_pipes(self):
        """Escapes multiple pipes."""
        assert _escape_pipe("a|b|c") == "a\\|b\\|c"

    def test_no_pipe_unchanged(self):
        """Text without pipe is unchanged."""
        assert _escape_pipe("hello") == "hello"


class TestCreateComparisonTable:
    """Tests for create_comparison_table."""

    def test_creates_from_row_dicts(self):
        """Creates table from row dictionaries."""
        headers = ["Name", "Value"]
        rows = [
            {"name": "A", "value": "100"},
            {"name": "B", "value": "200"},
        ]
        table = create_comparison_table(headers, rows)

        assert table.headers == ["Name", "Value"]
        assert table.rows == [["A", "100"], ["B", "200"]]

    def test_first_column_left_aligned(self):
        """First column is left-aligned."""
        table = create_comparison_table(
            ["Name", "X", "Y"],
            [{"name": "A", "x": "1", "y": "2"}],
        )
        assert table.alignments[0] == "left"

    def test_other_columns_right_aligned(self):
        """Other columns are right-aligned."""
        table = create_comparison_table(
            ["Name", "X", "Y"],
            [{"name": "A", "x": "1", "y": "2"}],
        )
        assert table.alignments[1] == "right"
        assert table.alignments[2] == "right"

    def test_missing_values_show_dash(self):
        """Missing values show em-dash."""
        table = create_comparison_table(
            ["Name", "Value"],
            [{"name": "A"}],
        )
        assert table.rows[0][1] == "—"


class TestCreateKeyValueTable:
    """Tests for create_key_value_table."""

    def test_creates_two_column_table(self):
        """Creates two-column key-value table."""
        items = [
            ("Project", "Test Project"),
            ("Date", "2026-05-17"),
        ]
        table = create_key_value_table(items)

        assert table.headers == ["Property", "Value"]
        assert table.rows == [["Project", "Test Project"], ["Date", "2026-05-17"]]

    def test_custom_headers(self):
        """Supports custom headers."""
        table = create_key_value_table(
            [("A", "1")],
            key_header="Setting",
            value_header="Config",
        )
        assert table.headers == ["Setting", "Config"]

    def test_both_columns_left_aligned(self):
        """Both columns are left-aligned."""
        table = create_key_value_table([("K", "V")])
        assert table.alignments == ["left", "left"]


class TestCreateMetricComparisonTable:
    """Tests for create_metric_comparison_table."""

    def test_creates_comparison_columns(self):
        """Creates table with comparison columns."""
        metrics = [
            {
                "metric": "Peak Flow",
                "baseline": "100 cfs",
                "comparison": "120 cfs",
                "delta": "+20 cfs",
                "percent": "+20%",
            },
        ]
        table = create_metric_comparison_table("Existing", "Proposed", metrics)

        assert table.headers == ["Metric", "Existing", "Proposed", "Delta", "% Change"]
        assert table.rows[0] == ["Peak Flow", "100 cfs", "120 cfs", "+20 cfs", "+20%"]

    def test_numeric_columns_right_aligned(self):
        """Numeric columns are right-aligned."""
        table = create_metric_comparison_table("A", "B", [])

        assert table.alignments[0] == "left"
        assert table.alignments[1] == "right"
        assert table.alignments[2] == "right"
        assert table.alignments[3] == "right"
        assert table.alignments[4] == "right"

    def test_missing_values_show_dash(self):
        """Missing metric values show em-dash."""
        metrics = [{"metric": "Test"}]
        table = create_metric_comparison_table("A", "B", metrics)

        assert table.rows[0] == ["Test", "—", "—", "—", "—"]


class TestCreateEntitySummaryTable:
    """Tests for create_entity_summary_table."""

    def test_creates_from_entities(self):
        """Creates table from entity dictionaries."""
        entities = [
            {"name": "Area A", "area": "25 ac", "cn": "75"},
            {"name": "Area B", "area": "15 ac", "cn": "80"},
        ]
        columns = [("name", "Name"), ("area", "Area"), ("cn", "CN")]
        table = create_entity_summary_table(entities, columns)

        assert table.headers == ["Name", "Area", "CN"]
        assert table.rows[0] == ["Area A", "25 ac", "75"]
        assert table.rows[1] == ["Area B", "15 ac", "80"]

    def test_first_column_left_aligned(self):
        """First column is left-aligned."""
        table = create_entity_summary_table(
            [{"a": "1", "b": "2"}],
            [("a", "A"), ("b", "B")],
        )
        assert table.alignments[0] == "left"
        assert table.alignments[1] == "right"

    def test_missing_values_show_dash(self):
        """Missing values show em-dash."""
        entities = [{"name": "Test"}]
        columns = [("name", "Name"), ("missing", "Missing")]
        table = create_entity_summary_table(entities, columns)

        assert table.rows[0][1] == "—"
