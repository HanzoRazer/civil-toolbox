"""Validation utilities for report templates.

Validates template structure and checks whether a template can be
built with a given context.

Example:
    >>> from civil_toolbox.reporting.template_validation import (
    ...     validate_template,
    ...     validate_template_context,
    ... )
    >>> validate_template(template)  # raises on invalid
    >>> warnings = validate_template_context(template, context)
"""

from __future__ import annotations

from civil_toolbox.reporting.report_templates import (
    ReportTemplate,
    SectionTemplate,
    SUPPORTED_SECTION_TYPES,
)
from civil_toolbox.reporting.template_context import ReportTemplateContext


SECTION_REQUIREMENTS: dict[str, str] = {
    "project_summary": "project",
    "scenario_summary": "scenario",
    "comparison_summary": "comparison",
    "comparison_table": "comparison",
    "comparison_totals": "comparison",
    "storm_sensitivity_table": "storm_sensitivity",
    "calculation_summary": "scenario",
    "calculation_appendix": "scenario",
    # Infrastructure requirements
    "infrastructure_summary": "infrastructure_network",
    "infrastructure_schedule": "infrastructure_network",
    "pipe_schedule": "infrastructure_network",
    "inlet_schedule": "infrastructure_network",
    "detention_schedule": "infrastructure_network",
    "infrastructure_check_summary": "infrastructure_check_results",
    "infrastructure_warnings": "infrastructure_check_results",
    "infrastructure_assumptions": "infrastructure_check_results",
}


class TemplateValidationError(ValueError):
    """Raised when template validation fails."""

    def __init__(self, message: str, section_id: str | None = None):
        self.section_id = section_id
        super().__init__(message)


class ContextValidationError(ValueError):
    """Raised when context validation fails for a required section."""

    def __init__(self, message: str, section_id: str, requirement: str):
        self.section_id = section_id
        self.requirement = requirement
        super().__init__(message)


def validate_section_template(section: SectionTemplate) -> None:
    """Validate a section template.

    Args:
        section: The section template to validate.

    Raises:
        TemplateValidationError: If section is invalid.
    """
    if not section.id:
        raise TemplateValidationError("Section ID is required")
    if not section.title:
        raise TemplateValidationError(
            f"Section title is required",
            section_id=section.id,
        )
    if not section.section_type:
        raise TemplateValidationError(
            f"Section type is required",
            section_id=section.id,
        )
    if section.section_type not in SUPPORTED_SECTION_TYPES:
        raise TemplateValidationError(
            f"Unknown section type: {section.section_type}. "
            f"Supported: {sorted(SUPPORTED_SECTION_TYPES)}",
            section_id=section.id,
        )


def validate_template(template: ReportTemplate) -> None:
    """Validate a report template.

    Args:
        template: The template to validate.

    Raises:
        TemplateValidationError: If template is invalid.
    """
    if not template.id:
        raise TemplateValidationError("Template ID is required")
    if not template.name:
        raise TemplateValidationError("Template name is required")
    if not template.version:
        raise TemplateValidationError("Template version is required")
    if not template.sections and not template.appendices:
        raise TemplateValidationError(
            "Template must have at least one section or appendix"
        )

    all_ids = set()
    for section in template.sections:
        validate_section_template(section)
        if section.id in all_ids:
            raise TemplateValidationError(
                f"Duplicate section ID: {section.id}",
                section_id=section.id,
            )
        all_ids.add(section.id)

    for appendix in template.appendices:
        validate_section_template(appendix)
        if appendix.id in all_ids:
            raise TemplateValidationError(
                f"Duplicate section ID: {appendix.id}",
                section_id=appendix.id,
            )
        all_ids.add(appendix.id)


def validate_template_context(
    template: ReportTemplate,
    context: ReportTemplateContext,
) -> list[str]:
    """Validate that a template can be built with the given context.

    Args:
        template: The template to build.
        context: The context providing data.

    Returns:
        List of warning messages for optional missing data.

    Raises:
        ContextValidationError: If required section data is missing.
    """
    warnings = []

    all_sections = template.sections + template.appendices

    for section in all_sections:
        requirement = SECTION_REQUIREMENTS.get(section.section_type)

        if requirement is None:
            if section.section_type == "custom_text":
                custom_text = context.get_custom_section(section.id)
                if custom_text is None and not section.include_when_empty:
                    if section.required:
                        raise ContextValidationError(
                            f"Required custom section '{section.id}' has no content",
                            section_id=section.id,
                            requirement="custom_section",
                        )
                    else:
                        warnings.append(
                            f"Optional section '{section.id}' has no custom content"
                        )
            continue

        has_data = False
        if requirement == "project":
            has_data = context.has_project()
        elif requirement == "scenario":
            has_data = context.has_scenario()
        elif requirement == "comparison":
            has_data = context.has_comparison()
        elif requirement == "storm_sensitivity":
            has_data = context.has_storm_sensitivity()
        elif requirement == "infrastructure_network":
            has_data = context.has_infrastructure_network()
        elif requirement == "infrastructure_check_results":
            has_data = context.has_infrastructure_check_results()

        if not has_data:
            if section.required:
                raise ContextValidationError(
                    f"Required section '{section.id}' needs {requirement} data",
                    section_id=section.id,
                    requirement=requirement,
                )
            else:
                warnings.append(
                    f"Optional section '{section.id}' missing {requirement} data"
                )

    return warnings


def can_build_section(
    section: SectionTemplate,
    context: ReportTemplateContext,
) -> bool:
    """Check if a section can be built with the given context.

    Args:
        section: The section template.
        context: The context providing data.

    Returns:
        True if section can be built.
    """
    requirement = SECTION_REQUIREMENTS.get(section.section_type)

    if requirement is None:
        if section.section_type == "custom_text":
            custom_text = context.get_custom_section(section.id)
            return custom_text is not None or section.include_when_empty
        return True

    if requirement == "project":
        return context.has_project()
    elif requirement == "scenario":
        return context.has_scenario()
    elif requirement == "comparison":
        return context.has_comparison()
    elif requirement == "storm_sensitivity":
        return context.has_storm_sensitivity()
    elif requirement == "infrastructure_network":
        return context.has_infrastructure_network()
    elif requirement == "infrastructure_check_results":
        return context.has_infrastructure_check_results()

    return True
