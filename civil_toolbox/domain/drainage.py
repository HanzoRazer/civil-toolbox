"""Drainage area domain entity for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from civil_toolbox.domain.base import BaseEntity


@dataclass
class DrainageArea(BaseEntity):
    """A drainage area within a scenario.

    Represents a contributing watershed or subbasin with hydrologic
    properties used for runoff calculations.
    """

    name: str = ""
    scenario_id: str | None = None
    area_acres: float | None = None
    runoff_coefficient: float | None = None
    curve_number: int | None = None
    soil_group: str | None = None
    land_use: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("DrainageArea requires a name")
        if self.area_acres is not None and self.area_acres <= 0:
            raise ValueError("area_acres must be positive")
        if self.runoff_coefficient is not None:
            if not 0 <= self.runoff_coefficient <= 1:
                raise ValueError("runoff_coefficient must be between 0 and 1")
        if self.curve_number is not None:
            if not 0 <= self.curve_number <= 100:
                raise ValueError("curve_number must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "scenario_id": self.scenario_id,
            "area_acres": self.area_acres,
            "runoff_coefficient": self.runoff_coefficient,
            "curve_number": self.curve_number,
            "soil_group": self.soil_group,
            "land_use": self.land_use,
            "description": self.description,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DrainageArea:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            name=data["name"],
            scenario_id=data.get("scenario_id"),
            area_acres=data.get("area_acres"),
            runoff_coefficient=data.get("runoff_coefficient"),
            curve_number=data.get("curve_number"),
            soil_group=data.get("soil_group"),
            land_use=data.get("land_use"),
            description=data.get("description"),
        )
