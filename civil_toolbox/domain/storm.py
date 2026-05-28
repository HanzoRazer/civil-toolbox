"""Storm event domain entity for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from civil_toolbox.domain.base import BaseEntity


@dataclass
class StormEvent(BaseEntity):
    """A storm event within a scenario.

    Represents rainfall characteristics for a design storm or
    historical event used in runoff calculations.
    """

    name: str = ""
    scenario_id: str | None = None
    return_period_years: int | None = None
    duration_hours: float | None = None
    rainfall_depth_in: float | None = None
    rainfall_intensity_in_per_hr: float | None = None
    distribution: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("StormEvent requires a name")
        if self.return_period_years is not None and self.return_period_years <= 0:
            raise ValueError("return_period_years must be positive")
        if self.duration_hours is not None and self.duration_hours <= 0:
            raise ValueError("duration_hours must be positive")
        if self.rainfall_depth_in is not None and self.rainfall_depth_in < 0:
            raise ValueError("rainfall_depth_in cannot be negative")
        if self.rainfall_intensity_in_per_hr is not None and self.rainfall_intensity_in_per_hr < 0:
            raise ValueError("rainfall_intensity_in_per_hr cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "scenario_id": self.scenario_id,
            "return_period_years": self.return_period_years,
            "duration_hours": self.duration_hours,
            "rainfall_depth_in": self.rainfall_depth_in,
            "rainfall_intensity_in_per_hr": self.rainfall_intensity_in_per_hr,
            "distribution": self.distribution,
            "description": self.description,
            "metadata": self.metadata,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StormEvent:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            name=data["name"],
            scenario_id=data.get("scenario_id"),
            return_period_years=data.get("return_period_years"),
            duration_hours=data.get("duration_hours"),
            rainfall_depth_in=data.get("rainfall_depth_in"),
            rainfall_intensity_in_per_hr=data.get("rainfall_intensity_in_per_hr"),
            distribution=data.get("distribution"),
            description=data.get("description"),
            metadata=data.get("metadata", {}),
        )
