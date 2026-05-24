"""Outlet structure infrastructure model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.infrastructure.base import InfrastructureElementBase, ElementType
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError
from civil_toolbox.infrastructure.validation import (
    validate_positive,
    validate_non_negative,
    validate_outlet_type,
)


@dataclass
class OutletStructure(InfrastructureElementBase):
    """An outlet structure for controlling discharge from detention facilities.

    Supports orifices, weirs, risers, culverts, and combined structures.
    """

    element_type: ElementType = field(default=ElementType.OUTLET, init=False)

    outlet_type: str = "orifice"
    invert_elevation_ft: float = 0.0

    orifice_diameter_in: float | None = None
    orifice_coefficient: float = 0.6
    weir_length_ft: float | None = None
    weir_coefficient: float = 3.33
    weir_crest_elevation_ft: float | None = None

    riser_diameter_in: float | None = None
    riser_height_ft: float | None = None

    upstream_node_id: str | None = None
    downstream_node_id: str | None = None

    def __post_init__(self) -> None:
        self.outlet_type = validate_outlet_type(self.outlet_type)

        if self.orifice_diameter_in is not None:
            validate_positive(self.orifice_diameter_in, "orifice_diameter_in")
        if self.orifice_coefficient is not None:
            if self.orifice_coefficient <= 0 or self.orifice_coefficient > 1:
                raise InvalidInfrastructureError(
                    f"orifice_coefficient must be between 0 and 1, "
                    f"got {self.orifice_coefficient}"
                )
        if self.weir_length_ft is not None:
            validate_positive(self.weir_length_ft, "weir_length_ft")
        if self.weir_coefficient is not None:
            validate_positive(self.weir_coefficient, "weir_coefficient")
        if self.riser_diameter_in is not None:
            validate_positive(self.riser_diameter_in, "riser_diameter_in")
        if self.riser_height_ft is not None:
            validate_positive(self.riser_height_ft, "riser_height_ft")

    @property
    def orifice_area_sqft(self) -> float | None:
        """Calculate orifice area in square feet."""
        if self.orifice_diameter_in is not None:
            import math
            diameter_ft = self.orifice_diameter_in / 12.0
            return math.pi * (diameter_ft / 2.0) ** 2
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "outlet_type": self.outlet_type,
            "invert_elevation_ft": self.invert_elevation_ft,
            "orifice_diameter_in": self.orifice_diameter_in,
            "orifice_coefficient": self.orifice_coefficient,
            "weir_length_ft": self.weir_length_ft,
            "weir_coefficient": self.weir_coefficient,
            "weir_crest_elevation_ft": self.weir_crest_elevation_ft,
            "riser_diameter_in": self.riser_diameter_in,
            "riser_height_ft": self.riser_height_ft,
            "upstream_node_id": self.upstream_node_id,
            "downstream_node_id": self.downstream_node_id,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OutletStructure:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            outlet_type=data.get("outlet_type", "orifice"),
            invert_elevation_ft=data.get("invert_elevation_ft", 0.0),
            orifice_diameter_in=data.get("orifice_diameter_in"),
            orifice_coefficient=data.get("orifice_coefficient", 0.6),
            weir_length_ft=data.get("weir_length_ft"),
            weir_coefficient=data.get("weir_coefficient", 3.33),
            weir_crest_elevation_ft=data.get("weir_crest_elevation_ft"),
            riser_diameter_in=data.get("riser_diameter_in"),
            riser_height_ft=data.get("riser_height_ft"),
            upstream_node_id=data.get("upstream_node_id"),
            downstream_node_id=data.get("downstream_node_id"),
        )
