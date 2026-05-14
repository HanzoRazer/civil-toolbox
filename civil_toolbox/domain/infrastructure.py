"""Infrastructure domain entity for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from civil_toolbox.domain.base import BaseEntity


@dataclass
class InfrastructureElement(BaseEntity):
    """An infrastructure element within a scenario.

    Represents drainage infrastructure such as pipes, culverts,
    channels, inlets, and detention facilities.
    """

    name: str = ""
    scenario_id: str | None = None
    element_type: str = "pipe"
    description: str | None = None

    # Geometry - common fields
    length_ft: float | None = None
    slope_ft_per_ft: float | None = None

    # Pipe/culvert specific
    diameter_in: float | None = None
    material: str | None = None
    mannings_n: float | None = None

    # Channel specific
    bottom_width_ft: float | None = None
    side_slope: float | None = None
    depth_ft: float | None = None

    # Capacity
    capacity_cfs: float | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("InfrastructureElement requires a name")
        valid_types = ("pipe", "culvert", "channel", "inlet", "detention", "outlet")
        if self.element_type not in valid_types:
            raise ValueError(
                f"element_type must be one of {valid_types}, got '{self.element_type}'"
            )
        if self.length_ft is not None and self.length_ft < 0:
            raise ValueError("length_ft cannot be negative")
        if self.slope_ft_per_ft is not None and self.slope_ft_per_ft < 0:
            raise ValueError("slope_ft_per_ft cannot be negative")
        if self.diameter_in is not None and self.diameter_in <= 0:
            raise ValueError("diameter_in must be positive")
        if self.mannings_n is not None and self.mannings_n <= 0:
            raise ValueError("mannings_n must be positive")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "scenario_id": self.scenario_id,
            "element_type": self.element_type,
            "description": self.description,
            "length_ft": self.length_ft,
            "slope_ft_per_ft": self.slope_ft_per_ft,
            "diameter_in": self.diameter_in,
            "material": self.material,
            "mannings_n": self.mannings_n,
            "bottom_width_ft": self.bottom_width_ft,
            "side_slope": self.side_slope,
            "depth_ft": self.depth_ft,
            "capacity_cfs": self.capacity_cfs,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureElement:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            name=data["name"],
            scenario_id=data.get("scenario_id"),
            element_type=data.get("element_type", "pipe"),
            description=data.get("description"),
            length_ft=data.get("length_ft"),
            slope_ft_per_ft=data.get("slope_ft_per_ft"),
            diameter_in=data.get("diameter_in"),
            material=data.get("material"),
            mannings_n=data.get("mannings_n"),
            bottom_width_ft=data.get("bottom_width_ft"),
            side_slope=data.get("side_slope"),
            depth_ft=data.get("depth_ft"),
            capacity_cfs=data.get("capacity_cfs"),
        )
