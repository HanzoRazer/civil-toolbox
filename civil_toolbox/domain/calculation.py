"""Calculation result domain entity for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from civil_toolbox.domain.base import (
    BaseEntity,
    EngineeringAssumption,
    EngineeringReference,
    ValidationWarning,
)


@dataclass
class CalculationResult(BaseEntity):
    """An auditable calculation result.

    Records the method, inputs, outputs, units, assumptions, and
    references for a single calculation. Supports engineering
    traceability and review.
    """

    method: str = ""
    scenario_id: str | None = None
    entity_id: str | None = None
    entity_type: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    assumptions: list[EngineeringAssumption] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)
    references: list[EngineeringReference] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.method:
            raise ValueError("CalculationResult requires a method name")

    def add_assumption(self, assumption: EngineeringAssumption) -> None:
        """Add an assumption to the result."""
        if not isinstance(assumption, EngineeringAssumption):
            raise TypeError("Expected an EngineeringAssumption instance")
        self.assumptions.append(assumption)

    def add_warning(self, warning: ValidationWarning) -> None:
        """Add a warning to the result."""
        if not isinstance(warning, ValidationWarning):
            raise TypeError("Expected a ValidationWarning instance")
        self.warnings.append(warning)

    def add_reference(self, reference: EngineeringReference) -> None:
        """Add a reference to the result."""
        if not isinstance(reference, EngineeringReference):
            raise TypeError("Expected an EngineeringReference instance")
        self.references.append(reference)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "method": self.method,
            "scenario_id": self.scenario_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "units": self.units,
            "assumptions": [a.to_dict() for a in self.assumptions],
            "warnings": [w.to_dict() for w in self.warnings],
            "references": [r.to_dict() for r in self.references],
            "metadata": self.metadata,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CalculationResult:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            method=data["method"],
            scenario_id=data.get("scenario_id"),
            entity_id=data.get("entity_id"),
            entity_type=data.get("entity_type"),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            units=data.get("units", {}),
            assumptions=[
                EngineeringAssumption.from_dict(a)
                for a in data.get("assumptions", [])
            ],
            warnings=[
                ValidationWarning.from_dict(w)
                for w in data.get("warnings", [])
            ],
            references=[
                EngineeringReference.from_dict(r)
                for r in data.get("references", [])
            ],
            metadata=data.get("metadata", {}),
        )
