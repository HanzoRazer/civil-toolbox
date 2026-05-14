"""Flow path domain entities for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from civil_toolbox.domain.base import BaseEntity


@dataclass
class FlowPathSegment:
    """A segment of a flow path.

    Flow paths are typically composed of multiple segments with
    different flow characteristics (sheet flow, shallow concentrated,
    channel flow).
    """

    segment_type: str = "sheet"
    length_ft: float = 0.0
    slope_ft_per_ft: float = 0.0
    roughness_n: float | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if self.segment_type not in ("sheet", "shallow_concentrated", "channel"):
            raise ValueError(
                f"segment_type must be 'sheet', 'shallow_concentrated', or 'channel', "
                f"got '{self.segment_type}'"
            )
        if self.length_ft < 0:
            raise ValueError("length_ft cannot be negative")
        if self.slope_ft_per_ft < 0:
            raise ValueError("slope_ft_per_ft cannot be negative")
        if self.roughness_n is not None and self.roughness_n <= 0:
            raise ValueError("roughness_n must be positive")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "segment_type": self.segment_type,
            "length_ft": self.length_ft,
            "slope_ft_per_ft": self.slope_ft_per_ft,
            "roughness_n": self.roughness_n,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowPathSegment:
        """Deserialize from dictionary."""
        return cls(
            segment_type=data.get("segment_type", "sheet"),
            length_ft=data.get("length_ft", 0.0),
            slope_ft_per_ft=data.get("slope_ft_per_ft", 0.0),
            roughness_n=data.get("roughness_n"),
            description=data.get("description"),
        )


@dataclass
class FlowPath(BaseEntity):
    """A flow path within a scenario.

    Represents the path water travels from the hydraulically most
    distant point to the outlet, used for time of concentration
    calculations.
    """

    name: str = ""
    scenario_id: str | None = None
    segments: list[FlowPathSegment] = field(default_factory=list)
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("FlowPath requires a name")

    @property
    def total_length_ft(self) -> float:
        """Total length of all segments in feet."""
        return sum(s.length_ft for s in self.segments)

    def add_segment(self, segment: FlowPathSegment) -> None:
        """Add a segment to the flow path."""
        if not isinstance(segment, FlowPathSegment):
            raise TypeError("Expected a FlowPathSegment instance")
        self.segments.append(segment)
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "scenario_id": self.scenario_id,
            "segments": [s.to_dict() for s in self.segments],
            "description": self.description,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowPath:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            name=data["name"],
            scenario_id=data.get("scenario_id"),
            segments=[FlowPathSegment.from_dict(s) for s in data.get("segments", [])],
            description=data.get("description"),
        )
