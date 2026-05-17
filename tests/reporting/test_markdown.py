"""Tests for Markdown rendering."""

import pytest

from civil_toolbox.reporting.markdown import (
    render_report_markdown,
    render_section_markdown,
    render_metadata_header,
    render_full_report_markdown,
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


class TestRenderSectionMarkdown:
    """Tests for render_section_markdown."""

    def test_renders_title(self):
        """Renders title section."""
        section = ReportSection(
            section_type=SectionType.TITLE,
            title="Report Title",
        )
        lines = render_section_markdown(section)

        assert "# Report Title" in lines

    def test_renders_heading(self):
        """Renders heading with correct level."""
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Section Title",
            level=2,
        )
        lines = render_section_markdown(section)

        assert "## Section Title" in lines

    def test_renders_heading_level_3(self):
        """Renders level 3 heading."""
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Subsection",
            level=3,
        )
        lines = render_section_markdown(section)

        assert "### Subsection" in lines

    def test_renders_text(self):
        """Renders text paragraph."""
        section = ReportSection(
            section_type=SectionType.TEXT,
            content="This is a paragraph.",
        )
        lines = render_section_markdown(section)

        assert "This is a paragraph." in lines

    def test_renders_list(self):
        """Renders bullet list."""
        section = ReportSection(
            section_type=SectionType.LIST,
            items=["Item A", "Item B", "Item C"],
        )
        lines = render_section_markdown(section)

        assert "- Item A" in lines
        assert "- Item B" in lines
        assert "- Item C" in lines

    def test_renders_list_with_title(self):
        """Renders list with title."""
        section = ReportSection(
            section_type=SectionType.LIST,
            title="Inputs",
            items=["Value 1", "Value 2"],
        )
        lines = render_section_markdown(section)

        assert "**Inputs:**" in lines

    def test_renders_table(self):
        """Renders table section."""
        table = ReportTable(
            headers=["Name", "Value"],
            rows=[["A", "100"]],
        )
        section = ReportSection(
            section_type=SectionType.TABLE,
            table=table,
        )
        lines = render_section_markdown(section)
        output = "\n".join(lines)

        assert "| Name | Value |" in output
        assert "| A | 100 |" in output

    def test_renders_assumptions(self):
        """Renders assumptions list."""
        section = ReportSection(
            section_type=SectionType.ASSUMPTIONS,
            title="Assumptions",
            items=["Steady state", "Uniform rainfall"],
        )
        lines = render_section_markdown(section)

        assert "**Assumptions:**" in lines
        assert "- Steady state" in lines

    def test_renders_warnings_with_emoji(self):
        """Renders warnings with warning emoji."""
        section = ReportSection(
            section_type=SectionType.WARNINGS,
            title="Warnings",
            items=["Area exceeds limit"],
        )
        lines = render_section_markdown(section)

        assert "⚠️" in "\n".join(lines)

    def test_renders_references_numbered(self):
        """Renders references as numbered list."""
        section = ReportSection(
            section_type=SectionType.REFERENCES,
            title="References",
            items=["TR-55, NRCS (1986)", "HEC-22, FHWA (2009)"],
        )
        lines = render_section_markdown(section)

        assert "1. TR-55" in "\n".join(lines)
        assert "2. HEC-22" in "\n".join(lines)

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
        lines = render_section_markdown(section)
        output = "\n".join(lines)

        assert "*[Figure: Site Plan]*" in output
        assert "drainage boundaries" in output

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
        lines = render_section_markdown(section)
        output = "\n".join(lines)

        assert "## Parent" in output
        assert "Child content" in output


class TestRenderReportMarkdown:
    """Tests for render_report_markdown."""

    def test_renders_multiple_sections(self):
        """Renders report with multiple sections."""
        metadata = ReportMetadata(
            title="Test",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(
            metadata=metadata,
            sections=[
                ReportSection(
                    section_type=SectionType.HEADING,
                    title="Introduction",
                    level=1,
                ),
                ReportSection(
                    section_type=SectionType.TEXT,
                    content="First paragraph.",
                ),
                ReportSection(
                    section_type=SectionType.HEADING,
                    title="Details",
                    level=2,
                ),
            ],
        )
        output = render_report_markdown(report)

        assert "# Introduction" in output
        assert "First paragraph." in output
        assert "## Details" in output

    def test_output_is_deterministic(self):
        """Output is deterministic."""
        metadata = ReportMetadata(
            title="Test",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(
            metadata=metadata,
            sections=[
                ReportSection(section_type=SectionType.TEXT, content="Hello"),
            ],
        )
        output1 = render_report_markdown(report)
        output2 = render_report_markdown(report)

        assert output1 == output2

    def test_empty_report(self):
        """Handles empty report."""
        metadata = ReportMetadata(
            title="Empty",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(metadata=metadata, sections=[])
        output = render_report_markdown(report)

        assert output == ""


class TestRenderMetadataHeader:
    """Tests for render_metadata_header."""

    def test_renders_yaml_style_header(self):
        """Renders YAML-style metadata header."""
        metadata = ReportMetadata(
            title="Test Report",
            report_type=ReportType.PROJECT_SUMMARY,
            project_name="Test Project",
        )
        report = Report(metadata=metadata)
        output = render_metadata_header(report)

        assert output.startswith("---")
        assert "title: Test Report" in output
        assert "type: project_summary" in output
        assert "project: Test Project" in output
        assert output.count("---") == 2

    def test_includes_scenarios(self):
        """Includes scenario names."""
        metadata = ReportMetadata(
            title="Test",
            report_type=ReportType.SCENARIO_COMPARISON,
            scenario_names=["Existing", "Proposed"],
        )
        report = Report(metadata=metadata)
        output = render_metadata_header(report)

        assert "scenarios: Existing, Proposed" in output

    def test_includes_author_and_org(self):
        """Includes author and organization."""
        metadata = ReportMetadata(
            title="Test",
            report_type=ReportType.PROJECT_SUMMARY,
            author="Engineer",
            organization="Acme Corp",
        )
        report = Report(metadata=metadata)
        output = render_metadata_header(report)

        assert "author: Engineer" in output
        assert "organization: Acme Corp" in output


class TestRenderFullReportMarkdown:
    """Tests for render_full_report_markdown."""

    def test_includes_metadata_header(self):
        """Includes metadata header by default."""
        metadata = ReportMetadata(
            title="Full Report",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(
            metadata=metadata,
            sections=[
                ReportSection(section_type=SectionType.TEXT, content="Content"),
            ],
        )
        output = render_full_report_markdown(report)

        assert output.startswith("---")
        assert "title: Full Report" in output
        assert "Content" in output

    def test_without_metadata_header(self):
        """Can exclude metadata header."""
        metadata = ReportMetadata(
            title="Simple",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(
            metadata=metadata,
            sections=[
                ReportSection(section_type=SectionType.TEXT, content="Content"),
            ],
        )
        output = render_full_report_markdown(report, include_metadata_header=False)

        assert not output.startswith("---")
        assert "Content" in output

    def test_output_is_valid_markdown(self):
        """Output is syntactically valid Markdown."""
        metadata = ReportMetadata(
            title="Valid",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(
            metadata=metadata,
            sections=[
                ReportSection(
                    section_type=SectionType.HEADING,
                    title="Section",
                    level=2,
                ),
                ReportSection(
                    section_type=SectionType.TABLE,
                    table=ReportTable(
                        headers=["A", "B"],
                        rows=[["1", "2"]],
                    ),
                ),
                ReportSection(
                    section_type=SectionType.LIST,
                    items=["Item 1", "Item 2"],
                ),
            ],
        )
        output = render_full_report_markdown(report)

        assert "## Section" in output
        assert "| A | B |" in output
        assert "- Item 1" in output
