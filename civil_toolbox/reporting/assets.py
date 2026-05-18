"""CSS and styling assets for PDF reports."""

from __future__ import annotations


REPORT_CSS = """
@page {
    size: letter;
    margin: 1in 0.75in;
    @top-center {
        content: string(report-title);
        font-size: 9pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

@page :first {
    @top-center {
        content: none;
    }
}

body {
    font-family: "Segoe UI", Calibri, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #333;
}

h1 {
    string-set: report-title content();
    font-size: 18pt;
    font-weight: 600;
    color: #1a1a1a;
    margin-top: 0;
    margin-bottom: 12pt;
    border-bottom: 2px solid #333;
    padding-bottom: 8pt;
}

h2 {
    font-size: 14pt;
    font-weight: 600;
    color: #1a1a1a;
    margin-top: 18pt;
    margin-bottom: 10pt;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4pt;
}

h3 {
    font-size: 12pt;
    font-weight: 600;
    color: #333;
    margin-top: 14pt;
    margin-bottom: 8pt;
}

h4 {
    font-size: 11pt;
    font-weight: 600;
    color: #444;
    margin-top: 12pt;
    margin-bottom: 6pt;
}

p {
    margin: 0 0 10pt 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 10pt;
}

th, td {
    border: 1px solid #ccc;
    padding: 6pt 8pt;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: 600;
    color: #333;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

.table-title {
    font-weight: 600;
    font-size: 10pt;
    margin-bottom: 4pt;
    color: #444;
}

.table-footer {
    font-style: italic;
    font-size: 9pt;
    color: #666;
    margin-top: 4pt;
}

.align-left {
    text-align: left;
}

.align-center {
    text-align: center;
}

.align-right {
    text-align: right;
}

ul, ol {
    margin: 8pt 0;
    padding-left: 20pt;
}

li {
    margin-bottom: 4pt;
}

.title-block {
    margin-bottom: 24pt;
}

.title-block h1 {
    margin-bottom: 16pt;
}

.metadata-block {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 4pt;
    padding: 12pt 16pt;
    margin-bottom: 18pt;
}

.metadata-block table {
    margin: 0;
    border: none;
}

.metadata-block th,
.metadata-block td {
    border: none;
    padding: 4pt 8pt;
    background-color: transparent;
}

.metadata-block th {
    width: 30%;
    color: #666;
    font-weight: normal;
}

.generated-timestamp {
    font-size: 9pt;
    color: #666;
    margin-top: 8pt;
    text-align: right;
}

.assumptions-section,
.warnings-section,
.references-section {
    margin: 16pt 0;
}

.assumptions-section .section-title,
.warnings-section .section-title,
.references-section .section-title {
    font-weight: 600;
    margin-bottom: 8pt;
}

.warnings-section {
    background-color: #fff8e6;
    border-left: 4pt solid #f0ad4e;
    padding: 10pt 14pt;
}

.warning-item {
    color: #856404;
}

.warning-icon {
    margin-right: 4pt;
}

.figure-placeholder {
    border: 2px dashed #ccc;
    background-color: #fafafa;
    padding: 20pt;
    margin: 16pt 0;
    text-align: center;
    color: #666;
}

.figure-caption {
    font-style: italic;
    margin-top: 8pt;
}

.calculation-section {
    page-break-inside: avoid;
    margin: 12pt 0;
    padding: 10pt;
    background-color: #fdfdfd;
    border: 1px solid #eee;
}

.appendix {
    page-break-before: always;
}

.appendix h2 {
    border-bottom: 2px solid #333;
}

code {
    font-family: "Consolas", "Monaco", monospace;
    font-size: 9pt;
    background-color: #f4f4f4;
    padding: 1pt 4pt;
    border-radius: 2pt;
}

pre {
    font-family: "Consolas", "Monaco", monospace;
    font-size: 9pt;
    background-color: #f4f4f4;
    padding: 10pt;
    border-radius: 4pt;
    overflow-x: auto;
    white-space: pre-wrap;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 16pt 0;
}
"""


def get_report_css() -> str:
    """Get the CSS stylesheet for PDF reports.

    Returns:
        CSS stylesheet as a string.
    """
    return REPORT_CSS
