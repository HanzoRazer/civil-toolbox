"""Infrastructure schedule model for tabular reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InfrastructureScheduleRow:
    """A single row in an infrastructure schedule.

    Used for generating pipe schedules, inlet schedules, etc.
    """

    element_id: str
    element_name: str
    element_type: str
    station: str | None = None
    description: str | None = None

    size: str | None = None
    material: str | None = None
    length_ft: float | None = None
    slope_percent: float | None = None
    invert_in_ft: float | None = None
    invert_out_ft: float | None = None
    rim_elevation_ft: float | None = None

    capacity_cfs: float | None = None
    velocity_fps: float | None = None

    notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "element_id": self.element_id,
            "element_name": self.element_name,
            "element_type": self.element_type,
            "station": self.station,
            "description": self.description,
            "size": self.size,
            "material": self.material,
            "length_ft": self.length_ft,
            "slope_percent": self.slope_percent,
            "invert_in_ft": self.invert_in_ft,
            "invert_out_ft": self.invert_out_ft,
            "rim_elevation_ft": self.rim_elevation_ft,
            "capacity_cfs": self.capacity_cfs,
            "velocity_fps": self.velocity_fps,
            "notes": self.notes,
            "metadata": self.metadata.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureScheduleRow:
        """Deserialize from dictionary."""
        return cls(
            element_id=data["element_id"],
            element_name=data["element_name"],
            element_type=data["element_type"],
            station=data.get("station"),
            description=data.get("description"),
            size=data.get("size"),
            material=data.get("material"),
            length_ft=data.get("length_ft"),
            slope_percent=data.get("slope_percent"),
            invert_in_ft=data.get("invert_in_ft"),
            invert_out_ft=data.get("invert_out_ft"),
            rim_elevation_ft=data.get("rim_elevation_ft"),
            capacity_cfs=data.get("capacity_cfs"),
            velocity_fps=data.get("velocity_fps"),
            notes=data.get("notes"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class InfrastructureSchedule:
    """A schedule (table) of infrastructure elements.

    Used for generating pipe schedules, structure schedules, etc.
    """

    name: str
    schedule_type: str
    rows: list[InfrastructureScheduleRow] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_row(self, row: InfrastructureScheduleRow) -> None:
        """Add a row to the schedule."""
        self.rows.append(row)

    def __len__(self) -> int:
        """Number of rows in the schedule."""
        return len(self.rows)

    def __iter__(self):
        """Iterate over rows."""
        return iter(self.rows)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "schedule_type": self.schedule_type,
            "rows": [r.to_dict() for r in self.rows],
            "metadata": self.metadata.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureSchedule:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            schedule_type=data["schedule_type"],
            rows=[InfrastructureScheduleRow.from_dict(r) for r in data.get("rows", [])],
            metadata=data.get("metadata", {}),
        )
