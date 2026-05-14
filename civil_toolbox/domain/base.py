"""Base domain entities for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _generate_id() -> str:
    """Generate a unique entity ID."""
    return str(uuid4())


def _utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class BaseEntity:
    """Base class for all domain entities.

    Provides common fields: id, created_at, updated_at.
    """

    id: str = field(default_factory=_generate_id)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = _utc_now()

    def to_dict(self) -> dict[str, Any]:
        """Serialize entity to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseEntity:
        """Deserialize entity from dictionary."""
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class EngineeringReference:
    """Reference to an authoritative engineering source.

    Used to cite standards, manuals, and publications that support
    calculation methods and assumptions.
    """

    title: str
    source: str
    year: int | None = None
    section: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("EngineeringReference requires a title")
        if not self.source:
            raise ValueError("EngineeringReference requires a source")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "title": self.title,
            "source": self.source,
            "year": self.year,
            "section": self.section,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineeringReference:
        """Deserialize from dictionary."""
        return cls(
            title=data["title"],
            source=data["source"],
            year=data.get("year"),
            section=data.get("section"),
            url=data.get("url"),
        )


@dataclass
class EngineeringAssumption:
    """An explicit assumption made during a calculation.

    Engineering calculations depend on assumptions. Recording them
    supports auditability and review.
    """

    description: str
    category: str | None = None
    reference: EngineeringReference | None = None

    def __post_init__(self) -> None:
        if not self.description:
            raise ValueError("EngineeringAssumption requires a description")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "description": self.description,
            "category": self.category,
            "reference": self.reference.to_dict() if self.reference else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineeringAssumption:
        """Deserialize from dictionary."""
        ref_data = data.get("reference")
        return cls(
            description=data["description"],
            category=data.get("category"),
            reference=EngineeringReference.from_dict(ref_data) if ref_data else None,
        )


@dataclass
class ValidationWarning:
    """A warning generated during input validation or calculation.

    Warnings indicate potential issues that do not prevent calculation
    but may affect reliability or applicability.
    """

    message: str
    field: str | None = None
    severity: str = "warning"

    def __post_init__(self) -> None:
        if not self.message:
            raise ValueError("ValidationWarning requires a message")
        if self.severity not in ("info", "warning", "error"):
            raise ValueError(
                f"ValidationWarning severity must be 'info', 'warning', or 'error', "
                f"got '{self.severity}'"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "message": self.message,
            "field": self.field,
            "severity": self.severity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValidationWarning:
        """Deserialize from dictionary."""
        return cls(
            message=data["message"],
            field=data.get("field"),
            severity=data.get("severity", "warning"),
        )
