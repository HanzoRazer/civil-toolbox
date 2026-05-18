"""Tests for PDF export functionality."""

import tempfile
from pathlib import Path

import pytest

from civil_toolbox.reporting.pdf import (
    PdfExportUnavailableError,
    export_report_to_pdf,
    export_markdown_to_pdf,
    export_html_to_pdf,
    is_pdf_export_available,
    _check_weasyprint_available,
)
from civil_toolbox.reporting.models import (
    Report,
    ReportMetadata,
    ReportSection,
    ReportTable,
    ReportType,
    SectionType,
)
from civil_toolbox.reporting.errors import RenderingError


def weasyprint_available():
    """Check if weasyprint is available for tests."""
    try:
        import weasyprint  # noqa: F401
        return True
    except ImportError:
        return False


requires_weasyprint = pytest.mark.skipif(
    not weasyprint_available(),
    reason="WeasyPrint not installed",
)


class TestIsPdfExportAvailable:
    """Tests for is_pdf_export_available."""

    def test_returns_bool(self):
        """Returns a boolean value."""
        result = is_pdf_export_available()
        assert isinstance(result, bool)

    def test_matches_import_check(self):
        """Result matches direct import check."""
        expected = weasyprint_available()
        assert is_pdf_export_available() == expected


class TestCheckWeasyprintAvailable:
    """Tests for _check_weasyprint_available."""

    @pytest.mark.skipif(
        weasyprint_available(),
        reason="Test only runs when WeasyPrint is NOT installed",
    )
    def test_raises_when_unavailable(self):
        """Raises PdfExportUnavailableError when WeasyPrint not installed."""
        with pytest.raises(PdfExportUnavailableError) as exc_info:
            _check_weasyprint_available()

        assert "weasyprint" in str(exc_info.value).lower()

    @requires_weasyprint
    def test_passes_when_available(self):
        """Passes silently when WeasyPrint is installed."""
        _check_weasyprint_available()


class TestPdfExportUnavailableError:
    """Tests for PdfExportUnavailableError."""

    def test_is_rendering_error(self):
        """Is a subclass of RenderingError."""
        error = PdfExportUnavailableError()
        assert isinstance(error, RenderingError)

    def test_default_message(self):
        """Has a default message."""
        error = PdfExportUnavailableError()
        assert "weasyprint" in str(error).lower()

    def test_custom_message(self):
        """Accepts custom message."""
        error = PdfExportUnavailableError("Custom error")
        assert "Custom error" in str(error)


class TestExportReportToPdf:
    """Tests for export_report_to_pdf."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing."""
        return Report(
            metadata=ReportMetadata(
                title="Test Report",
                report_type=ReportType.PROJECT_SUMMARY,
                project_name="Test Project",
                author="Test Author",
            ),
            sections=[
                ReportSection(
                    section_type=SectionType.HEADING,
                    title="Introduction",
                    level=2,
                ),
                ReportSection(
                    section_type=SectionType.TEXT,
                    content="This is a test report.",
                ),
                ReportSection(
                    section_type=SectionType.TABLE,
                    table=ReportTable(
                        headers=["Name", "Value"],
                        rows=[["A", "100"], ["B", "200"]],
                        title="Results",
                    ),
                ),
                ReportSection(
                    section_type=SectionType.LIST,
                    title="Items",
                    items=["First item", "Second item"],
                ),
                ReportSection(
                    section_type=SectionType.ASSUMPTIONS,
                    title="Assumptions",
                    items=["Steady state conditions"],
                ),
                ReportSection(
                    section_type=SectionType.WARNINGS,
                    title="Warnings",
                    items=["Area exceeds limit"],
                ),
                ReportSection(
                    section_type=SectionType.REFERENCES,
                    title="References",
                    items=["TR-55 (1986)"],
                ),
            ],
        )

    @pytest.mark.skipif(
        weasyprint_available(),
        reason="Test only runs when WeasyPrint is NOT installed",
    )
    def test_raises_when_weasyprint_unavailable(self, sample_report):
        """Raises PdfExportUnavailableError when WeasyPrint not installed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            with pytest.raises(PdfExportUnavailableError):
                export_report_to_pdf(sample_report, path)

    @requires_weasyprint
    def test_creates_pdf_file(self, sample_report):
        """Creates a PDF file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            result = export_report_to_pdf(sample_report, path)

            assert result.exists()
            assert result.suffix == ".pdf"
            assert result.stat().st_size > 0

    @requires_weasyprint
    def test_returns_path(self, sample_report):
        """Returns the output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.pdf"

            result = export_report_to_pdf(sample_report, path)

            assert result == path

    @requires_weasyprint
    def test_accepts_string_path(self, sample_report):
        """Accepts string path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "test.pdf")

            result = export_report_to_pdf(sample_report, path)

            assert Path(result).exists()

    @requires_weasyprint
    def test_pdf_is_valid(self, sample_report):
        """Generated PDF has valid PDF header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            export_report_to_pdf(sample_report, path)

            with open(path, "rb") as f:
                header = f.read(8)
                assert header.startswith(b"%PDF-")


class TestExportMarkdownToPdf:
    """Tests for export_markdown_to_pdf."""

    @pytest.fixture
    def sample_markdown(self):
        """Sample markdown content for testing."""
        return """# Report Title

## Introduction

This is a test report with some content.

### Details

- Item 1
- Item 2
- Item 3

| Column A | Column B |
|----------|----------|
| Value 1  | Value 2  |

---

**Note:** This is important.
"""

    @pytest.mark.skipif(
        weasyprint_available(),
        reason="Test only runs when WeasyPrint is NOT installed",
    )
    def test_raises_when_weasyprint_unavailable(self, sample_markdown):
        """Raises PdfExportUnavailableError when WeasyPrint not installed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            with pytest.raises(PdfExportUnavailableError):
                export_markdown_to_pdf(sample_markdown, path)

    @requires_weasyprint
    def test_creates_pdf_file(self, sample_markdown):
        """Creates a PDF file from markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            result = export_markdown_to_pdf(sample_markdown, path)

            assert result.exists()
            assert result.stat().st_size > 0

    @requires_weasyprint
    def test_accepts_custom_title(self, sample_markdown):
        """Accepts custom document title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            result = export_markdown_to_pdf(
                sample_markdown,
                path,
                title="Custom Title",
            )

            assert result.exists()

    @requires_weasyprint
    def test_returns_path(self, sample_markdown):
        """Returns the output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.pdf"

            result = export_markdown_to_pdf(sample_markdown, path)

            assert result == path


class TestExportHtmlToPdf:
    """Tests for export_html_to_pdf."""

    @pytest.fixture
    def sample_html(self):
        """Sample HTML content for testing."""
        return """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<h1>Test Document</h1>
<p>This is a test.</p>
</body>
</html>"""

    @pytest.mark.skipif(
        weasyprint_available(),
        reason="Test only runs when WeasyPrint is NOT installed",
    )
    def test_raises_when_weasyprint_unavailable(self, sample_html):
        """Raises PdfExportUnavailableError when WeasyPrint not installed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            with pytest.raises(PdfExportUnavailableError):
                export_html_to_pdf(sample_html, path)

    @requires_weasyprint
    def test_creates_pdf_file(self, sample_html):
        """Creates a PDF file from HTML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.pdf"

            result = export_html_to_pdf(sample_html, path)

            assert result.exists()
            assert result.stat().st_size > 0


class TestPdfDeterminism:
    """Tests for PDF output determinism."""

    @requires_weasyprint
    def test_same_report_produces_similar_size(self):
        """Same report produces PDFs of similar size."""
        report = Report(
            metadata=ReportMetadata(
                title="Determinism Test",
                report_type=ReportType.PROJECT_SUMMARY,
            ),
            sections=[
                ReportSection(
                    section_type=SectionType.TEXT,
                    content="Test content for determinism.",
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "test1.pdf"
            path2 = Path(tmpdir) / "test2.pdf"

            export_report_to_pdf(report, path1)
            export_report_to_pdf(report, path2)

            size1 = path1.stat().st_size
            size2 = path2.stat().st_size

            assert abs(size1 - size2) < 1000


class TestPdfContent:
    """Tests for PDF content coverage."""

    @requires_weasyprint
    def test_all_section_types_render(self):
        """All section types can be rendered to PDF."""
        report = Report(
            metadata=ReportMetadata(
                title="Full Coverage Test",
                report_type=ReportType.PROJECT_SUMMARY,
            ),
            sections=[
                ReportSection(section_type=SectionType.TITLE, title="Title"),
                ReportSection(section_type=SectionType.HEADING, title="H2", level=2),
                ReportSection(section_type=SectionType.TEXT, content="Text"),
                ReportSection(
                    section_type=SectionType.LIST,
                    items=["A", "B"],
                ),
                ReportSection(
                    section_type=SectionType.TABLE,
                    table=ReportTable(headers=["X"], rows=[["Y"]]),
                ),
                ReportSection(
                    section_type=SectionType.ASSUMPTIONS,
                    title="Assumptions",
                    items=["Assume this"],
                ),
                ReportSection(
                    section_type=SectionType.WARNINGS,
                    title="Warnings",
                    items=["Warning here"],
                ),
                ReportSection(
                    section_type=SectionType.REFERENCES,
                    title="References",
                    items=["Reference 1"],
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "coverage.pdf"

            result = export_report_to_pdf(report, path)

            assert result.exists()
            assert result.stat().st_size > 0
