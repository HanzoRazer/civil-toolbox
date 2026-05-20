"""PDF export for reports.

This module provides PDF export capabilities for the reporting engine.
PDF export consumes existing Report objects or markdown content —
it does not run calculations.

The PDF pipeline uses WeasyPrint for HTML-to-PDF conversion.
When WeasyPrint is unavailable, a PdfExportUnavailableError is raised.

Example:
    >>> from civil_toolbox.reporting import generate_project_summary_report
    >>> from civil_toolbox.reporting.pdf import export_report_to_pdf
    >>>
    >>> report = generate_project_summary_report(project)
    >>> export_report_to_pdf(report, "output.pdf")
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from civil_toolbox.reporting.errors import RenderingError
from civil_toolbox.reporting.templates import (
    render_report_to_html_document,
    render_html_document,
    render_markdown_to_html_body,
)

if TYPE_CHECKING:
    from civil_toolbox.reporting.models import Report


class PdfExportUnavailableError(RenderingError):
    """Raised when PDF export dependencies are not available."""

    def __init__(self, message: str = "PDF export requires weasyprint"):
        super().__init__(message)


def _check_weasyprint_available() -> None:
    """Check if WeasyPrint is available.

    Raises:
        PdfExportUnavailableError: If WeasyPrint is not installed.
    """
    try:
        import weasyprint  # noqa: F401
    except ImportError:
        raise PdfExportUnavailableError(
            "PDF export requires weasyprint. Install with: pip install weasyprint"
        )


def export_report_to_pdf(
    report: Report,
    path: str | Path,
    *,
    optimize_images: bool = True,
) -> Path:
    """Export a Report object to PDF.

    Args:
        report: The Report to export.
        path: Output file path.
        optimize_images: Whether to optimize embedded images.

    Returns:
        Path to the generated PDF file.

    Raises:
        PdfExportUnavailableError: If WeasyPrint is not installed.
        RenderingError: If PDF rendering fails.
    """
    _check_weasyprint_available()

    import weasyprint

    output_path = Path(path)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise RenderingError(f"Failed to create output directory: {e}") from e

    try:
        html_content = render_report_to_html_document(report)

        html_doc = weasyprint.HTML(string=html_content)

        html_doc.write_pdf(
            output_path,
            optimize_images=optimize_images,
        )

        return output_path

    except Exception as e:
        if isinstance(e, PdfExportUnavailableError):
            raise
        raise RenderingError(f"Failed to render PDF: {e}") from e


def export_markdown_to_pdf(
    markdown_content: str,
    path: str | Path,
    *,
    title: str = "Report",
    optimize_images: bool = True,
) -> Path:
    """Export markdown content to PDF.

    Args:
        markdown_content: Markdown text to convert.
        path: Output file path.
        title: Document title for the PDF.
        optimize_images: Whether to optimize embedded images.

    Returns:
        Path to the generated PDF file.

    Raises:
        PdfExportUnavailableError: If WeasyPrint is not installed.
        RenderingError: If markdown is empty or PDF rendering fails.
    """
    if not markdown_content or not markdown_content.strip():
        raise RenderingError("Cannot export empty or whitespace-only markdown to PDF")

    _check_weasyprint_available()

    import weasyprint

    output_path = Path(path)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise RenderingError(f"Failed to create output directory: {e}") from e

    try:
        html_body = render_markdown_to_html_body(markdown_content)
        html_content = render_html_document(html_body, title=title)

        html_doc = weasyprint.HTML(string=html_content)

        html_doc.write_pdf(
            output_path,
            optimize_images=optimize_images,
        )

        return output_path

    except Exception as e:
        if isinstance(e, PdfExportUnavailableError):
            raise
        raise RenderingError(f"Failed to render PDF: {e}") from e


def export_html_to_pdf(
    html_content: str,
    path: str | Path,
    *,
    optimize_images: bool = True,
) -> Path:
    """Export raw HTML content to PDF.

    This is a lower-level function for custom HTML content.

    Args:
        html_content: Complete HTML document string.
        path: Output file path.
        optimize_images: Whether to optimize embedded images.

    Returns:
        Path to the generated PDF file.

    Raises:
        PdfExportUnavailableError: If WeasyPrint is not installed.
        RenderingError: If PDF rendering fails.
    """
    _check_weasyprint_available()

    import weasyprint

    output_path = Path(path)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise RenderingError(f"Failed to create output directory: {e}") from e

    try:
        html_doc = weasyprint.HTML(string=html_content)

        html_doc.write_pdf(
            output_path,
            optimize_images=optimize_images,
        )

        return output_path

    except Exception as e:
        if isinstance(e, PdfExportUnavailableError):
            raise
        raise RenderingError(f"Failed to render PDF: {e}") from e


def is_pdf_export_available() -> bool:
    """Check if PDF export is available.

    Returns:
        True if WeasyPrint is installed, False otherwise.
    """
    try:
        import weasyprint  # noqa: F401
        return True
    except ImportError:
        return False
