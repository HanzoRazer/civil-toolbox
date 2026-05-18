"""Tests for HTML template rendering."""

import pytest

from civil_toolbox.reporting.templates import (
    escape_html,
    render_html_document,
    render_table_html,
    render_section_html,
    render_report_html,
    render_report_to_html_document,
    render_markdown_to_html_body,
    _simple_markdown_to_html,
)
from civil_toolbox.reporting.models import (
    Report,
    ReportMetadata,
    ReportSection,
    ReportTable,
    ReportFigurePlaceholder,
    ReportType,
    SectionType,
)


class TestEscapeHtml:
    """Tests for escape_html."""

    def test_escapes_ampersand(self):
        """Escapes & character."""
        assert escape_html("A & B") == "A &amp; B"

    def test_escapes_less_than(self):
        """Escapes < character."""
        assert escape_html("a < b") == "a &lt; b"

    def test_escapes_greater_than(self):
        """Escapes > character."""
        assert escape_html("a > b") == "a &gt; b"

    def test_escapes_quotes(self):
        """Escapes quote characters."""
        assert escape_html('a "b" c') == "a &quot;b&quot; c"
        assert escape_html("a 'b' c") == "a &#39;b&#39; c"

    def test_no_change_for_safe_text(self):
        """Safe text is unchanged."""
        assert escape_html("Hello World") == "Hello World"


class TestRenderHtmlDocument:
    """Tests for render_html_document."""

    def test_creates_complete_html(self):
        """Creates a complete HTML document."""
        result = render_html_document("<p>Test</p>", title="My Report")

        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "<head>" in result
        assert "<title>My Report</title>" in result
        assert "<style>" in result
        assert "<body>" in result
        assert "<p>Test</p>" in result
        assert "</body>" in result
        assert "</html>" in result

    def test_includes_css(self):
        """Includes CSS stylesheet."""
        result = render_html_document("<p>Test</p>")

        assert "@page" in result
        assert "font-family" in result

    def test_escapes_title(self):
        """Escapes special characters in title."""
        result = render_html_document("<p>Test</p>", title="Report <Draft>")

        assert "Report &lt;Draft&gt;" in result


class TestRenderTableHtml:
    """Tests for render_table_html."""

    def test_renders_simple_table(self):
        """Renders a simple table."""
        table = ReportTable(
            headers=["Name", "Value"],
            rows=[["A", "100"], ["B", "200"]],
        )
        result = render_table_html(table)

        assert "<table>" in result
        assert "<thead>" in result
        assert "<th" in result
        assert ">Name</th>" in result
        assert ">Value</th>" in result
        assert "<tbody>" in result
        assert ">A</td>" in result
        assert ">100</td>" in result
        assert "</table>" in result

    def test_renders_title(self):
        """Renders table title."""
        table = ReportTable(
            headers=["X"],
            rows=[["Y"]],
            title="Table 1",
        )
        result = render_table_html(table)

        assert 'class="table-title"' in result
        assert "Table 1" in result

    def test_renders_footer(self):
        """Renders table footer."""
        table = ReportTable(
            headers=["X"],
            rows=[["Y"]],
            footer="Note: Values in cfs",
        )
        result = render_table_html(table)

        assert 'class="table-footer"' in result
        assert "Note: Values in cfs" in result

    def test_renders_alignment(self):
        """Renders column alignment."""
        table = ReportTable(
            headers=["Left", "Center", "Right"],
            rows=[["a", "b", "c"]],
            alignments=["left", "center", "right"],
        )
        result = render_table_html(table)

        assert 'class="align-left"' in result
        assert 'class="align-center"' in result
        assert 'class="align-right"' in result

    def test_escapes_content(self):
        """Escapes HTML in table content."""
        table = ReportTable(
            headers=["Expression"],
            rows=[["a < b & c > d"]],
        )
        result = render_table_html(table)

        assert "a &lt; b &amp; c &gt; d" in result


class TestRenderSectionHtml:
    """Tests for render_section_html."""

    def test_renders_title_section(self):
        """Renders title section."""
        section = ReportSection(
            section_type=SectionType.TITLE,
            title="Report Title",
        )
        result = render_section_html(section)

        assert "<h1>Report Title</h1>" in result

    def test_renders_heading_section(self):
        """Renders heading section with correct level."""
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Section Heading",
            level=3,
        )
        result = render_section_html(section)

        assert "<h3>Section Heading</h3>" in result

    def test_renders_text_section(self):
        """Renders text section."""
        section = ReportSection(
            section_type=SectionType.TEXT,
            content="This is a paragraph.",
        )
        result = render_section_html(section)

        assert "<p>This is a paragraph.</p>" in result

    def test_renders_list_section(self):
        """Renders list section."""
        section = ReportSection(
            section_type=SectionType.LIST,
            title="Items",
            items=["First", "Second", "Third"],
        )
        result = render_section_html(section)

        assert "<strong>Items:</strong>" in result
        assert "<ul>" in result
        assert "<li>First</li>" in result
        assert "<li>Second</li>" in result
        assert "</ul>" in result

    def test_renders_table_section(self):
        """Renders table section."""
        section = ReportSection(
            section_type=SectionType.TABLE,
            table=ReportTable(
                headers=["Col1"],
                rows=[["Val1"]],
            ),
        )
        result = render_section_html(section)

        assert "<table>" in result
        assert "Col1" in result
        assert "Val1" in result

    def test_renders_metadata_section(self):
        """Renders metadata section with special styling."""
        section = ReportSection(
            section_type=SectionType.METADATA,
            table=ReportTable(
                headers=["Property", "Value"],
                rows=[["Project", "Test"]],
            ),
        )
        result = render_section_html(section)

        assert 'class="metadata-block"' in result

    def test_renders_assumptions_section(self):
        """Renders assumptions section."""
        section = ReportSection(
            section_type=SectionType.ASSUMPTIONS,
            title="Assumptions",
            items=["Steady state", "Uniform rainfall"],
        )
        result = render_section_html(section)

        assert 'class="assumptions-section"' in result
        assert "Steady state" in result

    def test_renders_warnings_section(self):
        """Renders warnings section with special styling."""
        section = ReportSection(
            section_type=SectionType.WARNINGS,
            title="Warnings",
            items=["Area exceeds limit"],
        )
        result = render_section_html(section)

        assert 'class="warnings-section"' in result
        assert 'class="warning-item"' in result
        assert "Area exceeds limit" in result

    def test_renders_references_section(self):
        """Renders references as ordered list."""
        section = ReportSection(
            section_type=SectionType.REFERENCES,
            title="References",
            items=["TR-55", "HEC-22"],
        )
        result = render_section_html(section)

        assert 'class="references-section"' in result
        assert "<ol>" in result
        assert "<li>TR-55</li>" in result

    def test_renders_figure_placeholder(self):
        """Renders figure placeholder."""
        section = ReportSection(
            section_type=SectionType.FIGURE_PLACEHOLDER,
            figure=ReportFigurePlaceholder(
                figure_id="fig-1",
                caption="Site Plan",
                description="Shows drainage boundaries",
            ),
        )
        result = render_section_html(section)

        assert 'class="figure-placeholder"' in result
        assert "fig-1" in result
        assert "Site Plan" in result
        assert "Shows drainage boundaries" in result

    def test_renders_subsections(self):
        """Renders nested subsections."""
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Parent",
            level=2,
            subsections=[
                ReportSection(
                    section_type=SectionType.TEXT,
                    content="Child content",
                ),
            ],
        )
        result = render_section_html(section)

        assert "<h2>Parent</h2>" in result
        assert "<p>Child content</p>" in result


class TestRenderReportHtml:
    """Tests for render_report_html."""

    def test_renders_report_body(self):
        """Renders report body content."""
        report = Report(
            metadata=ReportMetadata(
                title="Test Report",
                report_type=ReportType.PROJECT_SUMMARY,
                project_name="My Project",
            ),
            sections=[
                ReportSection(
                    section_type=SectionType.HEADING,
                    title="Overview",
                    level=2,
                ),
            ],
        )
        result = render_report_html(report)

        assert 'class="title-block"' in result
        assert "Test Report" in result
        assert 'class="metadata-block"' in result
        assert "My Project" in result
        assert "<h2>Overview</h2>" in result

    def test_includes_timestamp(self):
        """Includes generated timestamp."""
        report = Report(
            metadata=ReportMetadata(
                title="Test",
                report_type=ReportType.PROJECT_SUMMARY,
            ),
        )
        result = render_report_html(report)

        assert 'class="generated-timestamp"' in result
        assert "Generated:" in result


class TestRenderReportToHtmlDocument:
    """Tests for render_report_to_html_document."""

    def test_creates_complete_document(self):
        """Creates a complete HTML document from report."""
        report = Report(
            metadata=ReportMetadata(
                title="Full Report",
                report_type=ReportType.PROJECT_SUMMARY,
            ),
            sections=[
                ReportSection(
                    section_type=SectionType.TEXT,
                    content="Content here",
                ),
            ],
        )
        result = render_report_to_html_document(report)

        assert "<!DOCTYPE html>" in result
        assert "<title>Full Report</title>" in result
        assert "Content here" in result


class TestSimpleMarkdownToHtml:
    """Tests for _simple_markdown_to_html fallback."""

    def test_converts_headings(self):
        """Converts markdown headings."""
        md = "# H1\n## H2\n### H3\n#### H4"
        result = _simple_markdown_to_html(md)

        assert "<h1>H1</h1>" in result
        assert "<h2>H2</h2>" in result
        assert "<h3>H3</h3>" in result
        assert "<h4>H4</h4>" in result

    def test_converts_lists(self):
        """Converts markdown lists."""
        md = "- Item 1\n- Item 2"
        result = _simple_markdown_to_html(md)

        assert "<ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "</ul>" in result

    def test_converts_paragraphs(self):
        """Converts plain text to paragraphs."""
        md = "This is a paragraph."
        result = _simple_markdown_to_html(md)

        assert "<p>This is a paragraph.</p>" in result

    def test_converts_horizontal_rules(self):
        """Converts horizontal rules."""
        md = "Before\n---\nAfter"
        result = _simple_markdown_to_html(md)

        assert "<hr>" in result

    def test_closes_lists_on_blank_line(self):
        """Closes lists when blank line encountered."""
        md = "- Item\n\nParagraph"
        result = _simple_markdown_to_html(md)

        assert "</ul>" in result
        assert "<p>Paragraph</p>" in result


class TestRenderMarkdownToHtmlBody:
    """Tests for render_markdown_to_html_body."""

    def test_converts_basic_markdown(self):
        """Converts basic markdown to HTML."""
        md = "# Title\n\nSome text."
        result = render_markdown_to_html_body(md)

        assert "Title" in result
        assert "Some text" in result

    def test_handles_tables_when_markdown_available(self):
        """Handles tables when markdown library is available."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = render_markdown_to_html_body(md)

        assert "<table>" in result or "<p>" in result
