"""Data models for infrastructure sizing results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InfrastructureCheckWarning:
    """A warning generated during infrastructure capacity check.

    Non-fatal issues that should be reviewed but don't prevent analysis.
    """

    warning_code: str
    message: str
    element_id: str | None = None
    element_name: str | None = None
    severity: str = "warning"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "warning_code": self.warning_code,
            "message": self.message,
            "element_id": self.element_id,
            "element_name": self.element_name,
            "severity": self.severity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureCheckWarning:
        """Deserialize from dictionary."""
        return cls(
            warning_code=data["warning_code"],
            message=data["message"],
            element_id=data.get("element_id"),
            element_name=data.get("element_name"),
            severity=data.get("severity", "warning"),
        )


@dataclass
class InfrastructureCheckResult:
    """Result of an infrastructure capacity check.

    Contains capacity, utilization, pass/fail status, and any warnings.
    """

    element_id: str
    element_name: str
    element_type: str
    passes: bool
    capacity_cfs: float | None = None
    design_flow_cfs: float | None = None
    utilization_ratio: float | None = None
    velocity_fps: float | None = None
    storage_cuft: float | None = None
    required_storage_cuft: float | None = None
    warnings: list[InfrastructureCheckWarning] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    method: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.capacity_cfs is not None and self.design_flow_cfs is not None:
            if self.design_flow_cfs > 0:
                self.utilization_ratio = self.design_flow_cfs / self.capacity_cfs

    def add_warning(
        self,
        warning_code: str,
        message: str,
        severity: str = "warning",
    ) -> None:
        """Add a warning to this result."""
        self.warnings.append(
            InfrastructureCheckWarning(
                warning_code=warning_code,
                message=message,
                element_id=self.element_id,
                element_name=self.element_name,
                severity=severity,
            )
        )

    def add_assumption(self, assumption: str) -> None:
        """Add an assumption to this result."""
        self.assumptions.append(assumption)

    @property
    def is_overcapacity(self) -> bool:
        """Check if design flow exceeds capacity."""
        if self.utilization_ratio is not None:
            return self.utilization_ratio > 1.0
        return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "element_id": self.element_id,
            "element_name": self.element_name,
            "element_type": self.element_type,
            "passes": self.passes,
            "capacity_cfs": self.capacity_cfs,
            "design_flow_cfs": self.design_flow_cfs,
            "utilization_ratio": self.utilization_ratio,
            "velocity_fps": self.velocity_fps,
            "storage_cuft": self.storage_cuft,
            "required_storage_cuft": self.required_storage_cuft,
            "warnings": [w.to_dict() for w in self.warnings],
            "assumptions": self.assumptions.copy(),
            "method": self.method,
            "metadata": self.metadata.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureCheckResult:
        """Deserialize from dictionary."""
        result = cls(
            element_id=data["element_id"],
            element_name=data["element_name"],
            element_type=data["element_type"],
            passes=data["passes"],
            capacity_cfs=data.get("capacity_cfs"),
            design_flow_cfs=data.get("design_flow_cfs"),
            velocity_fps=data.get("velocity_fps"),
            storage_cuft=data.get("storage_cuft"),
            required_storage_cuft=data.get("required_storage_cuft"),
            warnings=[
                InfrastructureCheckWarning.from_dict(w)
                for w in data.get("warnings", [])
            ],
            assumptions=data.get("assumptions", []),
            method=data.get("method", ""),
            metadata=data.get("metadata", {}),
        )
        result.utilization_ratio = data.get("utilization_ratio")
        return result
