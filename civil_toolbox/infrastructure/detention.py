"""Detention facility infrastructure model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.infrastructure.base import InfrastructureElementBase, ElementType
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError
from civil_toolbox.infrastructure.validation import (
    validate_positive,
    validate_non_negative,
)


@dataclass
class StageStoragePoint:
    """A single point in the stage-storage relationship."""

    stage_ft: float
    storage_cuft: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "stage_ft": self.stage_ft,
            "storage_cuft": self.storage_cuft,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StageStoragePoint:
        """Deserialize from dictionary."""
        return cls(
            stage_ft=data["stage_ft"],
            storage_cuft=data["storage_cuft"],
        )


@dataclass
class DetentionFacility(InfrastructureElementBase):
    """A detention/retention facility for stormwater storage.

    Can be defined by simple geometry or stage-storage curve.
    """

    element_type: ElementType = field(default=ElementType.DETENTION, init=False)

    facility_type: str = "detention"
    pond_bottom_elevation_ft: float = 0.0
    pond_bottom_area_sqft: float | None = None
    side_slope: float | None = None
    maximum_depth_ft: float | None = None
    permanent_pool_depth_ft: float | None = None

    stage_storage: list[StageStoragePoint] = field(default_factory=list)

    outlet_node_id: str | None = None
    spillway_elevation_ft: float | None = None
    spillway_width_ft: float | None = None

    def __post_init__(self) -> None:
        valid_types = {"detention", "retention", "infiltration", "constructed_wetland"}
        if self.facility_type not in valid_types:
            raise InvalidInfrastructureError(
                f"facility_type must be one of {sorted(valid_types)}, "
                f"got '{self.facility_type}'"
            )

        if self.pond_bottom_area_sqft is not None:
            validate_positive(self.pond_bottom_area_sqft, "pond_bottom_area_sqft")
        if self.side_slope is not None:
            validate_non_negative(self.side_slope, "side_slope")
        if self.maximum_depth_ft is not None:
            validate_positive(self.maximum_depth_ft, "maximum_depth_ft")
        if self.permanent_pool_depth_ft is not None:
            validate_non_negative(self.permanent_pool_depth_ft, "permanent_pool_depth_ft")
        if self.spillway_width_ft is not None:
            validate_positive(self.spillway_width_ft, "spillway_width_ft")

        if self.stage_storage:
            stages = [p.stage_ft for p in self.stage_storage]
            if stages != sorted(stages):
                raise InvalidInfrastructureError(
                    "stage_storage must be sorted by increasing stage_ft"
                )

    @property
    def total_storage_cuft(self) -> float | None:
        """Maximum storage volume from stage-storage curve."""
        if self.stage_storage:
            return max(p.storage_cuft for p in self.stage_storage)
        return None

    def storage_at_stage(self, stage_ft: float) -> float | None:
        """Interpolate storage volume at a given stage.

        Returns None if stage is outside the defined range.
        """
        if not self.stage_storage:
            return None

        if stage_ft < self.stage_storage[0].stage_ft:
            return 0.0
        if stage_ft >= self.stage_storage[-1].stage_ft:
            return self.stage_storage[-1].storage_cuft

        for i in range(len(self.stage_storage) - 1):
            p1 = self.stage_storage[i]
            p2 = self.stage_storage[i + 1]
            if p1.stage_ft <= stage_ft < p2.stage_ft:
                ratio = (stage_ft - p1.stage_ft) / (p2.stage_ft - p1.stage_ft)
                return p1.storage_cuft + ratio * (p2.storage_cuft - p1.storage_cuft)
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "facility_type": self.facility_type,
            "pond_bottom_elevation_ft": self.pond_bottom_elevation_ft,
            "pond_bottom_area_sqft": self.pond_bottom_area_sqft,
            "side_slope": self.side_slope,
            "maximum_depth_ft": self.maximum_depth_ft,
            "permanent_pool_depth_ft": self.permanent_pool_depth_ft,
            "stage_storage": [p.to_dict() for p in self.stage_storage],
            "outlet_node_id": self.outlet_node_id,
            "spillway_elevation_ft": self.spillway_elevation_ft,
            "spillway_width_ft": self.spillway_width_ft,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DetentionFacility:
        """Deserialize from dictionary."""
        stage_storage = [
            StageStoragePoint.from_dict(p) for p in data.get("stage_storage", [])
        ]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            facility_type=data.get("facility_type", "detention"),
            pond_bottom_elevation_ft=data.get("pond_bottom_elevation_ft", 0.0),
            pond_bottom_area_sqft=data.get("pond_bottom_area_sqft"),
            side_slope=data.get("side_slope"),
            maximum_depth_ft=data.get("maximum_depth_ft"),
            permanent_pool_depth_ft=data.get("permanent_pool_depth_ft"),
            stage_storage=stage_storage,
            outlet_node_id=data.get("outlet_node_id"),
            spillway_elevation_ft=data.get("spillway_elevation_ft"),
            spillway_width_ft=data.get("spillway_width_ft"),
        )
