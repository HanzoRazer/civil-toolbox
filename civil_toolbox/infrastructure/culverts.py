"""Culvert infrastructure model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.infrastructure.base import InfrastructureElementBase, ElementType
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError
from civil_toolbox.infrastructure.validation import (
    validate_positive,
    validate_mannings_n,
    validate_slope,
    validate_pipe_shape,
)


@dataclass
class Culvert(InfrastructureElementBase):
    """A culvert element for conveying water under roads/embankments.

    Similar to pipes but includes additional properties for inlet/outlet
    conditions and headwater analysis.
    """

    element_type: ElementType = field(default=ElementType.CULVERT, init=False)

    shape: str = "circular"
    diameter_in: float | None = None
    width_in: float | None = None
    height_in: float | None = None
    length_ft: float = 0.0
    slope_ft_per_ft: float = 0.0
    mannings_n: float = 0.024
    material: str | None = None

    inlet_type: str = "projecting"
    inlet_coefficient: float | None = None
    outlet_type: str = "projecting"

    upstream_node_id: str | None = None
    downstream_node_id: str | None = None
    upstream_invert_ft: float | None = None
    downstream_invert_ft: float | None = None

    embankment_height_ft: float | None = None
    allowable_headwater_ft: float | None = None

    def __post_init__(self) -> None:
        self.shape = validate_pipe_shape(self.shape)

        if self.length_ft <= 0:
            raise InvalidInfrastructureError("length_ft must be positive")
        validate_positive(self.length_ft, "length_ft")
        validate_slope(self.slope_ft_per_ft)
        validate_mannings_n(self.mannings_n)

        if self.shape == "circular":
            if self.diameter_in is None:
                raise InvalidInfrastructureError(
                    "diameter_in is required for circular culverts"
                )
            validate_positive(self.diameter_in, "diameter_in")
        elif self.shape in ("box", "arch", "elliptical"):
            if self.width_in is None or self.height_in is None:
                raise InvalidInfrastructureError(
                    f"width_in and height_in are required for {self.shape} culverts"
                )
            validate_positive(self.width_in, "width_in")
            validate_positive(self.height_in, "height_in")

        valid_inlet_types = {"projecting", "mitered", "headwall", "wingwall", "beveled"}
        if self.inlet_type not in valid_inlet_types:
            raise InvalidInfrastructureError(
                f"inlet_type must be one of {sorted(valid_inlet_types)}, "
                f"got '{self.inlet_type}'"
            )

        if self.embankment_height_ft is not None:
            validate_positive(self.embankment_height_ft, "embankment_height_ft")
        if self.allowable_headwater_ft is not None:
            validate_positive(self.allowable_headwater_ft, "allowable_headwater_ft")

    @property
    def diameter_ft(self) -> float | None:
        """Diameter in feet."""
        if self.diameter_in is not None:
            return self.diameter_in / 12.0
        return None

    @property
    def rise_ft(self) -> float | None:
        """Rise (height) in feet."""
        if self.height_in is not None:
            return self.height_in / 12.0
        if self.diameter_in is not None:
            return self.diameter_in / 12.0
        return None

    @property
    def span_ft(self) -> float | None:
        """Span (width) in feet."""
        if self.width_in is not None:
            return self.width_in / 12.0
        if self.diameter_in is not None:
            return self.diameter_in / 12.0
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "shape": self.shape,
            "diameter_in": self.diameter_in,
            "width_in": self.width_in,
            "height_in": self.height_in,
            "length_ft": self.length_ft,
            "slope_ft_per_ft": self.slope_ft_per_ft,
            "mannings_n": self.mannings_n,
            "material": self.material,
            "inlet_type": self.inlet_type,
            "inlet_coefficient": self.inlet_coefficient,
            "outlet_type": self.outlet_type,
            "upstream_node_id": self.upstream_node_id,
            "downstream_node_id": self.downstream_node_id,
            "upstream_invert_ft": self.upstream_invert_ft,
            "downstream_invert_ft": self.downstream_invert_ft,
            "embankment_height_ft": self.embankment_height_ft,
            "allowable_headwater_ft": self.allowable_headwater_ft,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Culvert:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            shape=data.get("shape", "circular"),
            diameter_in=data.get("diameter_in"),
            width_in=data.get("width_in"),
            height_in=data.get("height_in"),
            length_ft=data["length_ft"],
            slope_ft_per_ft=data.get("slope_ft_per_ft", 0.0),
            mannings_n=data.get("mannings_n", 0.024),
            material=data.get("material"),
            inlet_type=data.get("inlet_type", "projecting"),
            inlet_coefficient=data.get("inlet_coefficient"),
            outlet_type=data.get("outlet_type", "projecting"),
            upstream_node_id=data.get("upstream_node_id"),
            downstream_node_id=data.get("downstream_node_id"),
            upstream_invert_ft=data.get("upstream_invert_ft"),
            downstream_invert_ft=data.get("downstream_invert_ft"),
            embankment_height_ft=data.get("embankment_height_ft"),
            allowable_headwater_ft=data.get("allowable_headwater_ft"),
        )
