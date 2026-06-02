"""Hydraulic result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError
from civil_toolbox.hydraulics.validation import (
    require_positive,
    require_non_negative,
    validate_severity,
    validate_surcharge_status,
)


def _generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid4())


@dataclass
class HydraulicWarning:
    """A warning generated during hydraulic analysis.

    Attributes:
        code: Warning code (e.g., 'steady_flow_assumption').
        message: Human-readable warning message.
        severity: Warning severity ('info', 'warning', 'error').
        entity_id: Optional ID of the related entity.
        metadata: Additional warning metadata.
    """

    code: str
    message: str
    severity: str = "warning"
    entity_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.code:
            raise InvalidHydraulicInputError("HydraulicWarning code cannot be empty")
        if not self.message:
            raise InvalidHydraulicInputError("HydraulicWarning message cannot be empty")
        self.severity = validate_severity(self.severity)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "entity_id": self.entity_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HydraulicWarning:
        """Deserialize from dictionary."""
        return cls(
            code=data["code"],
            message=data["message"],
            severity=data.get("severity", "warning"),
            entity_id=data.get("entity_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class PipeReachInput:
    """Input data for a pipe reach hydraulic calculation.

    Attributes:
        id: Unique reach identifier.
        pipe_id: ID of the source pipe.
        name: Human-readable name.
        design_flow_cfs: Design flow rate in cfs.
        length_ft: Reach length in feet.
        roughness_n: Manning's roughness coefficient.
        slope_ft_per_ft: Pipe slope (optional, can be derived from inverts).
        diameter_in: Pipe diameter for circular pipes.
        width_in: Pipe width for box/rectangular pipes.
        height_in: Pipe height for box/rectangular pipes.
        upstream_invert_elevation_ft: Upstream invert elevation.
        downstream_invert_elevation_ft: Downstream invert elevation.
        upstream_rim_elevation_ft: Upstream rim/ground elevation.
        downstream_rim_elevation_ft: Downstream rim/ground elevation.
        metadata: Additional metadata.
    """

    id: str
    pipe_id: str
    name: str
    design_flow_cfs: float
    length_ft: float
    roughness_n: float
    slope_ft_per_ft: float | None = None
    diameter_in: float | None = None
    width_in: float | None = None
    height_in: float | None = None
    upstream_invert_elevation_ft: float | None = None
    downstream_invert_elevation_ft: float | None = None
    upstream_rim_elevation_ft: float | None = None
    downstream_rim_elevation_ft: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise InvalidHydraulicInputError("PipeReachInput id cannot be empty")
        if not self.pipe_id:
            raise InvalidHydraulicInputError("PipeReachInput pipe_id cannot be empty")
        if not self.name:
            raise InvalidHydraulicInputError("PipeReachInput name cannot be empty")

        self.design_flow_cfs = require_non_negative(self.design_flow_cfs, "design_flow_cfs")
        self.length_ft = require_positive(self.length_ft, "length_ft")
        self.roughness_n = require_positive(self.roughness_n, "roughness_n")

        if self.diameter_in is not None:
            self.diameter_in = require_positive(self.diameter_in, "diameter_in")
        if self.width_in is not None:
            self.width_in = require_positive(self.width_in, "width_in")
        if self.height_in is not None:
            self.height_in = require_positive(self.height_in, "height_in")

    @property
    def is_circular(self) -> bool:
        """Check if this is a circular pipe."""
        return self.diameter_in is not None

    @property
    def is_rectangular(self) -> bool:
        """Check if this is a rectangular/box pipe."""
        return self.width_in is not None and self.height_in is not None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "pipe_id": self.pipe_id,
            "name": self.name,
            "design_flow_cfs": self.design_flow_cfs,
            "length_ft": self.length_ft,
            "roughness_n": self.roughness_n,
            "slope_ft_per_ft": self.slope_ft_per_ft,
            "diameter_in": self.diameter_in,
            "width_in": self.width_in,
            "height_in": self.height_in,
            "upstream_invert_elevation_ft": self.upstream_invert_elevation_ft,
            "downstream_invert_elevation_ft": self.downstream_invert_elevation_ft,
            "upstream_rim_elevation_ft": self.upstream_rim_elevation_ft,
            "downstream_rim_elevation_ft": self.downstream_rim_elevation_ft,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipeReachInput:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            pipe_id=data["pipe_id"],
            name=data["name"],
            design_flow_cfs=data["design_flow_cfs"],
            length_ft=data["length_ft"],
            roughness_n=data["roughness_n"],
            slope_ft_per_ft=data.get("slope_ft_per_ft"),
            diameter_in=data.get("diameter_in"),
            width_in=data.get("width_in"),
            height_in=data.get("height_in"),
            upstream_invert_elevation_ft=data.get("upstream_invert_elevation_ft"),
            downstream_invert_elevation_ft=data.get("downstream_invert_elevation_ft"),
            upstream_rim_elevation_ft=data.get("upstream_rim_elevation_ft"),
            downstream_rim_elevation_ft=data.get("downstream_rim_elevation_ft"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class PipeReachHydraulicResult:
    """Result of a single pipe reach hydraulic calculation.

    Attributes:
        reach_id: ID of the reach.
        pipe_id: ID of the source pipe.
        design_flow_cfs: Design flow rate in cfs.
        flow_area_sqft: Flow area in square feet.
        velocity_fps: Flow velocity in feet per second.
        velocity_head_ft: Velocity head in feet.
        friction_slope_ft_per_ft: Friction slope.
        friction_loss_ft: Friction head loss in feet.
        downstream_hgl_ft: HGL at downstream end.
        upstream_hgl_ft: HGL at upstream end.
        downstream_egl_ft: EGL at downstream end.
        upstream_egl_ft: EGL at upstream end.
        downstream_crown_elevation_ft: Pipe crown at downstream.
        upstream_crown_elevation_ft: Pipe crown at upstream.
        downstream_rim_elevation_ft: Rim elevation at downstream.
        upstream_rim_elevation_ft: Rim elevation at upstream.
        downstream_freeboard_ft: Freeboard to rim at downstream.
        upstream_freeboard_ft: Freeboard to rim at upstream.
        downstream_surcharge_status: Surcharge status at downstream end.
        upstream_surcharge_status: Surcharge status at upstream end.
        warnings: List of warnings generated.
        metadata: Additional metadata.
    """

    reach_id: str
    pipe_id: str
    design_flow_cfs: float
    flow_area_sqft: float
    velocity_fps: float
    velocity_head_ft: float
    friction_slope_ft_per_ft: float
    friction_loss_ft: float
    downstream_hgl_ft: float
    upstream_hgl_ft: float
    downstream_egl_ft: float
    upstream_egl_ft: float
    downstream_crown_elevation_ft: float | None = None
    upstream_crown_elevation_ft: float | None = None
    downstream_rim_elevation_ft: float | None = None
    upstream_rim_elevation_ft: float | None = None
    downstream_freeboard_ft: float | None = None
    upstream_freeboard_ft: float | None = None
    downstream_surcharge_status: str = "unknown"
    upstream_surcharge_status: str = "unknown"
    warnings: list[HydraulicWarning] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.downstream_surcharge_status = validate_surcharge_status(
            self.downstream_surcharge_status
        )
        self.upstream_surcharge_status = validate_surcharge_status(
            self.upstream_surcharge_status
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "reach_id": self.reach_id,
            "pipe_id": self.pipe_id,
            "design_flow_cfs": self.design_flow_cfs,
            "flow_area_sqft": self.flow_area_sqft,
            "velocity_fps": self.velocity_fps,
            "velocity_head_ft": self.velocity_head_ft,
            "friction_slope_ft_per_ft": self.friction_slope_ft_per_ft,
            "friction_loss_ft": self.friction_loss_ft,
            "downstream_hgl_ft": self.downstream_hgl_ft,
            "upstream_hgl_ft": self.upstream_hgl_ft,
            "downstream_egl_ft": self.downstream_egl_ft,
            "upstream_egl_ft": self.upstream_egl_ft,
            "downstream_crown_elevation_ft": self.downstream_crown_elevation_ft,
            "upstream_crown_elevation_ft": self.upstream_crown_elevation_ft,
            "downstream_rim_elevation_ft": self.downstream_rim_elevation_ft,
            "upstream_rim_elevation_ft": self.upstream_rim_elevation_ft,
            "downstream_freeboard_ft": self.downstream_freeboard_ft,
            "upstream_freeboard_ft": self.upstream_freeboard_ft,
            "downstream_surcharge_status": self.downstream_surcharge_status,
            "upstream_surcharge_status": self.upstream_surcharge_status,
            "warnings": [w.to_dict() for w in self.warnings],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipeReachHydraulicResult:
        """Deserialize from dictionary."""
        return cls(
            reach_id=data["reach_id"],
            pipe_id=data["pipe_id"],
            design_flow_cfs=data["design_flow_cfs"],
            flow_area_sqft=data["flow_area_sqft"],
            velocity_fps=data["velocity_fps"],
            velocity_head_ft=data["velocity_head_ft"],
            friction_slope_ft_per_ft=data["friction_slope_ft_per_ft"],
            friction_loss_ft=data["friction_loss_ft"],
            downstream_hgl_ft=data["downstream_hgl_ft"],
            upstream_hgl_ft=data["upstream_hgl_ft"],
            downstream_egl_ft=data["downstream_egl_ft"],
            upstream_egl_ft=data["upstream_egl_ft"],
            downstream_crown_elevation_ft=data.get("downstream_crown_elevation_ft"),
            upstream_crown_elevation_ft=data.get("upstream_crown_elevation_ft"),
            downstream_rim_elevation_ft=data.get("downstream_rim_elevation_ft"),
            upstream_rim_elevation_ft=data.get("upstream_rim_elevation_ft"),
            downstream_freeboard_ft=data.get("downstream_freeboard_ft"),
            upstream_freeboard_ft=data.get("upstream_freeboard_ft"),
            downstream_surcharge_status=data.get("downstream_surcharge_status", "unknown"),
            upstream_surcharge_status=data.get("upstream_surcharge_status", "unknown"),
            warnings=[HydraulicWarning.from_dict(w) for w in data.get("warnings", [])],
            metadata=data.get("metadata", {}),
        )


@dataclass
class HydraulicProfileResult:
    """Result of a hydraulic profile calculation.

    Attributes:
        id: Unique profile identifier.
        name: Profile name.
        profile_type: Type of profile ('hgl', 'egl', etc.).
        reaches: List of reach results, downstream to upstream.
        starting_downstream_hgl_ft: Starting HGL at downstream boundary.
        ending_upstream_hgl_ft: Final HGL at upstream end of last reach.
        warnings: Aggregated warnings from all reaches.
        assumptions: List of assumptions made.
        references: Engineering references.
        metadata: Additional metadata.
    """

    id: str = field(default_factory=_generate_id)
    name: str = "Hydraulic Grade Line Profile"
    profile_type: str = "hgl"
    reaches: list[PipeReachHydraulicResult] = field(default_factory=list)
    starting_downstream_hgl_ft: float = 0.0
    ending_upstream_hgl_ft: float | None = None
    warnings: list[HydraulicWarning] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_warnings(self) -> bool:
        """Check if profile or any reach has warnings.

        Returns:
            True if any warnings exist.
        """
        if self.warnings:
            return True
        return any(r.warnings for r in self.reaches)

    def all_warnings(self) -> list[HydraulicWarning]:
        """Get all warnings from profile and reaches.

        Returns:
            Combined list of all warnings.
        """
        result = list(self.warnings)
        for reach in self.reaches:
            result.extend(reach.warnings)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "profile_type": self.profile_type,
            "reaches": [r.to_dict() for r in self.reaches],
            "starting_downstream_hgl_ft": self.starting_downstream_hgl_ft,
            "ending_upstream_hgl_ft": self.ending_upstream_hgl_ft,
            "warnings": [w.to_dict() for w in self.warnings],
            "assumptions": list(self.assumptions),
            "references": list(self.references),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HydraulicProfileResult:
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", _generate_id()),
            name=data.get("name", "Hydraulic Grade Line Profile"),
            profile_type=data.get("profile_type", "hgl"),
            reaches=[PipeReachHydraulicResult.from_dict(r) for r in data.get("reaches", [])],
            starting_downstream_hgl_ft=data.get("starting_downstream_hgl_ft", 0.0),
            ending_upstream_hgl_ft=data.get("ending_upstream_hgl_ft"),
            warnings=[HydraulicWarning.from_dict(w) for w in data.get("warnings", [])],
            assumptions=data.get("assumptions", []),
            references=data.get("references", []),
            metadata=data.get("metadata", {}),
        )
