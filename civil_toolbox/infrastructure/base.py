"""Base classes for infrastructure elements."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ElementType(str, Enum):
    """Infrastructure element types."""

    PIPE = "pipe"
    INLET = "inlet"
    CULVERT = "culvert"
    CHANNEL = "channel"
    DETENTION = "detention"
    OUTLET = "outlet"
    SWALE = "swale"
    NODE = "node"


@dataclass
class InfrastructureValidationWarning:
    """A validation warning for infrastructure.

    Non-fatal issues that should be reviewed but don't prevent analysis.
    """

    element_id: str
    element_name: str
    warning_code: str
    message: str
    severity: str = "warning"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "element_id": self.element_id,
            "element_name": self.element_name,
            "warning_code": self.warning_code,
            "message": self.message,
            "severity": self.severity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureValidationWarning:
        """Deserialize from dictionary."""
        return cls(
            element_id=data["element_id"],
            element_name=data["element_name"],
            warning_code=data["warning_code"],
            message=data["message"],
            severity=data.get("severity", "warning"),
        )


@dataclass
class InfrastructureCheckResult:
    """Result of infrastructure validation check.

    Contains warnings and errors discovered during validation.
    """

    is_valid: bool
    warnings: list[InfrastructureValidationWarning] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "is_valid": self.is_valid,
            "warnings": [w.to_dict() for w in self.warnings],
            "errors": self.errors,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureCheckResult:
        """Deserialize from dictionary."""
        return cls(
            is_valid=data["is_valid"],
            warnings=[
                InfrastructureValidationWarning.from_dict(w)
                for w in data.get("warnings", [])
            ],
            errors=data.get("errors", []),
        )


@dataclass
class InfrastructureElementBase:
    """Base class for infrastructure elements (plain dataclass, not BaseEntity)."""

    id: str
    name: str
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata.copy(),
        }
