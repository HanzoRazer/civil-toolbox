"""Culvert analysis result models.

These are standalone result models (mirroring the hydraulics foundation's
``HydraulicProfileResult``). The shape is deliberately kept adapter-friendly:
``inputs``/``outputs``-style data is exposed as flat fields plus a ``metadata``
dict so a later adapter can map a ``CulvertAnalysisResult`` onto the domain
``CalculationResult`` audit type without reworking this model.

References and assumptions are ``list[str]`` for consistency with the sibling
hydraulics foundation. They can be upgraded to structured
``EngineeringReference``/``EngineeringAssumption`` objects if/when all analysis
subsystems are standardized.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from civil_toolbox.culverts.errors import InvalidCulvertInputError
from civil_toolbox.culverts.validation import (
    validate_control_status,
    validate_governing_control,
    validate_severity,
)


def _generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid4())


@dataclass
class CulvertAnalysisWarning:
    """A warning generated during culvert analysis.

    Attributes:
        code: Warning code (e.g., 'unsubmerged_inlet').
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
            raise InvalidCulvertInputError("CulvertAnalysisWarning code cannot be empty")
        if not self.message:
            raise InvalidCulvertInputError(
                "CulvertAnalysisWarning message cannot be empty"
            )
        self.severity = validate_severity(self.severity)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CulvertAnalysisWarning:
        """Deserialize from dictionary."""
        return cls(
            code=data["code"],
            message=data["message"],
            severity=data.get("severity", "warning"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CulvertAnalysisResult:
    """Result of a single-barrel culvert analysis.

    Headwater is reported both as a depth above the inlet invert
    (``headwater_depth_ft``, always available when computed) and, when the
    inlet invert elevation is known, as an absolute elevation
    (``headwater_elevation_ft``).

    Attributes:
        id: Unique result identifier.
        culvert_id: ID of the analyzed culvert.
        design_flow_cfs: Design flow rate in cfs.
        barrel_capacity_cfs: Manning full-barrel capacity in cfs (reused from
            the infrastructure sizing layer), or None if not computable.
        headwater_depth_ft: Governing headwater depth above the inlet invert.
        headwater_elevation_ft: Governing headwater elevation (depth + inlet
            invert elevation), or None if the invert elevation is unknown.
        inlet_control_headwater_ft: Headwater depth under inlet control.
        outlet_control_headwater_ft: Headwater depth under outlet control.
        governing_control: Which control governs ('inlet', 'outlet', 'unknown').
        inlet_control_status: Status vs. allowable headwater under inlet control.
        outlet_control_status: Status vs. allowable headwater under outlet control.
        barrel_velocity_fps: Full-barrel velocity in fps, or None.
        warnings: Warnings generated during analysis.
        assumptions: Assumptions made (plain strings).
        references: Engineering references (plain strings).
        metadata: Additional metadata.
    """

    id: str = field(default_factory=_generate_id)
    culvert_id: str = ""
    design_flow_cfs: float = 0.0
    barrel_capacity_cfs: float | None = None
    headwater_depth_ft: float | None = None
    headwater_elevation_ft: float | None = None
    inlet_control_headwater_ft: float | None = None
    outlet_control_headwater_ft: float | None = None
    governing_control: str = "unknown"
    inlet_control_status: str = "unknown"
    outlet_control_status: str = "unknown"
    barrel_velocity_fps: float | None = None
    warnings: list[CulvertAnalysisWarning] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.governing_control = validate_governing_control(self.governing_control)
        self.inlet_control_status = validate_control_status(self.inlet_control_status)
        self.outlet_control_status = validate_control_status(self.outlet_control_status)

    def has_warnings(self) -> bool:
        """Return True if any warnings were generated."""
        return bool(self.warnings)

    def add_warning(
        self,
        code: str,
        message: str,
        severity: str = "warning",
        metadata: dict[str, Any] | None = None,
    ) -> CulvertAnalysisWarning:
        """Append a warning and return it."""
        warning = CulvertAnalysisWarning(
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
            "culvert_id": self.culvert_id,
            "design_flow_cfs": self.design_flow_cfs,
            "barrel_capacity_cfs": self.barrel_capacity_cfs,
            "headwater_depth_ft": self.headwater_depth_ft,
            "headwater_elevation_ft": self.headwater_elevation_ft,
            "inlet_control_headwater_ft": self.inlet_control_headwater_ft,
            "outlet_control_headwater_ft": self.outlet_control_headwater_ft,
            "governing_control": self.governing_control,
            "inlet_control_status": self.inlet_control_status,
            "outlet_control_status": self.outlet_control_status,
            "barrel_velocity_fps": self.barrel_velocity_fps,
            "warnings": [w.to_dict() for w in self.warnings],
            "assumptions": list(self.assumptions),
            "references": list(self.references),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CulvertAnalysisResult:
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", _generate_id()),
            culvert_id=data.get("culvert_id", ""),
            design_flow_cfs=data.get("design_flow_cfs", 0.0),
            barrel_capacity_cfs=data.get("barrel_capacity_cfs"),
            headwater_depth_ft=data.get("headwater_depth_ft"),
            headwater_elevation_ft=data.get("headwater_elevation_ft"),
            inlet_control_headwater_ft=data.get("inlet_control_headwater_ft"),
            outlet_control_headwater_ft=data.get("outlet_control_headwater_ft"),
            governing_control=data.get("governing_control", "unknown"),
            inlet_control_status=data.get("inlet_control_status", "unknown"),
            outlet_control_status=data.get("outlet_control_status", "unknown"),
            barrel_velocity_fps=data.get("barrel_velocity_fps"),
            warnings=[
                CulvertAnalysisWarning.from_dict(w) for w in data.get("warnings", [])
            ],
            assumptions=data.get("assumptions", []),
            references=data.get("references", []),
            metadata=data.get("metadata", {}),
        )
