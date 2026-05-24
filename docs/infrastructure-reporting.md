# Infrastructure Reporting

The infrastructure reporting module generates engineering reports from infrastructure networks and sizing check results.

## Overview

Infrastructure reporting provides:

- **Schedule tables** — Pipe, inlet, and detention facility schedules
- **Summary tables** — Element counts by type and status
- **Sizing check summaries** — Capacity check results with pass/fail status
- **Warnings appendix** — Aggregated warnings from all checks
- **Assumptions appendix** — Aggregated assumptions from all checks

**Important**: The reporting engine does not perform calculations. It formats existing data from `InfrastructureNetwork` and `InfrastructureCheckResult` objects.

## Template Integration

Infrastructure sections integrate with the existing template system:

```python
from civil_toolbox.reporting import (
    ReportTemplateContext,
    build_report_from_template,
    get_default_template_registry,
    render_full_report_markdown,
)
from civil_toolbox.infrastructure import create_example_network
from civil_toolbox.infrastructure_sizing import check_pipe_capacity

# Create network and run sizing checks
network = create_example_network()
check_results = []
for pipe in network.iter_pipes():
    result = check_pipe_capacity(pipe, design_flow_cfs=10.0)
    check_results.append(result)

# Build report from template
registry = get_default_template_registry()
template = registry.get("infrastructure_summary_report")
context = ReportTemplateContext(
    infrastructure_network=network,
    infrastructure_check_results=check_results,
)
report = build_report_from_template(template, context)
markdown = render_full_report_markdown(report)
```

## Context Setup

Add infrastructure data to the template context:

```python
from civil_toolbox.reporting import ReportTemplateContext

context = ReportTemplateContext(
    infrastructure_network=network,              # Optional
    infrastructure_check_results=check_results,  # Optional
)

# Check data availability
context.has_infrastructure_network()        # True/False
context.has_infrastructure_check_results()  # True/False
```

## Section Types

### infrastructure_summary

Displays element counts by type and status.

```python
SectionTemplate(
    id="summary",
    title="Infrastructure Summary",
    section_type="infrastructure_summary",
)
```

**Requires**: `infrastructure_network`

**Output table columns**:
| Element Type | Count | Existing | Proposed | Future | Other |

### infrastructure_schedule

Combined schedule showing pipes, inlets, and detention facilities.

```python
SectionTemplate(
    id="schedule",
    title="Infrastructure Schedule",
    section_type="infrastructure_schedule",
)
```

**Requires**: `infrastructure_network`

### pipe_schedule

Detailed pipe schedule.

```python
SectionTemplate(
    id="pipes",
    title="Pipe Schedule",
    section_type="pipe_schedule",
)
```

**Requires**: `infrastructure_network`

**Output table columns**:
| ID | Name | Status | Upstream Node | Downstream Node | Length (ft) | Diameter (in) | Material | Slope (ft/ft) |

### inlet_schedule

Detailed inlet schedule.

```python
SectionTemplate(
    id="inlets",
    title="Inlet Schedule",
    section_type="inlet_schedule",
)
```

**Requires**: `infrastructure_network`

**Output table columns**:
| ID | Name | Status | Node | Type | Connected Drainage Areas |

### detention_schedule

Detailed detention facility schedule.

```python
SectionTemplate(
    id="detention",
    title="Detention Schedule",
    section_type="detention_schedule",
)
```

**Requires**: `infrastructure_network`

**Output table columns**:
| ID | Name | Status | Type | Storage Volume (cu ft) | Outlet Structure |

### infrastructure_check_summary

Summary of sizing check results.

```python
SectionTemplate(
    id="checks",
    title="Sizing Check Summary",
    section_type="infrastructure_check_summary",
)
```

**Requires**: `infrastructure_check_results`

**Output table columns**:
| Entity ID | Entity Type | Check Type | Status | Capacity / Provided | Demand / Required | Margin | Warnings |

### infrastructure_warnings

Aggregated warnings from all sizing checks.

```python
SectionTemplate(
    id="warnings",
    title="Infrastructure Warnings",
    section_type="infrastructure_warnings",
)
```

**Requires**: `infrastructure_check_results`

### infrastructure_assumptions

Aggregated assumptions from all sizing checks.

```python
SectionTemplate(
    id="assumptions",
    title="Infrastructure Assumptions",
    section_type="infrastructure_assumptions",
)
```

**Requires**: `infrastructure_check_results`

## Built-in Template

The `infrastructure_summary_report` template provides a complete infrastructure report:

```python
registry = get_default_template_registry()
template = registry.get("infrastructure_summary_report")
```

**Main sections**:
1. Project Information (optional)
2. Infrastructure Summary
3. Infrastructure Schedule
4. Sizing Check Summary
5. Infrastructure Warnings
6. Infrastructure Assumptions
7. References

**Appendices**:
1. Pipe Schedule
2. Inlet Schedule
3. Detention Schedule

## Direct Table Builders

Build tables directly without templates:

```python
from civil_toolbox.reporting import (
    build_infrastructure_summary_table,
    build_pipe_schedule_table,
    build_inlet_schedule_table,
    build_detention_schedule_table,
    build_infrastructure_check_summary_table,
)

# Summary table
summary_table = build_infrastructure_summary_table(network)

# Schedule tables
pipe_table = build_pipe_schedule_table(network)
inlet_table = build_inlet_schedule_table(network)
detention_table = build_detention_schedule_table(network)

# Check summary table
check_table = build_infrastructure_check_summary_table(check_results)
```

## Direct Section Builders

Build sections directly without templates:

```python
from civil_toolbox.reporting import (
    build_infrastructure_summary_section,
    build_infrastructure_schedule_section,
    build_pipe_schedule_section,
    build_inlet_schedule_section,
    build_detention_schedule_section,
    build_infrastructure_check_summary_section,
    build_infrastructure_warnings_section,
    build_infrastructure_assumptions_section,
)

# Each returns a list of ReportSection objects
sections = build_infrastructure_summary_section(network, title="Summary")
```

## Formatting Rules

### Missing Values

Missing optional values render as em-dash (—):

```
| ID  | Name | Material |
|-----|------|----------|
| p1  | P-1  | RCP      |
| p2  | P-2  | —        |
```

### Numeric Precision

- **Flow values**: 1 decimal place (e.g., `15.5 cfs`)
- **Storage volumes**: No decimals with thousands separator (e.g., `50,000 cu ft`)
- **Slope values**: 4 decimal places (e.g., `0.0051`)
- **Percentages**: No decimals (e.g., `+35%`)

### Row Ordering

Tables use deterministic row ordering:
- Sorted by name, then by ID
- Same data always produces same output

### Empty Tables

Empty tables still render headers:

```
| ID | Name | Status |
|----|------|--------|
```

## PDF Export

Infrastructure reports are compatible with PDF export:

```python
from civil_toolbox.reporting import export_report_to_pdf

export_report_to_pdf(report, "infrastructure-report.pdf")
```

## Design Principles

1. **No calculations** — Reporting only formats existing data
2. **Deterministic output** — Same input always produces same output
3. **Template compatible** — Works with existing template system
4. **Render-agnostic** — Works with Markdown and PDF output
5. **Separation of concerns** — Tables, sections, and templates are separate
