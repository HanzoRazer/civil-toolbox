# Report Templates

Reusable templates for consistent engineering report generation.

## Overview

Report templates define the structure, section ordering, and formatting intent for engineering reports. Templates assemble reports from domain objects without performing calculations.

The template system provides:

- Standardized report structures
- Configurable sections and appendices
- Built-in templates for common report types
- Custom template creation
- Template serialization for sharing

## Architecture

```text
Project / Scenario / Comparison Data
        ↓
Report Template
        ↓
Template Builder
        ↓
Structured Report
        ↓
Markdown Renderer
        ↓
PDF Export
```

## Quick Start

### Using Built-in Templates

```python
from civil_toolbox.reporting import (
    build_report_from_template,
    get_default_template_registry,
    ReportTemplateContext,
    render_full_report_markdown,
)

# Get the built-in registry
registry = get_default_template_registry()

# Choose a template
template = registry.get("project_summary")

# Create context with your data
context = ReportTemplateContext(
    project=my_project,
    scenario=my_scenario,
)

# Build the report
report = build_report_from_template(template, context)

# Render to Markdown
markdown = render_full_report_markdown(report)
```

### PDF Export

```python
from civil_toolbox.reporting import export_report_to_pdf

export_report_to_pdf(report, "report.pdf")
```

## Template Model

### ReportTemplate

```python
from civil_toolbox.reporting import ReportTemplate, SectionTemplate

template = ReportTemplate(
    id="my_template",
    name="My Report Template",
    version="1.0",
    description="Custom report for drainage analysis",
    sections=[
        SectionTemplate(
            id="project_info",
            title="Project Information",
            section_type="project_summary",
        ),
        SectionTemplate(
            id="calculations",
            title="Calculations",
            section_type="calculation_summary",
        ),
    ],
    appendices=[
        SectionTemplate(
            id="calc_details",
            title="Calculation Details",
            section_type="calculation_appendix",
        ),
    ],
    formatting_profile="standard",
)
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | Yes | Unique template identifier |
| `name` | str | Yes | Human-readable name |
| `version` | str | Yes | Template version |
| `description` | str | No | Template description |
| `sections` | list | No* | Main report sections |
| `appendices` | list | No* | Appendix sections |
| `formatting_profile` | str | No | Rendering hint (default: "standard") |
| `metadata` | dict | No | Additional configuration |

*At least one section or appendix is required.

## Section Templates

### SectionTemplate

```python
SectionTemplate(
    id="unique_id",
    title="Section Title",
    section_type="project_summary",
    required=True,
    include_when_empty=False,
    order=10,
    metadata={},
)
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str | Required | Unique identifier within template |
| `title` | str | Required | Section heading |
| `section_type` | str | Required | Type determining builder |
| `required` | bool | True | Fail if data missing |
| `include_when_empty` | bool | False | Include even without data |
| `order` | int | 0 | Sort order (lower first) |
| `metadata` | dict | {} | Additional configuration |

### Section Types

| Type | Data Required | Description |
|------|---------------|-------------|
| `project_summary` | project | Project metadata table |
| `scenario_summary` | scenario | Scenario overview |
| `comparison_summary` | comparison | Comparison overview |
| `comparison_table` | comparison | Entity delta table |
| `comparison_totals` | comparison | Scenario-level totals |
| `calculation_summary` | scenario | Calculation count summary |
| `calculation_appendix` | scenario | Detailed calculations |
| `assumptions` | - | Aggregated assumptions |
| `warnings` | - | Aggregated warnings |
| `references` | - | Aggregated references |
| `custom_text` | custom_sections | User-provided text |
| `heading` | - | Simple heading |
| `infrastructure_summary` | infrastructure_network | Element counts by type |
| `infrastructure_schedule` | infrastructure_network | Combined pipe/inlet/detention tables |
| `pipe_schedule` | infrastructure_network | Pipe schedule table |
| `inlet_schedule` | infrastructure_network | Inlet schedule table |
| `detention_schedule` | infrastructure_network | Detention schedule table |
| `infrastructure_check_summary` | infrastructure_check_results | Sizing check results |
| `infrastructure_warnings` | infrastructure_check_results | Sizing check warnings |
| `infrastructure_assumptions` | infrastructure_check_results | Sizing check assumptions |

## Built-In Templates

### project_summary

Standard project summary with optional scenario overview.

```python
registry = get_default_template_registry()
template = registry.get("project_summary")
```

Sections:
- Project Information
- Scenario Overview (optional)
- Assumptions (optional)
- Warnings (optional)
- References (optional)

### scenario_comparison

Compare two scenarios with totals and entity deltas.

```python
template = registry.get("scenario_comparison")
```

Sections:
- Project Information (optional)
- Comparison Overview
- Scenario Totals (optional)
- Entity Comparison
- Warnings (optional)
- References (optional)

### drainage_calculation_appendix

Detailed calculation appendix for drainage analysis.

```python
template = registry.get("drainage_calculation_appendix")
```

Sections:
- Calculation Summary
- Calculations
- Assumptions (optional)
- Warnings (optional)
- References (optional)

### combined_drainage_report

Comprehensive report with sections and appendices.

```python
template = registry.get("combined_drainage_report")
```

Sections:
- Project Information (optional)
- Scenario Overview (optional)
- Comparison Overview (optional)
- Scenario Totals (optional)
- Entity Comparison (optional)
- Calculation Summary (optional)

Appendices:
- Calculation Details (optional)
- Assumptions (optional)
- Warnings (optional)
- References (optional)

### infrastructure_summary_report

Infrastructure report with network summary and sizing checks.

```python
template = registry.get("infrastructure_summary_report")
```

Sections:
- Project Information (optional)
- Infrastructure Summary
- Infrastructure Schedule (optional)
- Sizing Check Summary (optional)
- Infrastructure Warnings (optional)
- Infrastructure Assumptions (optional)
- References (optional)

Appendices:
- Pipe Schedule (optional)
- Inlet Schedule (optional)
- Detention Schedule (optional)

## Template Context

### ReportTemplateContext

Pass data to template builders without global state.

```python
from civil_toolbox.reporting import ReportTemplateContext

context = ReportTemplateContext(
    project=my_project,
    scenario=my_scenario,
    comparison=my_comparison,
    infrastructure_network=my_network,
    infrastructure_check_results=my_check_results,
    metadata={
        "author": "Jane Engineer",
        "organization": "Engineering Corp",
    },
    custom_sections={
        "intro": "This report summarizes the drainage analysis.",
    },
    assumptions=["Steady state conditions"],
    warnings=["Area exceeds typical limit"],
    references=[
        {"title": "TR-55", "source": "NRCS", "year": "1986"},
    ],
)
```

### Helper Methods

```python
context.has_project()  # True if project is set
context.has_scenario()  # True if scenario is set
context.has_comparison()  # True if comparison is set
context.has_infrastructure_network()  # True if infrastructure_network is set
context.has_infrastructure_check_results()  # True if results list is non-empty
context.get_custom_section("intro")  # Get custom text by ID
context.get_all_assumptions()  # Aggregated assumptions
context.get_all_warnings()  # Aggregated warnings
context.get_all_references()  # Aggregated references
```

## Building Reports

### Basic Usage

```python
from civil_toolbox.reporting import (
    build_report_from_template,
    ReportTemplateContext,
)

report = build_report_from_template(template, context)
```

### Section Ordering

Sections are processed in order: sorted by `order`, then by `id`.

```python
SectionTemplate(id="a", order=10, ...)  # First
SectionTemplate(id="b", order=10, ...)  # Second (same order, sorted by id)
SectionTemplate(id="c", order=20, ...)  # Third
```

### Optional Sections

When `required=False`, sections are skipped if data is missing:

```python
SectionTemplate(
    id="scenario_info",
    section_type="scenario_summary",
    required=False,  # Skip if no scenario
)
```

### Custom Text Sections

Use `custom_text` type with matching context:

```python
template = ReportTemplate(
    id="custom",
    name="Custom Report",
    version="1.0",
    sections=[
        SectionTemplate(
            id="introduction",
            title="Introduction",
            section_type="custom_text",
        ),
    ],
)

context = ReportTemplateContext(
    custom_sections={
        "introduction": "This report presents the drainage analysis...",
    },
)
```

## Formatting Profiles

Templates include a formatting profile hint:

| Profile | Description |
|---------|-------------|
| `standard` | Default formatting |
| `compact` | Reduced spacing |
| `review` | Review-oriented layout |
| `appendix_heavy` | Emphasizes appendix sections |

Currently profiles are metadata only; renderers may ignore them.

## Serialization

Templates serialize to dictionaries for storage:

```python
# Serialize
data = template.to_dict()

# Deserialize
restored = ReportTemplate.from_dict(data)
```

Example serialized template:

```json
{
  "id": "my_template",
  "name": "My Report",
  "version": "1.0",
  "description": "Custom template",
  "sections": [
    {
      "id": "section1",
      "title": "Section 1",
      "section_type": "project_summary",
      "required": true,
      "include_when_empty": false,
      "order": 0,
      "metadata": {}
    }
  ],
  "appendices": [],
  "formatting_profile": "standard",
  "metadata": {}
}
```

## Template Registry

### Using the Registry

```python
from civil_toolbox.reporting import ReportTemplateRegistry

registry = ReportTemplateRegistry()

# Register a template
registry.register(my_template)

# Get a template
template = registry.get("my_template")

# Check existence
if registry.has_template("my_template"):
    ...

# List all templates
for template in registry.list_templates():
    print(template.name)

# Overwrite existing
registry.register(updated_template, overwrite=True)
```

### Default Registry

```python
from civil_toolbox.reporting import get_default_template_registry

# Fresh registry with built-in templates
registry = get_default_template_registry()
```

## Validation

### Template Validation

```python
from civil_toolbox.reporting import validate_template, TemplateValidationError

try:
    validate_template(template)
except TemplateValidationError as e:
    print(f"Invalid template: {e}")
```

### Context Validation

```python
from civil_toolbox.reporting import (
    validate_template_context,
    ContextValidationError,
)

try:
    warnings = validate_template_context(template, context)
    for warning in warnings:
        print(f"Warning: {warning}")
except ContextValidationError as e:
    print(f"Cannot build: {e}")
```

## Limitations

- Templates do not run calculations
- Templates do not mutate domain objects
- Formatting profiles are metadata only (renderers may ignore)
- No plugin system for custom section types
- No cloud storage or versioning

## Future Work

- Jurisdiction-specific templates
- Custom section type registration
- Template inheritance
- Cover page configuration
- Table of contents generation
- Profile-aware rendering
