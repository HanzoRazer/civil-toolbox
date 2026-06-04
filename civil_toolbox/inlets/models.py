"""Inlet capacity result models.

Standalone result models (mirroring the hydraulics and culvert foundations).
References and assumptions are ``list[str]`` for consistency; the model is shaped
so a later adapter can map an ``InletCapacityResult`` onto the domain
``CalculationResult`` audit type without rework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from civil_toolbox.inlets.errors import InvalidInletInputError
from civil_toolbox.inlets.validation import validate_status


def _generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid4())


@dataclass
class InletCapacityWarning:
    """A warning generated during inlet capacity analysis.

    Attributes:
        code: Warning code (e.g., 'simplified_orifice_assumption').
        message: Human-readable warning message.
        severity: Warning severity ('info', 'warning', 'error').
        metadata: Additional warning metadata.
    """

    code: str
    message: str
    severity: str = "warning"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.code:
            raise InvalidInletInputError("InletCapacityWarning code cannot be empty")
        if not self.message:
            raise InvalidInletInputError("InletCapacityWarning message cannot be empty")
        if self.severity not in {"info", "warning", "error"}:
            raise InvalidInletInputError(
                f"severity must be one of ['error', 'info', 'warning'], "
                f"got '{self.severity}'"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InletCapacityWarning:
        """Deserialize from dictionary."""
        return cls(
            code=data["code"],
            message=data["message"],
            severity=data.get("severity", "warning"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class InletCapacityResult:
    """Result of a single inlet capacity check.

    Attributes:
        id: Unique result identifier.
        inlet_id: ID of the analyzed inlet.
        inlet_type: Inlet type ('grate', 'curb_opening', 'combination', 'slotted').
        design_flow_cfs: Supplied design flow approaching the inlet, in cfs.
        captured_flow_cfs: Flow intercepted by the inlet, in cfs.
        bypass_flow_cfs: Flow that bypasses the inlet, in cfs.
        capture_efficiency: captured / design (0-1), or None if design flow is 0.
        capacity_cfs: Estimated interception capacity, in cfs.
        status: 'pass' | 'fail' | 'warning' | 'not_evaluated'.
        warnings: Warnings generated during analysis.
        assumptions: Assumptions made (plain strings).
        references: Engineering references (plain strings).
        metadata: Additional metadata.
    """

    id: str = field(default_factory=_generate_id)
    inlet_id: str = ""
    inlet_type: str = ""
    design_flow_cfs: float = 0.0
    captured_flow_cfs: float = 0.0
    bypass_flow_cfs: float = 0.0
    capture_efficiency: float | None = None
    capacity_cfs: float = 0.0
    status: str = "not_evaluated"
    warnings: list[InletCapacityWarning] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.status = validate_status(self.status)

    def has_warnings(self) -> bool:
        """Return True if any warnings were generated."""
        return bool(self.warnings)

    def add_warning(
        self,
        code: str,
        message: str,
        severity: str = "warning",
        metadata: dict[str, Any] | None = None,
    ) -> InletCapacityWarning:
        """Append a warning and return it."""
        warning = InletCapacityWarning(
            code=code,
            message=message,
            severity=severity,
            metadata=metadata or {},
        )
        self.warnings.append(warning)
        return warning

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "inlet_id": self.inlet_id,
            "inlet_type": self.inlet_type,
            "design_flow_cfs": self.design_flow_cfs,
            "captured_flow_cfs": self.captured_flow_cfs,
            "bypass_flow_cfs": self.bypass_flow_cfs,
            "capture_efficiency": self.capture_efficiency,
            "capacity_cfs": self.capacity_cfs,
            "status": self.status,
            "warnings": [w.to_dict() for w in self.warnings],
            "assumptions": list(self.assumptions),
            "references": list(self.references),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InletCapacityResult:
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", _generate_id()),
            inlet_id=data.get("inlet_id", ""),
            inlet_type=data.get("inlet_type", ""),
            design_flow_cfs=data.get("design_flow_cfs", 0.0),
            captured_flow_cfs=data.get("captured_flow_cfs", 0.0),
            bypass_flow_cfs=data.get("bypass_flow_cfs", 0.0),
            capture_efficiency=data.get("capture_efficiency"),
            capacity_cfs=data.get("capacity_cfs", 0.0),
            status=data.get("status", "not_evaluated"),
            warnings=[
                InletCapacityWarning.from_dict(w) for w in data.get("warnings", [])
            ],
            assumptions=data.get("assumptions", []),
            references=data.get("references", []),
            metadata=data.get("metadata", {}),
        )


def apply_capture_outcome(
    result: InletCapacityResult,
    capacity_cfs: float,
    design_flow_cfs: float,
) -> InletCapacityResult:
    """Populate capture/bypass/efficiency/status on a result from a capacity.

    Captured flow is the lesser of capacity and the approaching design flow;
    bypass is the remainder; status passes when capacity meets the design flow.

    Args:
        result: The result to populate (mutated in place).
        capacity_cfs: Estimated interception capacity.
        design_flow_cfs: Approaching design flow.

    Returns:
        The same result, for chaining.
    """
    captured = min(capacity_cfs, design_flow_cfs)
    result.capacity_cfs = capacity_cfs
    result.captured_flow_cfs = captured
    result.bypass_flow_cfs = max(design_flow_cfs - captured, 0.0)
    result.capture_efficiency = (
        captured / design_flow_cfs if design_flow_cfs > 0 else None
    )
    result.status = "pass" if captured >= design_flow_cfs else "fail"
    return result
