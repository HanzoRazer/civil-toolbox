"""Report template models for structured report assembly.

Templates define what sections appear in a report, their order,
and formatting intent. Templates do not perform calculations.

Example:
    >>> from civil_toolbox.reporting.report_templates import (
    ...     ReportTemplate,
    ...     SectionTemplate,
    ... )
    >>> template = ReportTemplate(
    ...     id="my_report",
    ...     name="My Report",
    ...     version="1.0",
    ...     sections=[
    ...         SectionTemplate(
    ...             id="summary",
    ...             title="Project Summary",
    ...             section_type="project_summary",
    ...         ),
    ...     ],
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SUPPORTED_SECTION_TYPES = frozenset({
    "project_summary",
    "scenario_summary",
    "comparison_summary",
    "comparison_table",
    "comparison_totals",
    "storm_sensitivity_table",
    "calculation_summary",
    "calculation_appendix",
    "assumptions",
    "warnings",
    "references",
    "custom_text",
    "heading",
    # Infrastructure section types
    "infrastructure_summary",
    "infrastructure_schedule",
    "pipe_schedule",
    "inlet_schedule",
    "detention_schedule",
    "infrastructure_check_summary",
    "infrastructure_warnings",
    "infrastructure_assumptions",
})

SUPPORTED_FORMATTING_PROFILES = frozenset({
    "standard",
    "compact",
    "review",
    "appendix_heavy",
})


@dataclass
class SectionTemplate:
    """Template for a report section.

    Attributes:
        id: Unique identifier within the template.
        title: Section title/heading.
        section_type: Type of section (determines builder).
        required: Whether section must be included.
        include_when_empty: Include even if data is missing.
        order: Sort order (lower first).
        metadata: Additional configuration.
    """

    id: str
    title: str
    section_type: str
    required: bool = True
    include_when_empty: bool = False
    order: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("SectionTemplate id is required")
        if not self.title:
            raise ValueError("SectionTemplate title is required")
        if not self.section_type:
            raise ValueError("SectionTemplate section_type is required")
        if not isinstance(self.order, int):
            raise ValueError("SectionTemplate order must be an integer")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "section_type": self.section_type,
            "required": self.required,
            "include_when_empty": self.include_when_empty,
            "order": self.order,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SectionTemplate:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            section_type=data["section_type"],
            required=data.get("required", True),
            include_when_empty=data.get("include_when_empty", False),
            order=data.get("order", 0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ReportTemplate:
    """Template for assembling a report.

    Attributes:
        id: Unique template identifier.
        name: Human-readable template name.
        version: Template version string.
        description: Optional description.
        sections: Main report sections.
        appendices: Appendix sections (appear after main).
        formatting_profile: Profile for rendering hints.
        metadata: Additional configuration.
    """

    id: str
    name: str
    version: str
    description: str | None = None
    sections: list[SectionTemplate] = field(default_factory=list)
    appendices: list[SectionTemplate] = field(default_factory=list)
    formatting_profile: str = "standard"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ReportTemplate id is required")
        if not self.name:
            raise ValueError("ReportTemplate name is required")
        if not self.version:
            raise ValueError("ReportTemplate version is required")
        if not self.sections and not self.appendices:
            raise ValueError(
                "ReportTemplate must have at least one section or appendix"
            )
        if self.formatting_profile not in SUPPORTED_FORMATTING_PROFILES:
            raise ValueError(
                f"Unsupported formatting profile: {self.formatting_profile}. "
                f"Supported: {sorted(SUPPORTED_FORMATTING_PROFILES)}"
            )

        all_ids = [s.id for s in self.sections] + [a.id for a in self.appendices]
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("Section IDs must be unique within a template")

    def get_ordered_sections(self) -> list[SectionTemplate]:
        """Get sections sorted by order then id."""
        return sorted(self.sections, key=lambda s: (s.order, s.id))

    def get_ordered_appendices(self) -> list[SectionTemplate]:
        """Get appendices sorted by order then id."""
        return sorted(self.appendices, key=lambda s: (s.order, s.id))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "sections": [s.to_dict() for s in self.sections],
            "appendices": [a.to_dict() for a in self.appendices],
            "formatting_profile": self.formatting_profile,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportTemplate:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description"),
            sections=[
                SectionTemplate.from_dict(s) for s in data.get("sections", [])
            ],
            appendices=[
                SectionTemplate.from_dict(a) for a in data.get("appendices", [])
            ],
            formatting_profile=data.get("formatting_profile", "standard"),
            metadata=data.get("metadata", {}),
        )
