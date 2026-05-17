# Reporting Engine

Generate engineering reports from domain objects and comparison results.

## Report Types

| Type | Function | Description |
|------|----------|-------------|
| Project Summary | `generate_project_summary_report()` | Project metadata and scenario overview |
| Scenario Comparison | `generate_scenario_comparison_report()` | Comparison results between scenarios |
| Calculation Appendix | `generate_calculation_appendix()` | Detailed calculation documentation |

## Quick Start

```python
from civil_toolbox.reporting import (
    generate_project_summary_report,
    generate_scenario_comparison_report,
    generate_calculation_appendix,
    render_full_report_markdown,
)

# Project summary
report = generate_project_summary_report(project)
markdown = render_full_report_markdown(report)

# Scenario comparison
report = generate_scenario_comparison_report(comparison_result)
markdown = render_full_report_markdown(report)

# Calculation appendix
report = generate_calculation_appendix(scenario)
markdown = render_full_report_markdown(report)
```

## Output Formats

### Markdown (Current)

Markdown is the primary output format:

```python
from civil_toolbox.reporting import render_full_report_markdown

markdown = render_full_report_markdown(report)
print(markdown)

# Or without YAML metadata header
markdown = render_full_report_markdown(report, include_metadata_header=False)
```

### PDF (Planned)

PDF export is planned for a future release. The current architecture separates report data from rendering, enabling future format support.

## Report Structure

Reports are composed of sections:

```python
from civil_toolbox.reporting import (
    Report,
    ReportMetadata,
    ReportSection,
    ReportType,
    SectionType,
)

# Create report manually
metadata = ReportMetadata(
    title="Custom Report",
    report_type=ReportType.PROJECT_SUMMARY,
)

report = Report(metadata=metadata)
report.add_section(ReportSection(
    section_type=SectionType.HEADING,
    title="Introduction",
    level=1,
))
report.add_section(ReportSection(
    section_type=SectionType.TEXT,
    content="This is paragraph text.",
))
```

### Section Types

| Type | Content | Use Case |
|------|---------|----------|
| `HEADING` | Title with level | Section headers |
| `TEXT` | Paragraph content | Narrative text |
| `LIST` | Bullet items | Assumptions, warnings |
| `TABLE` | ReportTable | Data tables |
| `CALCULATION` | Calculation details | Appendix entries |
| `ASSUMPTIONS` | Assumption list | Engineering assumptions |
| `WARNINGS` | Warning list | Validation warnings |
| `REFERENCES` | Reference list | Engineering references |
| `FIGURE_PLACEHOLDER` | Figure marker | Image locations |

## Tables

Tables can be created programmatically:

```python
from civil_toolbox.reporting import (
    ReportTable,
    create_key_value_table,
    create_metric_comparison_table,
    render_table_markdown,
)

# Key-value table
table = create_key_value_table([
    ("Project", "Downtown Drainage"),
    ("Date", "2026-05-17"),
])

# Comparison table
table = create_metric_comparison_table(
    baseline_name="Existing",
    comparison_name="Proposed",
    metrics=[
        {
            "metric": "Peak Flow (cfs)",
            "baseline": "300.0 cfs",
            "comparison": "370.0 cfs",
            "delta": "+70.0 cfs",
            "percent": "+23.3%",
        },
    ],
)

# Render to Markdown
markdown = render_table_markdown(table)
```

## Formatters

Value formatting utilities:

```python
from civil_toolbox.reporting import (
    format_number,
    format_percent,
    format_delta,
    format_value_with_unit,
)

format_number(1234.56, precision=2)           # "1,234.56"
format_percent(23.5, include_sign=True)       # "+23.5%"
format_delta(70.0, unit="cfs", precision=1)   # "+70.0 cfs"
format_value_with_unit(300.0, "cfs")          # "300.00 cfs"
format_value_with_unit(None, "cfs")           # "—"
```

## Section Builders

Convenience functions for common sections:

```python
from civil_toolbox.reporting import (
    create_heading,
    create_text,
    create_list,
    create_assumptions_section,
    create_warnings_section,
    create_references_section,
)

heading = create_heading("Results", level=2)
paragraph = create_text("Analysis complete.")
bullets = create_list(["Item 1", "Item 2"])
assumptions = create_assumptions_section([
    "Steady-state conditions",
    "Uniform rainfall distribution",
])
```

## Serialization

Reports are fully serializable:

```python
# To dictionary
data = report.to_dict()

# To JSON
import json
json_str = json.dumps(data, indent=2)

# From dictionary
restored = Report.from_dict(data)
```

## Design Principles

1. **No calculations** — Reporting only formats existing data
2. **Deterministic** — Same input produces identical output
3. **Testable** — Tables render to plain strings
4. **Composable** — Sections combine into reports
5. **Format-agnostic** — Report data separates from rendering

## API Reference

### Report Generators

- `generate_project_summary_report(project)` — Project overview
- `generate_scenario_comparison_report(comparison)` — Comparison report
- `generate_calculation_appendix(scenario)` — Calculation details

### Renderers

- `render_full_report_markdown(report)` — Complete Markdown document
- `render_report_markdown(report)` — Markdown without metadata header
- `render_table_markdown(table)` — Single table to Markdown

### Models

- `Report` — Complete report container
- `ReportMetadata` — Title, type, timestamps
- `ReportSection` — Content section
- `ReportTable` — Tabular data
- `ReportFigurePlaceholder` — Image marker

### Errors

- `ReportingError` — Base exception
- `InvalidReportDataError` — Invalid data
- `MissingProjectError` — Project required
- `MissingScenarioError` — Scenario required
- `RenderingError` — Rendering failure
