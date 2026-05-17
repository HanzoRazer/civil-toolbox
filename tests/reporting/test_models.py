"""Tests for reporting data models."""

import pytest
from datetime import datetime, timezone

from civil_toolbox.reporting.models import (
    ReportType,
    SectionType,
    ReportMetadata,
    ReportTable,
    ReportFigurePlaceholder,
    ReportSection,
    Report,
)


class TestReportType:
    """Tests for ReportType enum."""

    def test_all_types_defined(self):
        """All report types exist."""
        assert ReportType.PROJECT_SUMMARY.value == "project_summary"
        assert ReportType.SCENARIO_COMPARISON.value == "scenario_comparison"
        assert ReportType.CALCULATION_APPENDIX.value == "calculation_appendix"


class TestSectionType:
    """Tests for SectionType enum."""

    def test_all_section_types_defined(self):
        """All section types exist."""
        expected = [
            "title", "metadata", "summary", "table", "text", "list",
            "heading", "calculation", "assumptions", "warnings",
            "references", "figure_placeholder"
        ]
        actual = [t.value for t in SectionType]
        for e in expected:
            assert e in actual


class TestReportMetadata:
    """Tests for ReportMetadata."""

    def test_creates_with_required_fields(self):
        """Creates metadata with required fields."""
        metadata = ReportMetadata(
            title="Test Report",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        assert metadata.title == "Test Report"
        assert metadata.report_type == ReportType.PROJECT_SUMMARY
        assert isinstance(metadata.generated_at, datetime)

    def test_creates_with_all_fields(self):
        """Creates metadata with all fields."""
        metadata = ReportMetadata(
            title="Full Report",
            report_type=ReportType.SCENARIO_COMPARISON,
            project_name="Test Project",
            project_id="proj-123",
            scenario_names=["Existing", "Proposed"],
            author="Engineer",
            organization="Acme Corp",
        )
        assert metadata.project_name == "Test Project"
        assert metadata.scenario_names == ["Existing", "Proposed"]
        assert metadata.author == "Engineer"

    def test_to_dict(self):
        """Serializes to dictionary."""
        metadata = ReportMetadata(
            title="Test Report",
            report_type=ReportType.PROJECT_SUMMARY,
            project_name="Test",
        )
        data = metadata.to_dict()
        assert data["title"] == "Test Report"
        assert data["report_type"] == "project_summary"
        assert data["project_name"] == "Test"
        assert "generated_at" in data

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "title": "Test Report",
            "report_type": "scenario_comparison",
            "generated_at": "2026-05-17T12:00:00+00:00",
            "project_name": "Test",
        }
        metadata = ReportMetadata.from_dict(data)
        assert metadata.title == "Test Report"
        assert metadata.report_type == ReportType.SCENARIO_COMPARISON
        assert metadata.project_name == "Test"

    def test_round_trip(self):
        """Round-trip serialization preserves data."""
        original = ReportMetadata(
            title="Round Trip",
            report_type=ReportType.CALCULATION_APPENDIX,
            project_name="Test",
            scenario_names=["A", "B"],
        )
        restored = ReportMetadata.from_dict(original.to_dict())
        assert restored.title == original.title
        assert restored.report_type == original.report_type
        assert restored.scenario_names == original.scenario_names


class TestReportTable:
    """Tests for ReportTable."""

    def test_creates_with_headers_and_rows(self):
        """Creates table with headers and rows."""
        table = ReportTable(
            headers=["Name", "Value"],
            rows=[["Area A", "100 cfs"], ["Area B", "200 cfs"]],
        )
        assert table.headers == ["Name", "Value"]
        assert len(table.rows) == 2

    def test_default_alignments(self):
        """Default alignments are left."""
        table = ReportTable(
            headers=["A", "B", "C"],
            rows=[["1", "2", "3"]],
        )
        assert table.alignments == ["left", "left", "left"]

    def test_custom_alignments(self):
        """Accepts custom alignments."""
        table = ReportTable(
            headers=["Name", "Value"],
            rows=[["Test", "100"]],
            alignments=["left", "right"],
        )
        assert table.alignments == ["left", "right"]

    def test_alignment_count_mismatch_raises(self):
        """Raises when alignment count doesn't match headers."""
        with pytest.raises(ValueError, match="Alignments count"):
            ReportTable(
                headers=["A", "B", "C"],
                rows=[],
                alignments=["left", "right"],
            )

    def test_with_title_and_footer(self):
        """Creates table with title and footer."""
        table = ReportTable(
            headers=["Col"],
            rows=[["Data"]],
            title="Table 1: Results",
            footer="Note: Values in cfs",
        )
        assert table.title == "Table 1: Results"
        assert table.footer == "Note: Values in cfs"

    def test_to_dict(self):
        """Serializes to dictionary."""
        table = ReportTable(
            headers=["A", "B"],
            rows=[["1", "2"]],
            title="Test",
        )
        data = table.to_dict()
        assert data["headers"] == ["A", "B"]
        assert data["rows"] == [["1", "2"]]
        assert data["title"] == "Test"

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "headers": ["X", "Y"],
            "rows": [["a", "b"]],
            "alignments": ["left", "center"],
        }
        table = ReportTable.from_dict(data)
        assert table.headers == ["X", "Y"]
        assert table.alignments == ["left", "center"]


class TestReportFigurePlaceholder:
    """Tests for ReportFigurePlaceholder."""

    def test_creates_with_required_fields(self):
        """Creates placeholder with required fields."""
        figure = ReportFigurePlaceholder(
            figure_id="fig-1",
            caption="Site Plan",
        )
        assert figure.figure_id == "fig-1"
        assert figure.caption == "Site Plan"

    def test_creates_with_all_fields(self):
        """Creates placeholder with all fields."""
        figure = ReportFigurePlaceholder(
            figure_id="fig-2",
            caption="Drainage Map",
            description="Shows drainage area boundaries",
            suggested_filename="drainage_map.png",
        )
        assert figure.description == "Shows drainage area boundaries"
        assert figure.suggested_filename == "drainage_map.png"

    def test_to_dict(self):
        """Serializes to dictionary."""
        figure = ReportFigurePlaceholder(
            figure_id="fig-1",
            caption="Test",
        )
        data = figure.to_dict()
        assert data["figure_id"] == "fig-1"
        assert data["caption"] == "Test"

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "figure_id": "fig-3",
            "caption": "Flow Diagram",
            "description": "Shows flow paths",
        }
        figure = ReportFigurePlaceholder.from_dict(data)
        assert figure.figure_id == "fig-3"
        assert figure.description == "Shows flow paths"


class TestReportSection:
    """Tests for ReportSection."""

    def test_creates_heading_section(self):
        """Creates a heading section."""
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Introduction",
            level=2,
        )
        assert section.section_type == SectionType.HEADING
        assert section.title == "Introduction"
        assert section.level == 2

    def test_creates_text_section(self):
        """Creates a text section."""
        section = ReportSection(
            section_type=SectionType.TEXT,
            content="This is paragraph text.",
        )
        assert section.section_type == SectionType.TEXT
        assert section.content == "This is paragraph text."

    def test_creates_list_section(self):
        """Creates a list section."""
        section = ReportSection(
            section_type=SectionType.LIST,
            items=["Item 1", "Item 2", "Item 3"],
        )
        assert section.section_type == SectionType.LIST
        assert len(section.items) == 3

    def test_creates_table_section(self):
        """Creates a table section."""
        table = ReportTable(headers=["A"], rows=[["1"]])
        section = ReportSection(
            section_type=SectionType.TABLE,
            table=table,
        )
        assert section.table is not None
        assert section.table.headers == ["A"]

    def test_creates_figure_section(self):
        """Creates a figure placeholder section."""
        figure = ReportFigurePlaceholder(figure_id="f1", caption="Fig 1")
        section = ReportSection(
            section_type=SectionType.FIGURE_PLACEHOLDER,
            figure=figure,
        )
        assert section.figure is not None
        assert section.figure.figure_id == "f1"

    def test_nested_subsections(self):
        """Creates section with nested subsections."""
        subsection = ReportSection(
            section_type=SectionType.TEXT,
            content="Nested content",
        )
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Parent",
            subsections=[subsection],
        )
        assert len(section.subsections) == 1
        assert section.subsections[0].content == "Nested content"

    def test_to_dict(self):
        """Serializes to dictionary."""
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Test",
            level=3,
        )
        data = section.to_dict()
        assert data["section_type"] == "heading"
        assert data["title"] == "Test"
        assert data["level"] == 3

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "section_type": "text",
            "content": "Hello",
        }
        section = ReportSection.from_dict(data)
        assert section.section_type == SectionType.TEXT
        assert section.content == "Hello"

    def test_round_trip_with_table(self):
        """Round-trip with nested table."""
        table = ReportTable(headers=["X"], rows=[["Y"]])
        original = ReportSection(
            section_type=SectionType.TABLE,
            table=table,
        )
        restored = ReportSection.from_dict(original.to_dict())
        assert restored.table is not None
        assert restored.table.headers == ["X"]


class TestReport:
    """Tests for Report."""

    def test_creates_with_metadata(self):
        """Creates report with metadata."""
        metadata = ReportMetadata(
            title="Test Report",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(metadata=metadata)
        assert report.metadata.title == "Test Report"
        assert report.sections == []

    def test_add_section(self):
        """Adds sections to report."""
        metadata = ReportMetadata(
            title="Test",
            report_type=ReportType.PROJECT_SUMMARY,
        )
        report = Report(metadata=metadata)
        section = ReportSection(
            section_type=SectionType.HEADING,
            title="Section 1",
        )
        report.add_section(section)
        assert len(report.sections) == 1
        assert report.sections[0].title == "Section 1"

    def test_to_dict(self):
        """Serializes to dictionary."""
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
        data = report.to_dict()
        assert data["metadata"]["title"] == "Test"
        assert len(data["sections"]) == 1

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "metadata": {
                "title": "Loaded",
                "report_type": "calculation_appendix",
                "generated_at": "2026-05-17T00:00:00+00:00",
            },
            "sections": [
                {"section_type": "text", "content": "Content"},
            ],
        }
        report = Report.from_dict(data)
        assert report.metadata.title == "Loaded"
        assert len(report.sections) == 1

    def test_round_trip(self):
        """Round-trip serialization preserves structure."""
        metadata = ReportMetadata(
            title="Full Report",
            report_type=ReportType.SCENARIO_COMPARISON,
            project_name="Test Project",
        )
        original = Report(
            metadata=metadata,
            sections=[
                ReportSection(
                    section_type=SectionType.HEADING,
                    title="Summary",
                    level=2,
                ),
                ReportSection(
                    section_type=SectionType.TABLE,
                    table=ReportTable(
                        headers=["A", "B"],
                        rows=[["1", "2"]],
                    ),
                ),
            ],
        )
        restored = Report.from_dict(original.to_dict())
        assert restored.metadata.title == "Full Report"
        assert len(restored.sections) == 2
        assert restored.sections[1].table is not None
