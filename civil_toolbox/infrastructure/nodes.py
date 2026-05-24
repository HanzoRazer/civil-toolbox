"""Infrastructure node model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.infrastructure.base import InfrastructureElementBase, ElementType
from civil_toolbox.infrastructure.validation import validate_non_negative


@dataclass
class InfrastructureNode(InfrastructureElementBase):
    """A node in the infrastructure network.

    Nodes represent connection points where elements meet: junctions,
    manholes, inlets, outfalls, etc.
    """

    element_type: ElementType = field(default=ElementType.NODE, init=False)
    node_type: str = "junction"
    invert_elevation_ft: float | None = None
    rim_elevation_ft: float | None = None
    ground_elevation_ft: float | None = None
    x_coordinate: float | None = None
    y_coordinate: float | None = None

    def __post_init__(self) -> None:
        valid_node_types = {
            "junction",
            "manhole",
            "inlet",
            "outfall",
            "storage",
            "divider",
        }
        if self.node_type not in valid_node_types:
            from civil_toolbox.infrastructure.errors import InvalidInfrastructureError

            raise InvalidInfrastructureError(
                f"node_type must be one of {sorted(valid_node_types)}, "
                f"got '{self.node_type}'"
            )

    @property
    def depth_ft(self) -> float | None:
        """Depth from rim to invert, if both are defined."""
        if self.rim_elevation_ft is not None and self.invert_elevation_ft is not None:
            return self.rim_elevation_ft - self.invert_elevation_ft
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "node_type": self.node_type,
            "invert_elevation_ft": self.invert_elevation_ft,
            "rim_elevation_ft": self.rim_elevation_ft,
            "ground_elevation_ft": self.ground_elevation_ft,
            "x_coordinate": self.x_coordinate,
            "y_coordinate": self.y_coordinate,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureNode:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            node_type=data.get("node_type", "junction"),
            invert_elevation_ft=data.get("invert_elevation_ft"),
            rim_elevation_ft=data.get("rim_elevation_ft"),
            ground_elevation_ft=data.get("ground_elevation_ft"),
            x_coordinate=data.get("x_coordinate"),
            y_coordinate=data.get("y_coordinate"),
        )
