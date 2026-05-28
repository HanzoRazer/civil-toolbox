"""Built-in report templates.

Provides standard templates for common report types:
- project_summary
- scenario_comparison
- drainage_calculation_appendix
- combined_drainage_report

Example:
    >>> from civil_toolbox.reporting.builtins import (
    ...     get_builtin_templates,
    ...     get_default_template_registry,
    ... )
    >>> templates = get_builtin_templates()
    >>> registry = get_default_template_registry()
"""

from __future__ import annotations

from civil_toolbox.reporting.report_templates import (
    ReportTemplate,
    SectionTemplate,
)
from civil_toolbox.reporting.template_registry import ReportTemplateRegistry


def _create_project_summary_template() -> ReportTemplate:
    """Create the project summary template."""
    return ReportTemplate(
        id="project_summary",
        name="Project Summary Report",
        version="1.0",
        description="Summary report for a project with scenario overview.",
        sections=[
            SectionTemplate(
                id="project_info",
                title="Project Information",
                section_type="project_summary",
                order=10,
            ),
            SectionTemplate(
                id="scenario_overview",
                title="Scenario Overview",
                section_type="scenario_summary",
                required=False,
                order=20,
            ),
            SectionTemplate(
                id="assumptions",
                title="Assumptions",
                section_type="assumptions",
                required=False,
                order=30,
            ),
            SectionTemplate(
                id="warnings",
                title="Warnings",
                section_type="warnings",
                required=False,
                order=40,
            ),
            SectionTemplate(
                id="references",
                title="References",
                section_type="references",
                required=False,
                order=50,
            ),
        ],
        formatting_profile="standard",
    )


def _create_scenario_comparison_template() -> ReportTemplate:
    """Create the scenario comparison template."""
    return ReportTemplate(
        id="scenario_comparison",
        name="Scenario Comparison Report",
        version="1.0",
        description="Compare two scenarios with totals and entity-level deltas.",
        sections=[
            SectionTemplate(
                id="project_info",
                title="Project Information",
                section_type="project_summary",
                required=False,
                order=10,
            ),
            SectionTemplate(
                id="comparison_overview",
                title="Comparison Overview",
                section_type="comparison_summary",
                order=20,
            ),
            SectionTemplate(
                id="scenario_totals",
                title="Scenario Totals",
                section_type="comparison_totals",
                required=False,
                order=30,
            ),
            SectionTemplate(
                id="entity_comparison",
                title="Entity Comparison",
                section_type="comparison_table",
                order=40,
            ),
            SectionTemplate(
                id="warnings",
                title="Warnings",
                section_type="warnings",
                required=False,
                order=50,
            ),
            SectionTemplate(
                id="references",
                title="References",
                section_type="references",
                required=False,
                order=60,
            ),
        ],
        formatting_profile="standard",
    )


def _create_drainage_calculation_appendix_template() -> ReportTemplate:
    """Create the drainage calculation appendix template."""
    return ReportTemplate(
        id="drainage_calculation_appendix",
        name="Drainage Calculation Appendix",
        version="1.0",
        description="Detailed calculation appendix for drainage analysis.",
        sections=[
            SectionTemplate(
                id="calc_summary",
                title="Calculation Summary",
                section_type="calculation_summary",
                order=10,
            ),
            SectionTemplate(
                id="calculations",
                title="Calculations",
                section_type="calculation_appendix",
                order=20,
            ),
            SectionTemplate(
                id="assumptions",
                title="Assumptions",
                section_type="assumptions",
                required=False,
                order=30,
            ),
            SectionTemplate(
                id="warnings",
                title="Warnings",
                section_type="warnings",
                required=False,
                order=40,
            ),
            SectionTemplate(
                id="references",
                title="References",
                section_type="references",
                required=False,
                order=50,
            ),
        ],
        formatting_profile="appendix_heavy",
    )


def _create_combined_drainage_report_template() -> ReportTemplate:
    """Create the combined drainage report template."""
    return ReportTemplate(
        id="combined_drainage_report",
        name="Combined Drainage Report",
        version="1.0",
        description=(
            "Comprehensive drainage report with project summary, "
            "scenario comparison, and calculation appendix."
        ),
        sections=[
            SectionTemplate(
                id="project_info",
                title="Project Information",
                section_type="project_summary",
                required=False,
                order=10,
            ),
            SectionTemplate(
                id="scenario_overview",
                title="Scenario Overview",
                section_type="scenario_summary",
                required=False,
                order=20,
            ),
            SectionTemplate(
                id="comparison_overview",
                title="Comparison Overview",
                section_type="comparison_summary",
                required=False,
                order=30,
            ),
            SectionTemplate(
                id="scenario_totals",
                title="Scenario Totals",
                section_type="comparison_totals",
                required=False,
                order=40,
            ),
            SectionTemplate(
                id="entity_comparison",
                title="Entity Comparison",
                section_type="comparison_table",
                required=False,
                order=50,
            ),
            SectionTemplate(
                id="calc_summary",
                title="Calculation Summary",
                section_type="calculation_summary",
                required=False,
                order=60,
            ),
        ],
        appendices=[
            SectionTemplate(
                id="calculations",
                title="Calculation Details",
                section_type="calculation_appendix",
                required=False,
                order=10,
            ),
            SectionTemplate(
                id="assumptions",
                title="Assumptions",
                section_type="assumptions",
                required=False,
                order=20,
            ),
            SectionTemplate(
                id="warnings",
                title="Warnings",
                section_type="warnings",
                required=False,
                order=30,
            ),
            SectionTemplate(
                id="references",
                title="References",
                section_type="references",
                required=False,
                order=40,
            ),
        ],
        formatting_profile="standard",
    )


def _create_infrastructure_summary_report_template() -> ReportTemplate:
    """Create the infrastructure summary report template."""
    return ReportTemplate(
        id="infrastructure_summary_report",
        name="Infrastructure Summary Report",
        version="1.0",
        description=(
            "Comprehensive infrastructure report with network summary, "
            "sizing checks, and element schedules."
        ),
        sections=[
            SectionTemplate(
                id="project_info",
                title="Project Information",
                section_type="project_summary",
                required=False,
                order=10,
            ),
            SectionTemplate(
                id="infrastructure_summary",
                title="Infrastructure Summary",
                section_type="infrastructure_summary",
                order=20,
            ),
            SectionTemplate(
                id="infrastructure_schedule",
                title="Infrastructure Schedule",
                section_type="infrastructure_schedule",
                required=False,
                order=30,
            ),
            SectionTemplate(
                id="infrastructure_check_summary",
                title="Sizing Check Summary",
                section_type="infrastructure_check_summary",
                required=False,
                order=40,
            ),
            SectionTemplate(
                id="infrastructure_warnings",
                title="Infrastructure Warnings",
                section_type="infrastructure_warnings",
                required=False,
                order=50,
            ),
            SectionTemplate(
                id="infrastructure_assumptions",
                title="Infrastructure Assumptions",
                section_type="infrastructure_assumptions",
                required=False,
                order=60,
            ),
            SectionTemplate(
                id="references",
                title="References",
                section_type="references",
                required=False,
                order=70,
            ),
        ],
        appendices=[
            SectionTemplate(
                id="pipe_schedule",
                title="Pipe Schedule",
                section_type="pipe_schedule",
                required=False,
                order=10,
            ),
            SectionTemplate(
                id="inlet_schedule",
                title="Inlet Schedule",
                section_type="inlet_schedule",
                required=False,
                order=20,
            ),
            SectionTemplate(
                id="detention_schedule",
                title="Detention Schedule",
                section_type="detention_schedule",
                required=False,
                order=30,
            ),
        ],
        formatting_profile="standard",
    )


def get_builtin_templates() -> list[ReportTemplate]:
    """Get all built-in report templates.

    Returns:
        List of built-in templates.
    """
    return [
        _create_project_summary_template(),
        _create_scenario_comparison_template(),
        _create_drainage_calculation_appendix_template(),
        _create_combined_drainage_report_template(),
        _create_infrastructure_summary_report_template(),
    ]


def get_default_template_registry() -> ReportTemplateRegistry:
    """Get a registry pre-populated with built-in templates.

    Returns a fresh registry each time to avoid global mutable state.

    Returns:
        Registry containing all built-in templates.
    """
    registry = ReportTemplateRegistry()
    for template in get_builtin_templates():
        registry.register(template)
    return registry
