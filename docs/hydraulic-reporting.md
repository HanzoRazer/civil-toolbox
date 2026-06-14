# Hydraulic Reporting

Integrates the hydraulic grade line (HGL) foundation into the reporting system so
`HydraulicProfileResult` objects can appear in Markdown/PDF reports, templates,
and appendices.

This is an **integration** layer — it does **not** run HGL calculations. It only
formats existing `HydraulicProfileResult` data.

## Overview

```text
HydraulicProfileResult → HGL report sections → Markdown / PDF reports
```

Given a computed `HydraulicProfileResult`, the reporting layer can render:

- a profile summary,
- a reach-by-reach results table,
- warnings, assumptions, and references.

## HGL Profile Reports

Build a report from the built-in template:

```python
from civil_toolbox.reporting.builtins import get_builtin_templates
from civil_toolbox.reporting.template_builders import build_report_from_template
from civil_toolbox.reporting.template_context import ReportTemplateContext
from civil_toolbox.reporting.markdown import render_report_markdown

template = next(t for t in get_builtin_templates() if t.id == "hydraulic_profile_report")
context = ReportTemplateContext(hydraulic_profile=profile)
report = build_report_from_template(template, context)
markdown = render_report_markdown(report)
```

The built-in `hydraulic_profile_report` template puts the **summary** and
**reach table** in the body and the **warnings / assumptions / references** in
appendices (each rendered once — no duplication).

## Reach Tables

`build_hgl_reach_table(profile)` produces one row per reach:

```text
Reach ID | Pipe ID | Design Flow (cfs) | Velocity (fps) | Velocity Head (ft) |
Friction Loss (ft) | Downstream HGL (ft) | Upstream HGL (ft) | Upstream EGL (ft) |
Surcharge Status | Freeboard to Rim (ft)
```

## Surcharge and Freeboard Reporting

Surcharge status and freeboard are reported for the **upstream end** of each
reach (the controlling end as the profile is computed downstream → upstream).
Surcharge statuses are preserved exactly from the hydraulics foundation:

```text
free_surface
pressurized
surcharged_above_crown
surcharged_above_rim
unknown
```

## Warnings

The warnings table aggregates both **profile-level** and **reach-level**
warnings. Reach-level warnings with no `entity_id` fall back to the reach ID, so
no warning is orphaned.

## Assumptions

Assumptions are deduplicated deterministically (sorted) before rendering.

## References

HGL `references` are plain strings (`list[str]`) on the result. They render
directly in the dedicated HGL references section, deduplicated preserving
first-seen order — they are **not** forced through the generic dict-based
reference machinery.

## Report Template Sections

New section types (all require `hydraulic_profile` in the context):

| Section type | Renders |
|--------------|---------|
| `hgl_profile_summary` | Profile summary table |
| `hgl_reach_table` | Reach-by-reach table |
| `hgl_warnings` | Warning table (profile + reach) |
| `hgl_assumptions` | Deduplicated assumptions list |
| `hgl_references` | References (string list) |

Required sections with no `hydraulic_profile` raise `ContextValidationError`;
optional ones warn and are skipped.

## Markdown and PDF Output

Markdown is the deterministic source of truth. PDF export goes through the same
`Report` object via WeasyPrint (`export_report_to_pdf`), which is an optional
dependency (`pip install "civil-toolbox[pdf]"`).

## Limitations

- No HGL calculations are performed here (integration only).
- No profile plotting / GIS visualization.
- No SWMM / HEC-RAS export.
- Single-profile context is wired into builders; the multi-profile
  (`hydraulic_profiles`) field is reserved for future use.

## Future Work

- Multi-profile reports (iterate `hydraulic_profiles`).
- Profile figures / plots.
- A `CalculationResult` adapter so HGL results gain uniform audit coverage.
