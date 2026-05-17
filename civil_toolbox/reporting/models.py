"""Data models for the reporting engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ReportType(Enum):
    """Types of reports that can be generated."""

    PROJECT_SUMMARY = "project_summary"
    SCENARIO_COMPARISON = "scenario_comparison"
    CALCULATION_APPENDIX = "calculation_appendix"


class SectionType(Enum):
    """Types of report sections."""

    TITLE = "title"
    METADATA = "metadata"
    SUMMARY = "summary"
    TABLE = "table"
    TEXT = "text"
    LIST = "list"
    HEADING = "heading"
    CALCULATION = "calculation"
    ASSUMPTIONS = "assumptions"
    WARNINGS = "warnings"
    REFERENCES = "references"
    FIGURE_PLACEHOLDER = "figure_placeholder"


def _utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class ReportMetadata:
    """Metadata for a generated report.

    Attributes:
        title: Report title.
        report_type: Type of report.
        generated_at: Generation timestamp.
        generator_version: Version of the reporting engine.
        project_name: Name of the source project.
        project_id: ID of the source project.
        scenario_names: Names of scenarios included.
        author: Optional author name.
        organization: Optional organization name.
    """

    title: str
    report_type: ReportType
    generated_at: datetime = field(default_factory=_utc_now)
    generator_version: str = "1.0.0"
    project_name: str | None = None
    project_id: str | None = None
    scenario_names: list[str] = field(default_factory=list)
    author: str | None = None
    organization: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "title": self.title,
            "report_type": self.report_type.value,
            "generated_at": self.generated_at.isoformat(),
            "generator_version": self.generator_version,
            "project_name": self.project_name,
            "project_id": self.project_id,
            "scenario_names": self.scenario_names,
            "author": self.author,
            "organization": self.organization,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportMetadata:
        """Deserialize from dictionary."""
        return cls(
            title=data["title"],
            report_type=ReportType(data["report_type"]),
            generated_at=datetime.fromisoformat(data["generated_at"]),
            generator_version=data.get("generator_version", "1.0.0"),
            project_name=data.get("project_name"),
            project_id=data.get("project_id"),
            scenario_names=data.get("scenario_names", []),
            author=data.get("author"),
            organization=data.get("organization"),
        )


@dataclass
class ReportTable:
    """A table within a report.

    Attributes:
        title: Optional table title/caption.
        headers: Column headers.
        rows: Table data rows.
        alignments: Column alignments ('left', 'center', 'right').
        footer: Optional footer text.
    """

    headers: list[str]
    rows: list[list[str]]
    title: str | None = None
    alignments: list[str] | None = None
    footer: str | None = None

    def __post_init__(self) -> None:
        if self.alignments is None:
            self.alignments = ["left"] * len(self.headers)
        if len(self.alignments) != len(self.headers):
            raise ValueError(
                f"Alignments count ({len(self.alignments)}) must match "
                f"headers count ({len(self.headers)})"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "title": self.title,
            "headers": self.headers,
            "rows": self.rows,
            "alignments": self.alignments,
            "footer": self.footer,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportTable:
        """Deserialize from dictionary."""
        return cls(
            title=data.get("title"),
            headers=data["headers"],
            rows=data["rows"],
            alignments=data.get("alignments"),
            footer=data.get("footer"),
        )


@dataclass
class ReportFigurePlaceholder:
    """A placeholder for a figure in a report.

    Figures are not rendered by the reporting engine.
    This placeholder marks where a figure should appear.

    Attributes:
        figure_id: Unique identifier for the figure.
        caption: Figure caption.
        description: Description of what the figure should show.
        suggested_filename: Suggested filename for the figure.
    """

    figure_id: str
    caption: str
    description: str | None = None
    suggested_filename: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "figure_id": self.figure_id,
            "caption": self.caption,
            "description": self.description,
            "suggested_filename": self.suggested_filename,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportFigurePlaceholder:
        """Deserialize from dictionary."""
        return cls(
            figure_id=data["figure_id"],
            caption=data["caption"],
            description=data.get("description"),
            suggested_filename=data.get("suggested_filename"),
        )


@dataclass
class ReportSection:
    """A section within a report.

    Sections contain content and can be nested.

    Attributes:
        section_type: Type of section.
        title: Section title (for headings).
        level: Heading level (1-6).
        content: Text content.
        items: List items (for list sections).
        table: Table content (for table sections).
        figure: Figure placeholder (for figure sections).
        subsections: Nested sections.
        metadata: Additional metadata.
    """

    section_type: SectionType
    title: str | None = None
    level: int = 2
    content: str | None = None
    items: list[str] | None = None
    table: ReportTable | None = None
    figure: ReportFigurePlaceholder | None = None
    subsections: list[ReportSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "section_type": self.section_type.value,
            "title": self.title,
            "level": self.level,
            "content": self.content,
            "items": self.items,
            "table": self.table.to_dict() if self.table else None,
            "figure": self.figure.to_dict() if self.figure else None,
            "subsections": [s.to_dict() for s in self.subsections],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportSection:
        """Deserialize from dictionary."""
        table_data = data.get("table")
        figure_data = data.get("figure")
        return cls(
            section_type=SectionType(data["section_type"]),
            title=data.get("title"),
            level=data.get("level", 2),
            content=data.get("content"),
            items=data.get("items"),
            table=ReportTable.from_dict(table_data) if table_data else None,
            figure=(
                ReportFigurePlaceholder.from_dict(figure_data)
                if figure_data
                else None
            ),
            subsections=[
                ReportSection.from_dict(s) for s in data.get("subsections", [])
            ],
            metadata=data.get("metadata", {}),
        )


@dataclass
class Report:
    """A complete report.

    Reports contain metadata and an ordered list of sections.
    Reports do not contain rendered output — they are data structures
    that can be rendered to various formats.

    Attributes:
        metadata: Report metadata.
        sections: Ordered list of report sections.
    """

    metadata: ReportMetadata
    sections: list[ReportSection] = field(default_factory=list)

    def add_section(self, section: ReportSection) -> None:
        """Add a section to the report."""
        self.sections.append(section)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "sections": [s.to_dict() for s in self.sections],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Report:
        """Deserialize from dictionary."""
        return cls(
            metadata=ReportMetadata.from_dict(data["metadata"]),
            sections=[
                ReportSection.from_dict(s) for s in data.get("sections", [])
            ],
        )
